import asyncio
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from faster_whisper import WhisperModel
from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from tempfile import NamedTemporaryFile
import ollama
import tempfile
import io
import time
import uvicorn
import ffmpeg
import tempfile
import asyncio
import uuid 
import os 
import subprocess
import matplotlib.pyplot as plt

import ollama
import whisper
import matplotlib.pyplot as plt
import re
import os 
import string

from difflib import Differ
from fuzzywuzzy import fuzz
from typing import List, Tuple

from database import create_tables, pingDatabase, add_transcription_data, get_transcription_by_id, get_last_valid_id


app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gemmaModel = 'gemma3:4b' # Must Download
whisperModeSize = 'medium'
whisperModel = whisper.load_model("base")
DICTIONARY_AVAILABLE = False
silence_threshold = 2

# app = FastAPI()

def normalizeText(text: str) -> str:
    """Normalize text for comparison."""
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)  # Normalize spaces
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    return text

def load_homophones():
    """Return a dictionary of common homophones."""
    return {
        'to': ['too', 'two'],
        'their': ['there', 'theyre'],
        'write': ['right', 'rite'],
        'your': ['youre'],
    }


def compare_texts(original: str, transcription: str, similarity_threshold: int = 80) -> List[Tuple[int, str, str, str]]:
    """
    Compare original text and transcription, returning errors as (position, original_word, transcribed_word, error_type).
    Error types: missing, extra, typo, homophone, substitution, gibberish.
    """
    original_words = normalizeText(original).split()
    transcription_words = normalizeText(transcription).split()
    errors = []
    homophones = load_homophones()
    differ = Differ()
    differences = list(differ.compare(original_words, transcription_words))
    
    pos = 0
    i = 0
    while i < len(differences):
        diff = differences[i]
        if diff.startswith('  '):  # Matched word
            pos += 1
            i += 1
        elif diff.startswith('- '):  # Word in original
            orig_word = diff[2:]
            if i + 1 < len(differences) and differences[i + 1].startswith('+ '):
                trans_word = differences[i + 1][2:]
                if fuzz.ratio(orig_word, trans_word) > similarity_threshold:
                    errors.append((pos + 1, orig_word, trans_word, f'typo (did you mean "{orig_word}"?)'))
                elif orig_word in homophones and trans_word in homophones[orig_word]:
                    errors.append((pos + 1, orig_word, trans_word, 'homophone'))
                elif DICTIONARY_AVAILABLE and not dictionary.check(trans_word):
                    errors.append((pos + 1, orig_word, trans_word, 'gibberish'))
                else:
                    errors.append((pos + 1, orig_word, trans_word, 'substitution'))
                i += 2
                pos += 1
            else:
                errors.append((pos + 1, orig_word, '', 'missing'))
                pos += 1
                i += 1
        elif diff.startswith('+ '):  # Extra word in transcription
            trans_word = diff[2:]
            errors.append((pos + 1, '', trans_word, 'extra'))
            i += 1
        else:  # Diff marker
            i += 1
    return errors



currentText = "" # Remove Later
def generate(inp : str):
    '''
    Input: (Do not Call directly) Pushes input into Gemma
    Output: return Gemma Repsonse
    '''
    print("Starting Generation")
    tmp = ""
    response = ollama.generate(
        model="gemma3:4b",
        prompt=inp,
        stream=True
    )

    for chunk in response:
        if "response" in chunk:
            print(chunk["response"], end="", flush=True)
            tmp += chunk["response"]
        
        if chunk.get('done', False):
            print("\nGeneration complete.")
            break 

    return tmp


def generateStory(prompt : str):
    '''
    Input: User Prompt from FastAPI
    Output: Returns the story that is generated

    (remove global variable currentText later)
    '''
    currentText = generate(f"In one paragraph, write a story about: {prompt}")
    return currentText
   
def generateResponse(currentText, segments, silences, pace, incorrect):
    '''
    Input: Requires the inforamtion after grading (segment, silence, pace, incorrect)
    Output: Prints a response
    '''
    analysis = ""
    transcription = " ".join([segment["text"] for segment in segments])

    prompt = f"""
    You are a helpful speech assistant. Your job is to provide constructive feedback on the user's speech, suggest improvements, and encourage them to improve based on the following data:
    1. **Text they were responding to:** {currentText}
    2. **Transcription of what they read:** {transcription}
    3. **Moments when they paused for too long (and their duration):** {str(silences)}
    4. **A timeline of their voice pacing over time:** {str(pace)}
    5. **A list of the words they got incorrect:** {str(incorrect)}

    Please:
    - Review the transcription and compare it to the original text. Point out any differences, especially any missed or mispronounced words.
    - Look at the silences. If the user paused for too long, suggest how they could pace their speech better.
    - Based on the pacing data, give advice on whether they are speaking too quickly or too slowly and how to improve.
    - Provide specific recommendations on how the user can improve their pronunciation, pacing, or fluency. Offer encouragement and actionable tips for better performance.

    Give them positive reinforcement and make sure to provide clear suggestions for improving their next speech.
    """
    currentText = generate(prompt)
    return currentText


def calculate_wpm(start_time, end_time, word_count):
    time_diff = end_time - start_time
    if time_diff <= 0:
        return 0
    minutes = time_diff / 60
    return word_count / minutes
    
