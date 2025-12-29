/**
 * ChatInterface Component
 * Main chat interface that combines all chat components
 */

import { useEffect, useState } from 'react';
import { useConversation } from '../hooks/useConversation';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import ShipCard from './ShipCard';
import EmailCapture from './EmailCapture';

export function ChatInterface() {
  const {
    conversationId,
    messages,
    isLoading,
    error,
    recommendedShips,
    isComplete,
    startConversation,
    sendMessage,
    resetConversation,
  } = useConversation();

  const [showEmailCapture, setShowEmailCapture] = useState(false);
  const [emailSent, setEmailSent] = useState(false);

  // Start conversation on mount
  useEffect(() => {
    startConversation();
  }, [startConversation]);

  // Show email capture when recommendations are available
  useEffect(() => {
    if (recommendedShips.length > 0 && !emailSent) {
      setShowEmailCapture(true);
    }
  }, [recommendedShips, emailSent]);

  const handleSendMessage = async (message) => {
    try {
      await sendMessage(message);
    } catch (err) {
      console.error('Failed to send message:', err);
    }
  };

  const handleNewConversation = () => {
    resetConversation();
    setShowEmailCapture(false);
    setEmailSent(false);
    startConversation();
  };

  const handleEmailSent = (data) => {
    setEmailSent(true);
    console.log('Email sent successfully:', data);
  };

  return (
    <div className="flex flex-col h-screen bg-gray-900">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">StarCiti Sales Agent</h1>
            <p className="text-sm text-gray-400">
              {conversationId ? (
                <>AI Ship Consultant <span className="text-green-400">● Online</span></>
              ) : (
                'Initializing...'
              )}
            </p>
          </div>

          <button
            onClick={handleNewConversation}
            className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors text-sm"
          >
            New Conversation
          </button>
        </div>
      </header>

      {/* Error Display */}
      {error && (
        <div className="bg-red-900 border-l-4 border-red-500 text-red-200 p-4 mx-6 mt-4 rounded">
          <p className="font-bold">Error</p>
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Chat Messages */}
        <div className="flex-1 flex flex-col">
          <MessageList messages={messages} isLoading={isLoading} />

          {/* Chat Input */}
          <ChatInput
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            disabled={!conversationId || isComplete}
          />
        </div>

        {/* Sidebar - Recommended Ships & Email Capture */}
        {(recommendedShips.length > 0 || showEmailCapture) && (
          <aside className="w-96 bg-gray-800 border-l border-gray-700 p-4 overflow-y-auto">
            <h2 className="text-lg font-bold text-white mb-4 flex items-center">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Recommended Ships
            </h2>

            <div className="space-y-4 mb-6">
              {recommendedShips.map((ship, index) => (
                <ShipCard key={index} ship={ship} />
              ))}
            </div>

            {/* Email Capture Form */}
            {showEmailCapture && conversationId && (
              <div className="mt-6">
                <EmailCapture
                  conversationId={conversationId}
                  onEmailSent={handleEmailSent}
                  disabled={isLoading}
                />
              </div>
            )}
          </aside>
        )}
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 border-t border-gray-700 px-6 py-3 text-center text-xs text-gray-500">
        Powered by Claude AI | Star Citizen data from community API
      </footer>
    </div>
  );
}

export default ChatInterface;
