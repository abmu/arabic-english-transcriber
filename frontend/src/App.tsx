import { useEffect, useRef, useState } from 'react';
import RecordRTC, { StereoAudioRecorder } from 'recordrtc';

function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [finalSegments, setFinalSegments] = useState<{ transcript: string; translation: string }[]>([]);
  const [interimSegment, setInterimSegment] = useState<{ transcript: string; translation: string } | null>(null);

  const socketRef = useRef<WebSocket | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const recorderRef = useRef<typeof RecordRTC | null>(null);

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8000/ws/audio');
    socketRef.current = socket;

    socket.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);

        if (msg.type === 'final') {
          setFinalSegments((prev) => [...prev, {
            transcript: msg.transcript,
            translation: msg.translation
          }]);
          setInterimSegment(null);
        } else if (msg.type === 'interim') {
          setInterimSegment({
            transcript: msg.transcript,
            translation: msg.translation
          });
        }
      } catch (e) {
        console.error('Invalid JSON from server:', event.data);
      }
    };

    socket.onerror = (err) => {
      console.error('WebSocket error:', err);
    };

    return () => {
      socket.close();
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const sampleRate = 16000;

      const recorder = new RecordRTC(stream, {
        type: 'audio',
        mimeType: 'audio/wav',
        recorderType: StereoAudioRecorder,
        numberOfAudioChannels: 1,
        desiredSampRate: sampleRate,
        timeSlice: 1000,
        ondataavailable: (blob: Blob) => {
          if (socketRef.current?.readyState === WebSocket.OPEN) {
            blob.arrayBuffer().then((buffer) => {
              socketRef.current?.send(buffer);
            });
          }
        },
      });

      recorder.startRecording();
      recorderRef.current = recorder;
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
    }
  };

  const stopRecording = () => {
    recorderRef.current?.stopRecording();
    recorderRef.current = null;

    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;

    setIsRecording(false);
  }

  return (
    <div>
      <h1>Arabic to English Translator</h1>
      <button onClick={isRecording ? stopRecording : startRecording}>
        {isRecording ? 'Stop Recording' : 'Start Recording'}
      </button>
      <h2>Transcript:</h2>
      <p>
        {[...finalSegments.map(seg => seg.transcript), interimSegment?.transcript]
          .filter(Boolean)
          .join(' ')}
      </p>
      <h2>Translation:</h2>
      <p>
        {[...finalSegments.map(seg => seg.translation), interimSegment?.translation]
          .filter(Boolean)
          .join(' ')}
      </p>
    </div>
  );
}

export default App;