from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydub import AudioSegment
from transcriber import Transcriber
from translator import Translator
from synthesiser import Synthesiser 
from utils import transcribe_and_translate, is_silent, save_audio_to_file
from settings import SUPPORTED_LANGUAGES, SAMPLE_RATE, WEBSOCKET_THRESHOLD, AUDIO_BUFFER_LIMIT, DEBUG, DEVICE
import json
import base64


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket('/ws/audio')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # initialise all of the possible transcribers and translators that may be used
    transcribers = {}
    translators = {}
    synthesisers = {}
    for s, t in SUPPORTED_LANGUAGES:
        if s not in transcribers:
            transcribers[s] = Transcriber(source_lang=s, device=DEVICE)
        
        if (s, t) not in translators:
            translators[(s,t)] = Translator(source_lang=s, target_lang=t, device=DEVICE)

        if s not in synthesisers:
            synthesisers[s] = Synthesiser(source_lang=s, device=DEVICE)
    current_source, current_target = SUPPORTED_LANGUAGES[0]

    websocket_buffer = AudioSegment.empty()
    audio_buffer = AudioSegment.empty()
    final_transcripts, final_translations = [], []
    interim_transcript, interim_translation = '', ''

    while True:
        try:
            message = await websocket.receive()

            if 'text' in message:
                try:
                    msg = json.loads(message['text'])
                except json.JSONDecodeError:
                    await websocket.send_text(json.dumps({'error': 'Invalid JSON format'}))
                    continue
                
                msg_type = msg.get('type')
                if msg_type == 'config':
                    # change source and target lang to new config set in frontend
                    source_lang = msg.get('source_lang')
                    target_lang = msg.get('target_lang')

                    if (source_lang, target_lang) not in SUPPORTED_LANGUAGES:
                        await websocket.send_text(json.dumps({'error': 'Error in languages chosen'}))
                        continue

                    current_source = source_lang
                    current_target = target_lang
                elif msg_type == 'start':
                    # clear all previous transcripts and translations
                    final_transcripts, final_translations = [], []
                    interim_transcript, interim_translation = '', ''
                elif msg_type == 'stop':
                    # create and send text to speech of final translation
                    final_transcripts.append(interim_transcript)
                    final_translations.append(interim_translation)
                    full_translation = ' '.join(final_translations).strip()
                    audio_bytes = synthesisers[current_source].synthesise(full_translation)
                    audio_b64 = base64.b64encode(audio_bytes).decode('utf-8')
                    await websocket.send_text(json.dumps({
                        'type': 'tts',
                        'audio': audio_b64
                    }))

            elif 'bytes' in message:
                # create audio segment from user bytes
                data = message['bytes']
                audio_chunk = AudioSegment(
                    data=data,
                    sample_width=2,
                    frame_rate=SAMPLE_RATE,
                    channels=1
                )

                # ensure a certain amount of audio is received from websocket before processing
                websocket_buffer += audio_chunk
                if len(websocket_buffer) < WEBSOCKET_THRESHOLD:
                    continue
                
                # append every non silent audio chunk and translate entire 'interim' audio buffer until silence is received or buffer limit is reached
                # when silence is received or buffer limit is reached, translate the 'final' audio buffer and clear it

                currently_silent = is_silent(websocket_buffer)
                if not currently_silent:
                    audio_buffer += websocket_buffer
                websocket_buffer = AudioSegment.empty()
                
                if len(audio_buffer) == 0:
                    continue
                
                previous_transcript = ' '.join(final_transcripts).strip()
                transcript, translation = transcribe_and_translate(
                    audio_buffer,
                    transcribers[current_source],
                    translators[(current_source, current_target)],
                    previous_transcript=previous_transcript
                )
                
                if currently_silent or len(audio_buffer) > AUDIO_BUFFER_LIMIT:
                    if DEBUG:
                        save_audio_to_file(audio_buffer)
                    message_type = 'final'
                    final_transcripts.append(transcript)
                    final_translations.append(translation)
                    interim_transcript, interim_translation = '', ''
                    audio_buffer = AudioSegment.empty() # reset audio buffer when final transcript is sent
                else:
                    message_type = 'interim'
                    interim_transcript, interim_translation = transcript, translation

                await websocket.send_text(json.dumps({
                    'type': message_type,
                    'transcript': transcript,
                    'translation': translation
                }))

        except Exception as e:
            print('WebSocket Error:', e)
            break
