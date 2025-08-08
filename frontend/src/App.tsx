import React, { useEffect, useRef, useState } from 'react';
import RecordRTC, { StereoAudioRecorder } from 'recordrtc';
import { AUDIO_SETTINGS } from './config';
import { FaMicrophone, FaStop } from 'react-icons/fa';

function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [finalSegments, setFinalSegments] = useState<{ transcript: string; translation: string }[]>([]);
  const [interimSegment, setInterimSegment] = useState<{ transcript: string; translation: string } | null>(null);
  const [sourceLang, setSourceLang] = useState<'ar' | 'en'>('ar');
  const [targetLang, setTargetLang] = useState<'ar' | 'en'>('en');

  const socketRef = useRef<WebSocket | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const recorderRef = useRef<typeof RecordRTC | null>(null);

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8000/ws/audio');
    socketRef.current = socket;

    socket.onopen = () => {
      socket.send(JSON.stringify({
        type: 'config',
        source_lang: sourceLang,
        target_lang: targetLang
      }));
    }

    socket.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        
        if (msg.error) {
          console.error(`Server Error: ${msg.error}`);
        }

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

  const handleLanguageDirectionChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const direction = e.target.value;
    let newSourceLang: 'ar' | 'en', newTargetLang: 'ar' | 'en';

    if (isRecording) {
      stopRecording();
    }

    if (direction === 'ar-en') {
      newSourceLang = 'ar';
      newTargetLang = 'en';
    } else {
      newSourceLang = 'en';
      newTargetLang = 'ar';
    }

    setSourceLang(newSourceLang);
    setTargetLang(newTargetLang);

    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({
        type: 'config',
        source_lang: newSourceLang,
        target_lang: newTargetLang
      }));
    }
  };

  const startRecording = async () => {
    setFinalSegments([]);
    setInterimSegment(null);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const recorder = new RecordRTC(stream, {
        type: 'audio',
        mimeType: 'audio/wav',
        recorderType: StereoAudioRecorder,
        numberOfAudioChannels: 1,
        desiredSampRate: AUDIO_SETTINGS.SAMPLE_RATE,
        timeSlice: AUDIO_SETTINGS.TIME_SLICE,
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
    <div className='flex flex-col items-center gap-5 min-h-screen bg-gray-900 text-white p-6'>
      <h1 className='text-2xl font-bold'>Live Arabic-English Translator</h1>
      <div>
        <label>
          <select onChange={handleLanguageDirectionChange} disabled={isRecording} className='bg-gray-800 text-white border border-gray-700 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50'>
            <option value='ar-en'>Arabic ➝ English</option>
            <option value='en-ar'>English ➝ Arabic</option>
          </select>
        </label>
      </div>
      <button onClick={isRecording ? stopRecording : startRecording}>
        {isRecording ? <FaStop /> : <FaMicrophone />}
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