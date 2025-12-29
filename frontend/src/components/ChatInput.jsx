/**
 * ChatInput Component
 * Voice-first interface with optional text input
 */

import { useState } from 'react';
import VoiceButton from './VoiceButton';

export function ChatInput({ onSendMessage, isLoading, disabled }) {
  const [message, setMessage] = useState('');
  const [showTextInput, setShowTextInput] = useState(false);

  const handleVoiceTranscription = (text) => {
    // Auto-send voice transcription
    if (text && text.trim()) {
      onSendMessage(text);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (message.trim() && !isLoading) {
      onSendMessage(message);
      setMessage('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="border-t border-gray-700 p-4">
      {/* Voice-First Interface */}
      <div className="flex flex-col items-center space-y-4">
        {/* Large Voice Button */}
        <VoiceButton
          onTranscription={handleVoiceTranscription}
          disabled={disabled || isLoading}
        />

        <p className="text-sm text-gray-400">
          Click the microphone to start recording, click again to stop
        </p>

        {/* Toggle Text Input Button */}
        <button
          type="button"
          onClick={() => setShowTextInput(!showTextInput)}
          className="text-xs text-gray-500 hover:text-gray-300 underline transition-colors"
        >
          {showTextInput ? 'Hide text input' : 'Prefer to type?'}
        </button>
      </div>

      {/* Optional Text Input (collapsed by default) */}
      {showTextInput && (
        <form onSubmit={handleSubmit} className="mt-4">
          <div className="flex space-x-2">
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your message here..."
              disabled={disabled || isLoading}
              className="flex-1 bg-gray-800 text-white border border-gray-700 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              rows={2}
            />

            <button
              type="submit"
              disabled={disabled || isLoading || !message.trim()}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? (
                <span className="flex items-center space-x-2">
                  <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Sending...</span>
                </span>
              ) : (
                'Send'
              )}
            </button>
          </div>

          <p className="text-xs text-gray-500 mt-2">
            Press Enter to send, Shift+Enter for new line
          </p>
        </form>
      )}
    </div>
  );
}

export default ChatInput;
