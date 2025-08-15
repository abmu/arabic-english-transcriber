SUPPORTED_LANGUAGES = [
    ('en', 'ar'),
    ('ar', 'en'),
]

WHISPER_MODEL_SIZE = 'tiny' # tiny, base, small, medium, large-v1, large-v2, large-v3, or large

DEVICE = 'cpu' # 'cpu' or 'cuda'

SAMPLE_RATE = 16000
RMS_THRESHOLD = 800 # silence level
WEBSOCKET_THRESHOLD = 1000 # milliseconds
AUDIO_BUFFER_LIMIT = 2500 # milliseconds

DEBUG = False
DEBUG_AUDIO_SAVE_DIR = 'audio'
