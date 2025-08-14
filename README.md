# arabic-english-transcriber

A web app built using a FastAPI backend and React frontend. This app transcribes Arabic or English audio in real time, translates it into the other language, and converts the translation text to speech. All processing is done locally on the server using on-device models -- Whisper for transcription, OPUS-MT for translation, and Piper for text-to-speech.

Live Demo: https://arabic-english-transcriber.web.app/
(Frontend deployed with Firebase, backend deployed on Google Cloud Run.)

INSERT VIDEO

**The setup below is designed for testing purposes only.**

## Backend setup

1. To run the server, first get a copy of the `backend/` directory. Within the `settings.py` file you can adjust various settings such as the size of the Whisper model, or whether to use CUDA or CPU.

2. Within your `backend/` directory install the dependencies located in the `requirements.txt` file. For example:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Run the server on port 8080.

```bash
uvicorn main:app --port 8080 
```

## Frontend Setup

Before you begin, ensure you have npm installed.

1. To run the React frontend, first get a copy of the `frontend/` directory.

2. Within your `frontend/` directory run the following:

```bash
npm install
npm run dev
```

Navigate to `http://localhost:5173/` from your browser to access the frontend.

## Additional Notes

Due to the nature of the transcription model, occasional hallucinations and transcription inaccuracies may occur.

Real-time transcription performance depends on your hardware and the Whisper model size. CPU-only setups may experience lag.
