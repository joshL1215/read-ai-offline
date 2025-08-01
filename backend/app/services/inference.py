import ollama 
from db.database import create_tables, pingDatabase, add_transcription_data, get_transcription_by_id, get_last_valid_id

silence_threshold = 2
currentText = ""
gemmaModel = 'gemma3n:e2b'

async def generate(inp : str):
    '''
    Input: (Do not Call directly) Pushes input into Gemma
    Output: return Gemma Repsonse
    '''
    print("Starting Generation")
    tmp = ""
    response = ollama.generate(
        model="gemma3n:e2b",
        prompt=inp,
        stream=True
    )

    for chunk in response:
        if "response" in chunk:
            print(chunk["response"], end="", flush=True)
            tmp += chunk["response"]
        
        if chunk.get('done', False):
            print("\nGeneration complete.")
            break 

    return tmp


async def generateStory(prompt : str):
    '''
    Input: User Prompt from FastAPI
    Output: Returns the story that is generated

    (remove global variable currentText later)
    '''
    currentText = await generate(f"In one paragraph, write a story about: {prompt}")
    return currentText
   
async def generateResponse(currentText, segments, silences, pace, incorrect):
    '''
    Input: Requires the inforamtion after grading (segment, silence, pace, incorrect)
    Output: Prints a response
    '''
    analysis = ""
    transcription = " ".join([segment.text for segment in segments])

    prompt = f"""
    You are a helpful speech assistant. Your job is to provide constructive feedback on the user's speech, suggest improvements, and encourage them to improve based on the following data:
    1. **Text they were responding to:** {currentText}
    2. **Transcription of what they read:** {transcription}
    3. **Moments when they paused for too long (and their duration):** {str(silences)}
    4. **A timeline of their voice pacing over time:** {str(pace)}
    5. **A list of the words they got incorrect:** {str(incorrect)}

    Please:
    - Review the transcription and compare it to the original text. Point out any differences, especially any missed or mispronounced words.
    - Look at the silences. If the user paused for too long, suggest how they could pace their speech better.
    - Based on the pacing data, give advice on whether they are speaking too quickly or too slowly and how to improve.
    - Provide specific recommendations on how the user can improve their pronunciation, pacing, or fluency. Offer encouragement and actionable tips for better performance.

    Give them positive reinforcement and make sure to provide clear suggestions for improving their next speech.
    """
    currentText = await generate(prompt)
    return currentText


async def calculate_wpm(start_time, end_time, word_count):
    time_diff = end_time - start_time
    if time_diff <= 0:
        return 0
    minutes = time_diff / 60
    return word_count / minutes
    
async def analyze_recording(result):
    '''
    Input: Audio File (.wav)
    Output: Analysis JSON which includes:
    - Silences: List of silence periods with phrases and duration
    - Pace: WPM over time
    - Errors: Incorrect words with timestamps
    '''

    segments, info = result

    segments = list(segments)

    print(segments)

    transcription = " ".join(segment.text.strip() for segment in segments)
    transcription_words = (await normalizeText(transcription)).split()
    
    currentText = "Science is the systematic pursuit of knowledge about the natural world through observation, experimentation, and analysis. It helps us understand how things work, from the tiniest atoms to vast galaxies, by asking questions and testing ideas. Science drives innovation, improves our daily lives, and challenges us to explore the unknown, constantly expanding what we know about the universe."
    current_words = (await normalizeText(currentText)).split()

    silences = []
    pace = []
    errors = []

    total_duration = segments[-1].end if segments else 0.0

    last_end_time = 0
    for i, segment in enumerate(segments):
        start_time = segment.start
        end_time = segment.end
        silence_threshold = 1.0
        if start_time - last_end_time > silence_threshold:
            prev_phrase = segments[i-1].text.strip() if i > 0 else ""
            silences.append({
                "phrase1": prev_phrase,
                "phrase2": segment.text.strip(),
                "duration": start_time - last_end_time
            })
        last_end_time = end_time

    window_size = 4
    word_window = []
    word_timestamps = []
    
    for segment in segments:
        if segment.words is not None:
            for word_info in segment.words:
                word = await normalizeText(word_info["word"])
                if word:  
                    word_timestamps.append((word, word_info["start"], word_info["end"]))
    
    for word, start, end in word_timestamps:
        word_window.append((word, start, end))
        if len(word_window) > window_size:
            word_window.pop(0)
        if len(word_window) == window_size:
            window_start_time = word_window[0][1]
            window_end_time = word_window[-1][2]
            wpm = await calculate_wpm(window_start_time, window_end_time, window_size)
            pace.append({"time": window_end_time, "wpm": wpm})

    total_words = len(transcription_words)
    if total_duration > 0:
        pace.append({"time": total_duration, "wpm": await calculate_wpm(0, total_duration, total_words)})

    text_errors = await compare_texts(currentText, transcription)
    trans_idx = 0  
    for pos, orig_word, trans_word, error_type in text_errors:
        if error_type == 'missing':
            errors.append({
                "word": orig_word,
                "start": word_timestamps[trans_idx-1][2] if trans_idx > 0 else 0.0,
                "end": word_timestamps[trans_idx-1][2] if trans_idx > 0 else 0.0
            })
        elif error_type == 'extra':
            while trans_idx < len(word_timestamps) and (await normalizeText(word_timestamps[trans_idx][0])) != trans_word:
                trans_idx += 1
            if trans_idx < len(word_timestamps):
                errors.append({
                    "word": "",
                    "start": word_timestamps[trans_idx][1],
                    "end": word_timestamps[trans_idx][2]
                })
                trans_idx += 1
        else:
            while trans_idx < len(word_timestamps) and (await normalizeText(word_timestamps[trans_idx][0])) != trans_word:
                trans_idx += 1
            if trans_idx < len(word_timestamps):
                errors.append({
                    "word": orig_word,
                    "start": word_timestamps[trans_idx][1],
                    "end": word_timestamps[trans_idx][2]
                })
                trans_idx += 1

    aiResponse = await generateResponse(currentText, segments, silences, pace, errors)
    aiResponse = "testing database"
    # await add_transcription_data(segments, silences, pace, errors, aiResponse) TODO: removed for testing

    return {"segments" : segments, "silences": silences, "pace": pace, "incorrect": errors, "aiResponse" : aiResponse}


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
