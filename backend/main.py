from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from transcriber import transcribe_and_translate

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
    audio_buffer = b''

    while True:
        try:
            data = await websocket.receive_bytes()
            audio_buffer += data

            try:
                translated_text = transcribe_and_translate(audio_buffer)
                await websocket.send_text(translated_text)
            except Exception as e:
                await websocket.send_text(f'[Error] {str(e)}')
            
            audio_buffer = b'' # reset buffer

        except Exception as e:
            print('WebSocket Error:', e)
            break
