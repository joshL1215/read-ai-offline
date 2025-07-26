import asyncio
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from faster_whisper import WhisperModel
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import ollama
import io
import time
import uvicorn

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
executor = ThreadPoolExecutor()

async def transcribe_async(audio_chunk):
    loop = asyncio.get_running_loop()

    return await loop.run_in_executor(executor, model.transcribe, audio_chunk, "en")


@app.get("/ping")
async def ping():
    return {"message": "pong"}

@app.post("/transcribe")
async def transcribe():

    return transcribed_text

@app.post("/inferences/passage-generation")
async def generate_passage(prompt : str):
    currentText = []
    for chunk in ollama.generate(model='gemma3n:e2b', prompt=f"Write a story about: {prompt}", stream=True): 
        currentText.append(chunk['response'])

    return currentText.strip(" ")



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
