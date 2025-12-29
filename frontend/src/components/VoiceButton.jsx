/**
 * VoiceButton Component
 * Push-to-talk voice recording button
 */

import { useState, useEffect } from 'react';
import { useVoiceRecording } from '../hooks/useVoiceRecording';
import api from '../services/api';

export function VoiceButton({ onTranscription, disabled }) {
  const [isTranscribing, setIsTranscribing] = useState(false);
  const { isRecording, audioBlob, error, startRecording, stopRecording, reset } = useVoiceRecording();

  const handleClick = async () => {
    if (disabled || isTranscribing) return;

    if (isRecording) {
      // Stop recording
      stopRecording();
    } else {
      // Start recording
      try {
        await startRecording();
      } catch (err) {
        console.error('Failed to start recording:', err);
      }
    }
  };

  // When audio blob is available, transcribe it
  useEffect(() => {
    const transcribeAudio = async () => {
      if (!audioBlob || isTranscribing) return;

      setIsTranscribing(true);
      try {
        const result = await api.voice.transcribe(audioBlob);
        onTranscription(result.text);
        reset();
      } catch (err) {
        console.error('Transcription failed:', err);
        alert('Voice transcription failed. Please try again or type your message.');
      } finally {
        setIsTranscribing(false);
      }
    };

    if (audioBlob) {
      transcribeAudio();
    }
  }, [audioBlob, isTranscribing, onTranscription, reset]);

  return (
    <button
      onClick={handleClick}
      disabled={disabled || isTranscribing}
      className={`p-4 rounded-full transition-all ${
        isRecording
          ? 'bg-red-600 animate-pulse scale-110'
          : isTranscribing
          ? 'bg-yellow-600'
          : 'bg-blue-600 hover:bg-blue-700'
      } disabled:opacity-50 disabled:cursor-not-allowed`}
      title={isRecording ? 'Click to stop recording' : isTranscribing ? 'Transcribing...' : 'Click to start recording'}
    >
      {isTranscribing ? (
        <svg className="w-6 h-6 text-white animate-spin" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      ) : (
        <svg
          className="w-6 h-6 text-white"
          fill={isRecording ? 'currentColor' : 'none'}
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
          />
        </svg>
      )}

      {error && (
        <div className="absolute top-full mt-2 left-1/2 transform -translate-x-1/2 bg-red-900 text-white text-xs px-3 py-1 rounded whitespace-nowrap">
          {error}
        </div>
      )}
    </button>
  );
}

export default VoiceButton;
