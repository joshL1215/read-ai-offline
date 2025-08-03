from sqlite3 import connect
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

def pingDatabase():
    print("Hello from Database.py")

def add_transcription_data(segments, silences, pace, incorrect, ai_analysis):
    '''
    segments = [{"start": 0.0, "end": 1.2, "text": "Hello world"}]
    silences = [{"phrase1": "Hello", "phrase2": "world", "duration": 0.5}]
    pace = [{"time": 0.0, "wpm": 120}]
    incorrect = [{"word": "Helo", "start": 0.0, "end": 0.5}]
    ai_analysis = "Minor pronunciation error detected in 'Hello'"
    '''
    print("Adding Transcription Data")
    database_path = os.path.join(os.path.dirname(__file__), 'database.db')
    
    with connect(database_path) as conn:
        cursor = conn.cursor()

        cursor.execute(
            'INSERT INTO transcriptions (ai_analysis) VALUES (?)',
            (ai_analysis,)
        )
        transcription_id = cursor.lastrowid

        for seg in segments:
            cursor.execute(
                'INSERT INTO segments (transcription_id, start, end, text) VALUES (?, ?, ?, ?)',
                (transcription_id, seg["start"], seg["end"], seg["text"])
            )

        for s in silences:
            cursor.execute(
                'INSERT INTO silences (transcription_id, phrase1, phrase2, duration) VALUES (?, ?, ?, ?)',
                (transcription_id, s["phrase1"], s["phrase2"], s["duration"])
            )

        for p in pace:
            cursor.execute(
                'INSERT INTO pace_graph (transcription_id, time, wpm) VALUES (?, ?, ?)',
                (transcription_id, p["time"], p["wpm"])
            )

        for w in incorrect:
            cursor.execute(
                'INSERT INTO incorrect_words (transcription_id, word, start, end) VALUES (?, ?, ?, ?)',
                (transcription_id, w["word"], w["start"], w["end"])
            )

        conn.commit()
        return transcription_id  


def get_transcription_by_id(transcription_id):
    print(f"Attemtping to grab data from ID: {transcription_id}")
    database_path = os.path.join(os.path.dirname(__file__), 'database.db')
    
    with connect(database_path) as conn:
        cursor = conn.cursor()

        cursor.execute(
            'SELECT id, created_at, ai_analysis FROM transcriptions WHERE id = ?',
            (transcription_id,)
        )
        transcription = cursor.fetchone()
        if not transcription:
            print("There is no data at (ID: {transcription_id})")
            return None

        cursor.execute(
            'SELECT start, end, text FROM segments WHERE transcription_id = ? ORDER BY start',
            (transcription_id,)
        )
        segments = [{"start": row[0], "end": row[1], "text": row[2]} for row in cursor.fetchall()]

        cursor.execute(
            'SELECT phrase1, phrase2, duration FROM silences WHERE transcription_id = ? ORDER BY id',
            (transcription_id,)
        )
        silences = [{"phrase1": row[0], "phrase2": row[1], "duration": row[2]} for row in cursor.fetchall()]

        cursor.execute(
            'SELECT time, wpm FROM pace_graph WHERE transcription_id = ? ORDER BY time',
            (transcription_id,)
        )
        pace = [{"time": row[0], "wpm": row[1]} for row in cursor.fetchall()]

        cursor.execute(
            'SELECT word, start, end FROM incorrect_words WHERE transcription_id = ? ORDER BY start',
            (transcription_id,)
        )
        incorrect = [{"word": row[0], "start": row[1], "end": row[2]} for row in cursor.fetchall()]

        return {
            "transcription": {
                "id": transcription[0],
                "created_at": transcription[1],
                "ai_analysis": transcription[2]
            },
            "segments": segments,
            "silences": silences,
            "pace": pace,
            "incorrect": incorrect
        }

def get_last_valid_id():
    database_path = os.path.join(os.path.dirname(__file__), 'database.db')
    
    with connect(database_path) as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT MAX(id) FROM transcriptions')
        last_valid_id = cursor.fetchone()[0]

        # If no valid ID is found (i.e., the table is empty), return None
        if last_valid_id is None:
            print("No valid transcription IDs found in the database.")
            return None

        # If we find a valid last ID, return it
        return last_valid_id