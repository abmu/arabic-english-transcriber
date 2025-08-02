from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydub import AudioSegment
from transcriber import transcribe_and_translate, is_silent, save_audio_to_file
from settings import SAMPLE_RATE, DEBUG
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

    audio_chunks = []

    while True:
        try:
            data = await websocket.receive_bytes()
            audio = AudioSegment(
                data=data,
                sample_width=2,
                frame_rate=SAMPLE_RATE,
                channels=1
            )

            # Append every non silent audio chunk to array and translate entire 'interim' audio array until silence is received.
            # When silence is received, translate a 'final' time and clear out array to start over.
            if is_silent(audio):
                if audio_chunks:
                    final_audio = sum(audio_chunks)
                    if DEBUG:
                        save_audio_to_file(final_audio)

                    transcript, translation = transcribe_and_translate(final_audio)
                    await websocket.send_text(json.dumps({
                        'type': 'final',
                        'transcript': transcript,
                        'translation': translation
                    }))

                    audio_chunks.clear() # reset after sentence/silence
            else:
                audio_chunks.append(audio)
                interim_audio = sum(audio_chunks)

                transcript, translation = transcribe_and_translate(interim_audio)
                await websocket.send_text(json.dumps({
                    'type': 'interim',
                    'transcript': transcript,
                    'translation': translation
                }))

        except Exception as e:
            print('WebSocket Error:', e)
            break
