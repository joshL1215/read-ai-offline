import subprocess
import tempfile
import time
from difflib import Differ
from typing import List, Tuple
import ffmpeg
from faster_whisper import WhisperModel
from fuzzywuzzy import fuzz

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