def analyzeRecording():
    '''
    Input: Audio File (.wav)
    Output: Analysis JSON which includes:
    - Silences: List of silence periods with phrases and duration
    - Pace: WPM over time
    - Errors: Incorrect words with timestamps
    '''
    script_dir = os.path.dirname(os.path.abspath(__file__))
    audioFilePath = os.path.join(script_dir, "audio.wav")
    result = whisperModel.transcribe(audioFilePath, word_timestamps=True)
    segments = result["segments"]

    transcription = " ".join(segment["text"].strip() for segment in result["segments"])
    transcription = "Science is the sistematic pursuit of car the natural world through observation, experimantation, and analysiz. It really helps us understand how things work, from the tiniest atoms to sky, by asking questions and testing ideas. Science drives inovation, improves our daily lives, and challenges us to explore the unknown, constantly expanding what we know about there universe."
    transcription_words = normalizeText(transcription).split()
    
    currentText = "Science is the systematic pursuit of knowledge about the natural world through observation, experimentation, and analysis. It helps us understand how things work, from the tiniest atoms to vast galaxies, by asking questions and testing ideas. Science drives innovation, improves our daily lives, and challenges us to explore the unknown, constantly expanding what we know about the universe."
    current_words = normalizeText(currentText).split()

    silences = []
    pace = []
    errors = []

    total_duration = result["segments"][-1]["end"] if result["segments"] else 0.0

    last_end_time = 0
    for i, segment in enumerate(result["segments"]):
        start_time = segment["start"]
        end_time = segment["end"]
        silence_threshold = 1.0
        if start_time - last_end_time > silence_threshold:
            prev_phrase = result["segments"][i-1]["text"].strip() if i > 0 else ""
            silences.append({
                "phrase1": prev_phrase,
                "phrase2": segment["text"].strip(),
                "duration": start_time - last_end_time
            })
        last_end_time = end_time

    window_size = 4
    word_window = []
    word_timestamps = []
    
    for segment in result["segments"]:
        if "words" in segment:
            for word_info in segment["words"]:
                word = normalizeText(word_info["word"])
                if word:  
                    word_timestamps.append((word, word_info["start"], word_info["end"]))
    
    for word, start, end in word_timestamps:
        word_window.append((word, start, end))
        if len(word_window) > window_size:
            word_window.pop(0)
        if len(word_window) == window_size:
            window_start_time = word_window[0][1]
            window_end_time = word_window[-1][2]
            wpm = calculate_wpm(window_start_time, window_end_time, window_size)
            pace.append({"time": window_end_time, "wpm": wpm})

    total_words = len(transcription_words)
    if total_duration > 0:
        pace.append({"time": total_duration, "wpm": calculate_wpm(0, total_duration, total_words)})

    text_errors = compare_texts(currentText, transcription)
    trans_idx = 0  
    for pos, orig_word, trans_word, error_type in text_errors:
        if error_type == 'missing':
            errors.append({
                "word": orig_word,
                "start": word_timestamps[trans_idx-1][2] if trans_idx > 0 else 0.0,
                "end": word_timestamps[trans_idx-1][2] if trans_idx > 0 else 0.0
            })
        elif error_type == 'extra':
            while trans_idx < len(word_timestamps) and normalizeText(word_timestamps[trans_idx][0]) != trans_word:
                trans_idx += 1
            if trans_idx < len(word_timestamps):
                errors.append({
                    "word": "",
                    "start": word_timestamps[trans_idx][1],
                    "end": word_timestamps[trans_idx][2]
                })
                trans_idx += 1
        else:
            while trans_idx < len(word_timestamps) and normalizeText(word_timestamps[trans_idx][0]) != trans_word:
                trans_idx += 1
            if trans_idx < len(word_timestamps):
                errors.append({
                    "word": orig_word,
                    "start": word_timestamps[trans_idx][1],
                    "end": word_timestamps[trans_idx][2]
                })
                trans_idx += 1

    aiResponse = generateResponse(currentText, segments, silences, pace, errors)
    aiResponse = "testing database"
    add_transcription_data(segments, silences, pace, errors, aiResponse)

    return

def plot_pace_graph(pace):
    '''
    Input: Pace Graph (as saved in the database)
    Output: Picture of a Pace over time (to frontend)
    '''
    times = [entry["time"] for entry in pace]
    wpms = [entry["wpm"] for entry in pace]
    plt.figure(figsize=(10, 6)) 
    plt.plot(times, wpms, marker='o', color='b', linestyle='-', linewidth=2, markersize=8)
    plt.xlabel("Time (seconds)", fontsize=12)
    plt.ylabel("Words Per Minute (WPM)", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    avg_wpm = sum(wpms) / len(wpms)
    plt.axhline(y=avg_wpm, color='r', linestyle='--', label=f"Average WPM: {avg_wpm:.2f}")
    plt.legend(loc='upper right')
    plt.tight_layout() 
    plt.show()
    # add API call


def plot_silences(silences):
    """
    Plot a horizontal bar chart to represent the duration of silences between phrase pairs.
    """
    phrase_pairs = [f"{s['phrase1']} - {s['phrase2']}" for s in silences]
    durations = [s['duration'] for s in silences]
    plt.figure(figsize=(10, 6))
    plt.barh(phrase_pairs, durations, color='skyblue', edgecolor='black')
    plt.title('Silence Durations Between Phrases', fontsize=16)
    plt.xlabel('Duration (seconds)', fontsize=12)
    plt.ylabel('Phrase Pair', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.show()
    # Add API Call


def readingProcess(prompt : str):
    currentText = generateStory(prompt)
    # Wait 


'''
Order of Operations:

Make sure database is made create_tables()
Generate the story with user prompt generateStory(...) save to current text
Push currnetText into analyzeTranscript() -> get all of the data + AI response
At the end of the function it adds to database
'''

# analyzeRecording()
# pingDatabase()
# create_tables()
# add_transcription_data(segments, silences, pace, incorrect, ai_analysis)
# x = get_transcription_by_id(get_last_valid_id())
# currentText = generateStory("Transistors")
# x= analyzeRecording()
# x = generateStory("Transistors")
# print(x)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
