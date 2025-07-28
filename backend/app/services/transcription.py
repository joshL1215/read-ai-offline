import asyncio
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from faster_whisper import WhisperModel
from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import ollama
import io
import time
import uvicorn
import ffmpeg
import tempfile
import asyncio
import uuid 
import os 

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

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import subprocess
from tempfile import NamedTemporaryFile
from faster_whisper import WhisperModel
from concurrent.futures import ThreadPoolExecutor
import asyncio
import uuid 
import os 

model = WhisperModel("small", device="cpu", compute_type="float32")

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):

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
async def generate_passage(prompt : str):
    currentText = []
    for chunk in ollama.generate(model='gemma3n:e2b', prompt=f"Write a story about: {prompt}", stream=True): 
        currentText.append(chunk['response'])

    return currentText.strip(" ")



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
