from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydub import AudioSegment
from utils import transcribe_and_translate, is_silent, save_audio_to_file
from settings import SAMPLE_RATE, WEBSOCKET_THRESHOLD, AUDIO_BUFFER_LIMIT, DEBUG
import json


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

    websocket_buffer = AudioSegment.empty()
    audio_buffer = AudioSegment.empty()
    previous_transcript = ''

    while True:
        try:
            data = await websocket.receive_bytes()
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
            
            print(len(audio_buffer))
            if len(audio_buffer) == 0:
                continue
                
            transcript, translation = transcribe_and_translate(audio_buffer, previous_transcript=previous_transcript)
            
            if currently_silent or len(audio_buffer) > AUDIO_BUFFER_LIMIT:
                if DEBUG:
                    save_audio_to_file(audio_buffer)
                message_type = 'final'
                previous_transcript = transcript
                audio_buffer = AudioSegment.empty() # reset after final transcript is sent
            else:
                message_type = 'interim'

            await websocket.send_text(json.dumps({
                'type': message_type,
                'transcript': transcript,
                'translation': translation
            }))


        except Exception as e:
            print('WebSocket Error:', e)
            break
