FROM python:3.10-slim-bookworm

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    # ffmpeg \
    # libavdevice-dev \
    # libavfilter-dev \
    # libavformat-dev \
    # libavcodec-dev \
    # libswscale-dev \
    # libavutil-dev \
    # libswresample-dev \
    # pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]