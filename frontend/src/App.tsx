import React, { useEffect, useRef, useState } from 'react';

function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [translatedText, setTranslatedText] = useState('');

  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8000/ws/audio');
    socketRef.current = socket;

    socket.onmessage = (event) => {
      setTranslatedText(event.data);
    };

    socket.onerror = (err) => {
      console.error('WebSocket error:', err);
    };

    return () => {
      socket.close();
    };
  }, []);

  const startRecording = async () => {
    setIsRecording(true);
    console.log('Recording Started');
  };

  const stopRecording = () => {
    setIsRecording(false);
    console.log('Recording Stopped');
  }

  return (
    <div>
      <h1>Arabic to English Translator</h1>
      <button onClick={isRecording ? stopRecording : startRecording}>
        {isRecording ? 'Stop Recording' : 'Start Recording'}
      </button>
      <h2>Translation:</h2>
      <p></p>
    </div>
  );
}

export default App;