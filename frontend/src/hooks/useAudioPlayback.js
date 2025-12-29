/**
 * useAudioPlayback Hook
 * Handles audio playback for TTS responses
 */

import { useState, useRef, useCallback, useEffect } from 'react';
import api from '../services/api';

export function useAudioPlayback() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isSynthesizing, setIsSynthesizing] = useState(false);
  const [error, setError] = useState(null);

  const audioRef = useRef(null);
  const audioQueueRef = useRef([]);

  /**
   * Synthesize and play text
   */
  const speak = useCallback(async (text) => {
    if (!text || text.trim().length === 0) return;

    try {
      setError(null);
      setIsSynthesizing(true);

      // Synthesize speech
      const audioBlob = await api.voice.synthesize(text);

      // Create audio URL
      const audioUrl = URL.createObjectURL(audioBlob);

      // Create and play audio
      const audio = new Audio(audioUrl);
      audioRef.current = audio;

      // Preload audio for faster playback
      audio.preload = 'auto';

      audio.onplay = () => {
        setIsPlaying(true);
        setIsSynthesizing(false);
      };
      audio.onended = () => {
        setIsPlaying(false);
        URL.revokeObjectURL(audioUrl);
        audioRef.current = null;
      };
      audio.onerror = (e) => {
        setError('Audio playback failed');
        setIsPlaying(false);
        setIsSynthesizing(false);
        URL.revokeObjectURL(audioUrl);
      };

      // Start playing as soon as possible
      audio.play().catch(err => {
        console.error('Playback error:', err);
        setError('Audio playback failed');
        setIsSynthesizing(false);
      });

    } catch (err) {
      console.error('TTS Error:', err);
      setError(err.message || 'Speech synthesis failed');
      setIsSynthesizing(false);
    }
  }, []);

  /**
   * Stop current playback
   */
  const stop = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
      setIsPlaying(false);
    }
  }, []);

  /**
   * Pause playback
   */
  const pause = useCallback(() => {
    if (audioRef.current && isPlaying) {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  }, [isPlaying]);

  /**
   * Resume playback
   */
  const resume = useCallback(() => {
    if (audioRef.current && !isPlaying) {
      audioRef.current.play();
      setIsPlaying(true);
    }
  }, [isPlaying]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  return {
    isPlaying,
    isSynthesizing,
    error,
    speak,
    stop,
    pause,
    resume,
  };
}

export default useAudioPlayback;
