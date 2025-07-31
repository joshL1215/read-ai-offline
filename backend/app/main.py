from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from services.transcription import webm_to_text, analyze_recording

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

@app.post("/eval")
async def eval(file: UploadFile = File(...)):
    webm_bytes = await file.read()
    model_output = await webm_to_text(webm_bytes)
    result = await analyze_recording(model_output)

    return result

