from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydub import AudioSegment
from transcriber import transcribe_and_translate, is_silent, SAMPLE_RATE

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

            if is_silent(audio):
                if audio_chunks:
                    full_audio = sum(audio_chunks)
                    try:
                        translated_text = transcribe_and_translate(full_audio)
                        await websocket.send_text(translated_text)
                    except Exception as e:
                        await websocket.send_text(f'[Error] {str(e)}')
                    audio_chunks.clear() # reset after sentence/silence
            else:
                audio_chunks.append(audio)            

        except Exception as e:
            print('WebSocket Error:', e)
            break
