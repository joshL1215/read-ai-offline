import numpy as np
from faster_whisper import WhisperModel
from fastapi import FastAPI, WebSocket, WebSocketDisconnect 
import ollama
import io
import time

# Global Variables
silenceThrehold = 5 # Flag if silent for more than X seconds
currentText = [] # Stores the current story as an array

app = FastAPI()

@app.websocket("/ws/transcribe")
async def transcribe_audio(websocket: WebSocket):
    await websocket.accept() 
    if not currentText: 
        websocket.close()
        return
        
    model_size = "small"
    model = WhisperModel(model_size, device="cpu", compute_type="int8_float16")
    streamer = model.stream()

    timeline = [] # Tables with text, start time, and end time
    lastSpokenTime = None
    currIndex = 0

    try:
        while True:
            data = await websocket.receive_bytes()
            audioChunk = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32678
            result = streamer.feed(audioChunk)
            chunkedText = result.text.strip()

            if chunkedText:
                lastSpokenTime = time.time()
                segment = {"text" : result.text, "start": result.start, "end" : result.end}
                timeline.append(segment)

                # Check if words they say match the original text
                for i in range(len(chunkedText)):
                    if(currentText[currIndex + i] != chunkedText[currIndex]):
                        pass # A word was said wrong
                currIndex += len(chunkedText)

                await websocket.send_text(result.text) # Sends Transcribed text back to frontend
            elif (lastSpokenTime and (time.time() - lastSpokenTime >= silenceThrehold)): # For Stuttering
                await websocket.send_text("Silence Threshold Passed")
          
    except WebSocketDisconnect:
        await websocket.close()


# Use normal GET request
@app.websocket("/ws/response")
async def generate_response(websocket : WebSocket):
    await websocket.accept()
    try:
        response = ollama.generate(model='gemma3n:e2b', prompt="Do something!", stream=True)
        for chunk in response:
            await websocket.send_text(chunk['response'])

    except:
        await websocket.close()


# Assume that the story it generates only happens once as the start (no real-time)
@app.get("/userprompt")
async def generate_prompt(prompt : str):
    currentText = []
    for chunk in ollama.generate(model='gemma3n:e2b', prompt=f"Write about {prompt}", stream=True): 
        currentText.append(chunk['response'])

    return currentText.strip(" ")