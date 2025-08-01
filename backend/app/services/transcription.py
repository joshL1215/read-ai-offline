import subprocess
import tempfile
import time
from difflib import Differ
from typing import List, Tuple
import ffmpeg
from faster_whisper import WhisperModel
from fuzzywuzzy import fuzz

from db.database import create_tables, pingDatabase, add_transcription_data, get_transcription_by_id, get_last_valid_id


gemmaModel = 'gemma3n:e2b'
whisperModel = WhisperModel("base", device="cpu", compute_type="float32")

DICTIONARY_AVAILABLE = False
silence_threshold = 2

async def webm_to_text(webm_bytes):
    '''
    Input: Takes audio file
    Output: Transcription fo the audio file 
    '''

    with tempfile.NamedTemporaryFile(suffix=".webm", delete=True) as webm_temp, \
         tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as wav_temp:

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
        result = whisperModel.transcribe(wav_temp.name, beam_size=5)

        return result

async def normalizeText(text: str) -> str:
    """Normalize text for comparison."""
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)  # Normalize spaces
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    return text

async def load_homophones():
    """Return a dictionary of common homophones."""
    return {
        'to': ['too', 'two'],
        'their': ['there', 'theyre'],
        'write': ['right', 'rite'],
        'your': ['youre'],
    }


async def compare_texts(original: str, transcription: str, similarity_threshold: int = 80) -> List[Tuple[int, str, str, str]]:
    """
    Compare original text and transcription, returning errors as (position, original_word, transcribed_word, error_type).
    Error types: missing, extra, typo, homophone, substitution, gibberish.
    """
    original_words = (await normalizeText(original)).split()
    transcription_words = (await normalizeText(transcription)).split()
    errors = []
    homophones = await load_homophones()
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
