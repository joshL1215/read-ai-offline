from sqlite3 import connect


def create_tables():
    with connect() as conn:
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transcriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS segments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transcription_id INTEGER,
            start REAL,
            end REAL,
            text TEXT,
            FOREIGN KEY (transcription_id) REFERENCES transcriptions(id) ON DELETE CASCADE
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS silences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transcription_id INTEGER,
            phrase1 TEXT,
            phrase2 TEXT,
            duration REAL,
            FOREIGN KEY (transcription_id) REFERENCES transcriptions(id) ON DELETE CASCADE
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS pace_graph (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transcription_id INTEGER,
            time REAL,
            wpm REAL,
            FOREIGN KEY (transcription_id) REFERENCES transcriptions(id) ON DELETE CASCADE
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS incorrect_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transcription_id INTEGER,
            word TEXT,
            start REAL,
            end REAL,
            FOREIGN KEY (transcription_id) REFERENCES transcriptions(id) ON DELETE CASCADE
        )
        ''')

        conn.commit()


def add_transcription_data(segments, silences, pace, incorrect):
    with connect() as conn:
        cursor = conn.cursor()

        # Insert a new transcription record and get its id
        cursor.execute('INSERT INTO transcriptions DEFAULT VALUES')
        transcription_id = cursor.lastrowid

        for seg in segments:
            cursor.execute(
                'INSERT INTO segments (transcription_id, start, end, text) VALUES (?, ?, ?, ?)',
                (transcription_id, seg["start"], seg["end"], seg["text"])
            )

        for s in silences:
            cursor.execute(
                'INSERT INTO silences (transcription_id, phrase1, phrase2, duration) VALUES (?, ?, ?, ?)',
                (transcription_id, s["phrase1"], s["phrase 2"], s["duration"])
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
    with connect() as conn:
        cursor = conn.cursor()

        # Check if transcription exists
        cursor.execute('SELECT id, created_at FROM transcriptions WHERE id = ?', (transcription_id,))
        transcription = cursor.fetchone()
        if not transcription:
            return None  # or raise exception if you prefer

        # Fetch related segments
        cursor.execute(
            'SELECT start, end, text FROM segments WHERE transcription_id = ? ORDER BY start',
            (transcription_id,)
        )
        segments = [{"start": row[0], "end": row[1], "text": row[2]} for row in cursor.fetchall()]

        # Fetch related silences
        cursor.execute(
            'SELECT phrase1, phrase2, duration FROM silences WHERE transcription_id = ? ORDER BY id',
            (transcription_id,)
        )
        silences = [{"phrase1": row[0], "phrase2": row[1], "duration": row[2]} for row in cursor.fetchall()]

        # Fetch related pace graph
        cursor.execute(
            'SELECT time, wpm FROM pace_graph WHERE transcription_id = ? ORDER BY time',
            (transcription_id,)
        )
        pace = [{"time": row[0], "wpm": row[1]} for row in cursor.fetchall()]

        # Fetch related incorrect words
        cursor.execute(
            'SELECT word, start, end FROM incorrect_words WHERE transcription_id = ? ORDER BY start',
            (transcription_id,)
        )
        incorrect = [{"word": row[0], "start": row[1], "end": row[2]} for row in cursor.fetchall()]

        return {
            "transcription": {
                "id": transcription[0],
                "created_at": transcription[1]
            },
            "segments": segments,
            "silences": silences,
            "pace": pace,
            "incorrect": incorrect
        }
