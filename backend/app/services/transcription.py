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


# Global Variables
silenceThrehold = 5 # Flag if silent for more than X seconds
currentText = [] # Stores the current story as an array

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

model = WhisperModel("small", device="cpu", compute_type="float32")

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    '''
    Input: Takes audio file
    Output: Transcription fo the audio file 
    '''

    with tempfile.NamedTemporaryFile(suffix=".webm", delete=True) as webm_temp, \
         tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as wav_temp:

        webm_bytes = await file.read()
        webm_temp.write(webm_bytes)
        webm_temp.flush()  # Ensure data is written to disk
        print(f"Saved webm to temp file: {webm_temp.name}")

        result = subprocess.run([
            "ffmpeg", "-y",
            "-i", webm_temp.name,
            "-ar", "16000",
            "-ac", "1",
            "-f", "wav",
            wav_temp.name
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print("FFmpeg error: ", result.stderr)

        print("Conversion to wav successful.")

        # transcription = await transcribe_async(wav_temp.name)
        segments, info = model.transcribe(wav_temp.name, beam_size=5)
        transcription = " ".join( [segment.text.strip() for segment in segments])
        print("Transcription done:", transcription)

        return {"transcription": transcription}


@app.get("/ping")
async def ping():
    return {"message": "pong"}


@app.post("/inferences/passage-generation")
async def generate_reponse(prompt : str, promptType : str):
    currentText = []
    context = ""
    if promptType == "storyGenerate": context = "Write a story about:"
    elif promptType == "recapGenerate": context = "Give me a Recap of their performance with this data: "

    for chunk in ollama.generate(model='gemma3n:e2b', prompt=f"{promptType} {prompt}", stream=True): 
        currentText.append(chunk['response'])

    return currentText.strip(" ")




def gradeTranscription(transcript, story : str):
    '''
    Input: Transcription (Transcription from User (result), Story = what they were suppose to read (currentText)

    Output: A dicitonary with three components
    silence -> times of all of the times when they pause for more than silence threshold
    pace -> average wpm collected at various times
    incorrect -> incorrect words and time stamps
    '''

    silenceTracker = []
    pacingGraph = []
    incorrectWords = []
    ci = 0 # currentIndex in currentText

    windowSize = 3
    wordWindow = 0
    durationWindow = 0
    
    for i in range(len(transcript)):
        start, end = transcript[i]["start"], transcript[i]["end"]
        seg = transcript[i]["text"].split(" ")
        
        # Check for long silences
        if (i > 0):
            silenceDiff = start - transcript[i-1]["end"]
            if(silenceDiff > silenceThrehold):
                silenceTracker.append({"phrase1": transcript[i-1]["text"] , "phrase 2": transcript[i]["text"], "duration": silenceDiff})
            
            # Pacing Graph (Change in Speech Speed)
            wordWindow += len(seg)
            durationWindow += (silenceDiff + end - start)
            if(i> windowSize - 1): 
                wpm = wordWindow / durationWindow * 60 
                pacingGraph.append({"time": end, "wpm": wpm})
                removed = transcribe[i - windowSize + 1]
                wordWindow -= len(removed["text"].split(" "))
                durationWindow -= (removed["end"] - transcribe[i - windowSize]["end"])

        # Check for correct words (may need to fine-tuning later)
        for word in seg:
            try:
                if (word != currentText[ci]):
                    incorrectWords.append({"word": word, "start": start, "end": end})
                ci += 1
            except:
                pass
    
    return {
        "silence" : silenceTracker,
        "pace" : pacingGraph,
        "incorrect": incorrectWords
    }


async def transcribeAudio(filePath : str):
    segments, info = model.transcribe(filePath, beam_size=5)
    return [{ "start": segment.start, "end": segment.end,"text": segment.text.strip()} for segment in segments]


@app.get("/plot")
async def plot_pace_graph_bytes(pace_data):
    '''
    For plotting (dont worry about this for now)
    '''

    times = [point["time"] for point in pace_data]
    wpm = [point["wpm"] for point in pace_data]

    plt.figure(figsize=(10, 5))
    plt.plot(times, wpm, marker='o', linestyle='-', color='b')
    plt.title("Speech Pace Over Time")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Words Per Minute (WPM)")
    plt.grid(True)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")

# Transcribe from audio file
@app.post("/inferences/analysis")
async def analyzeTranscript(file: UploadFile = File(...)):
    '''
    Takes a audio file. Pushes it into the transcriber gets the result, grades the result, and then saves it into db

    Later take value at pass into inference from this spot. Here you will return the json will all relevant inforamtion!
    '''


    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
        
        result = transcribeAudio(tmp_path)
        analysis = gradeTranscription(result, currentText)

        transcript_id = db.database.add_transcription_data(
            segments=result,
            silences=analysis["silence"],
            pace=analysis["pace"],
            incorrect=analysis["incorrect"]
        )

        # Adjust we return later (may be overkill)
        return JSONResponse(content ={"segments": result,
                                      "silence" : analysis["silence"],
                                      "pace": analysis["pace"],
                                      "incorrect": analysis["incorrect"]
                                      })
    except Exception as e:
        return JSONResponse(content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
