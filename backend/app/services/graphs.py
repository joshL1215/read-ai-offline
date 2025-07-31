import numpy as np
import matplotlib.pyplot as plt
from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:3000"] for React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
import io
import os
app = FastAPI()
db_path = os.path.join(os.path.dirname(__file__), '..', 'db', 'database.db')
from app.db.database import get_transcription_by_id, get_last_valid_id

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
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return buf

@app.get("/pace-graph")
async def get_pace_graph():
    transcription_id = get_last_valid_id()
    if not transcription_id:
        return JSONResponse(status_code=404, content={"error": "No valid transcription found."})
    data = get_transcription_by_id(transcription_id)
    if not data or "pace" not in data:
        return {"error"}
    pace = data["pace"]
    img_stream = plot_pace_graph(pace)
    return StreamingResponse(img_stream, media_type="image/png")

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
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)
    return buffer
    
@app.get("/silences-graph")
async def get_silences_graph():
    transcription_id = get_last_valid_id()
    if not transcription_id:
        return JSONResponse(status_code=404, content={"error": "No valid transcription found."})  
    data = get_transcription_by_id(transcription_id)
    if not data or "silences" not in data:
        return {"error"}
    silences = data["silences"]
    img_stream = plot_silences(silences)
    return StreamingResponse(img_stream, media_type = "image/png")