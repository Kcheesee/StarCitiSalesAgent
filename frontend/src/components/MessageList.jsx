/**
 * MessageList Component
 * Displays conversation messages with auto-scroll and TTS
 */

import { useEffect, useRef, useState } from 'react';
import { useAudioPlayback } from '../hooks/useAudioPlayback';

export function MessageList({ messages, isLoading }) {
  const messagesEndRef = useRef(null);
  const { speak, isPlaying, isSynthesizing } = useAudioPlayback();
  const lastMessageRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Auto-play TTS for new assistant messages
  useEffect(() => {
    if (messages.length === 0) return;

    const lastMessage = messages[messages.length - 1];

    // Only play if it's a new assistant message
    if (
      lastMessage.role === 'assistant' &&
      lastMessage !== lastMessageRef.current &&
      !isPlaying &&
      !isSynthesizing
    ) {
      lastMessageRef.current = lastMessage;
      speak(lastMessage.content);
    }
  }, [messages, speak, isPlaying, isSynthesizing]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.length === 0 ? (
        <div className="text-center text-gray-400 mt-8">
          <p className="text-xl mb-2">Welcome to StarCiti Sales Agent</p>
          <p className="text-sm">Your AI ship consultant is ready to help you find the perfect ship</p>
        </div>
      ) : (
        messages.map((message, index) => (
          <Message
            key={index}
            message={message}
            isCurrentlyPlaying={isPlaying && message === lastMessageRef.current}
          />
        ))
      )}

      {isLoading && (
        <div className="flex items-start space-x-3">
          <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white text-sm font-bold">
            N
          </div>
          <div className="flex-1 bg-gray-800 rounded-lg p-4">
            <div className="flex space-x-2">
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}

function Message({ message, isCurrentlyPlaying }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex items-start space-x-3 ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold ${
        isUser ? 'bg-green-500' : 'bg-blue-500'
      }`}>
        {isUser ? 'U' : 'N'}
      </div>

      <div className={`flex-1 max-w-3xl ${isUser ? 'text-right' : ''}`}>
        <div className={`inline-block rounded-lg p-4 ${
          isUser
            ? 'bg-green-600 text-white'
            : 'bg-gray-800 text-gray-100'
        }`}>
          <div className="flex items-start space-x-2">
            <p className="flex-1 whitespace-pre-wrap">{message.content}</p>

            {!isUser && isCurrentlyPlaying && (
              <div className="flex items-center space-x-1 text-blue-400 animate-pulse">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M18 3a1 1 0 00-1.196-.98l-10 2A1 1 0 006 5v9.114A4.369 4.369 0 005 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V7.82l8-1.6v5.894A4.37 4.37 0 0015 12c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V3z" />
                </svg>
              </div>
            )}
          </div>
        </div>

        {message.timestamp && (
          <p className="text-xs text-gray-500 mt-1 px-2">
            {new Date(message.timestamp).toLocaleTimeString()}
          </p>
        )}
      </div>
    </div>
  );
}

export default MessageList;
