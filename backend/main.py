from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydub import AudioSegment
from utils import transcribe_and_translate, save_audio_to_file
from settings import SAMPLE_RATE, DEBUG
import json

WINDOW_DURATION = 3000 # milliseconds

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

    audio_buffer = AudioSegment.empty()

    while True:
        try:
            data = await websocket.receive_bytes()
            audio = AudioSegment(
                data=data,
                sample_width=2,
                frame_rate=SAMPLE_RATE,
                channels=1
            )

            audio_buffer += audio
            current_duration = len(audio_buffer)

            if current_duration > WINDOW_DURATION:
                diff = current_duration - WINDOW_DURATION
                audio_buffer = audio_buffer[diff:]

            transcript, translation = transcribe_and_translate(audio_buffer)
            await websocket.send_text(json.dumps({
                'type': 'interim',
                'transcript': transcript,
                'translation': translation
            }))

        except Exception as e:
            print('WebSocket Error:', e)
            break
