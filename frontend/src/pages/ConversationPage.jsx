/**
 * Conversation Page Component
 * Contains the ElevenLabs Conversational AI widget for voice interaction
 */

import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

function ConversationPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [isWidgetLoaded, setIsWidgetLoaded] = useState(false);
  const [conversationEnded, setConversationEnded] = useState(false);

  // Get user info from navigation state
  const { conversationId, userName, userEmail } = location.state || {};

  // Redirect to landing page if no user info
  useEffect(() => {
    if (!conversationId || !userName || !userEmail) {
      navigate('/');
    }
  }, [conversationId, userName, userEmail, navigate]);

  // Load ElevenLabs widget script
  useEffect(() => {
    // Check if script already exists
    if (document.getElementById('elevenlabs-convai')) {
      setIsWidgetLoaded(true);
      return;
    }

    const script = document.createElement('script');
    script.id = 'elevenlabs-convai';
    script.src = 'https://elevenlabs.io/convai-widget/index.js';
    script.async = true;

    script.onload = () => {
      console.log('ElevenLabs widget script loaded');
      setIsWidgetLoaded(true);
    };

    script.onerror = () => {
      console.error('Failed to load ElevenLabs widget script');
    };

    document.body.appendChild(script);

    return () => {
      // Cleanup on unmount
      const existingScript = document.getElementById('elevenlabs-convai');
      if (existingScript) {
        existingScript.remove();
      }
    };
  }, []);

  // Listen for conversation end event
  useEffect(() => {
    const handleConversationEnd = async () => {
      console.log('Conversation ended, generating PDFs...');
      setConversationEnded(true);

      try {
        // Trigger PDF generation and email delivery
        const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

        const response = await fetch(
          `${API_BASE_URL}/api/conversations/${conversationId}/complete`,
          {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              user_email: userEmail,
              user_name: userName,
            }),
          }
        );

        if (!response.ok) {
          throw new Error('Failed to complete conversation');
        }

        const data = await response.json();
        console.log('PDFs generated and email sent:', data);

        // Navigate to thank you page
        navigate('/thank-you', {
          state: {
            userName,
            userEmail,
            pdfUrls: data.pdf_urls || {},
          }
        });

      } catch (error) {
        console.error('Error completing conversation:', error);
        // Still navigate to thank you page even if there's an error
        navigate('/thank-you', {
          state: {
            userName,
            userEmail,
            error: error.message,
          }
        });
      }
    };

    // Listen for custom event from widget (we'll need to implement this based on ElevenLabs docs)
    window.addEventListener('elevenlabs-conversation-ended', handleConversationEnd);

    return () => {
      window.removeEventListener('elevenlabs-conversation-ended', handleConversationEnd);
    };
  }, [conversationId, userName, userEmail, navigate]);

  if (!conversationId) {
    return null; // Will redirect in useEffect
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-blue-900 to-gray-900 flex flex-col">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 py-4 px-6">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-semibold text-white">
                Fleet Consultation with Nova
              </h1>
              <p className="text-sm text-gray-400">
                {userName} • {userEmail}
              </p>
            </div>
          </div>
          {conversationEnded && (
            <div className="flex items-center space-x-2 text-green-400">
              <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span className="text-sm font-medium">Processing...</span>
            </div>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="max-w-4xl w-full">
          {/* Instructions Card */}
          <div className="bg-gray-800 border-2 border-blue-500 rounded-2xl p-8 mb-6">
            <h2 className="text-2xl font-bold text-white mb-4">
              Ready to Build Your Fleet?
            </h2>
            <div className="space-y-3 text-gray-300">
              <p className="flex items-start space-x-2">
                <svg className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Click the microphone button below to start talking with Nova</span>
              </p>
              <p className="flex items-start space-x-2">
                <svg className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Talk naturally about your playstyle, budget, and what you want to do in Star Citizen</span>
              </p>
              <p className="flex items-start space-x-2">
                <svg className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Nova will help you build a fleet of up to 5 ships perfect for your needs</span>
              </p>
              <p className="flex items-start space-x-2">
                <svg className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Your personalized fleet guide will be emailed to you when the conversation ends</span>
              </p>
            </div>
          </div>

          {/* ElevenLabs Widget Container */}
          <div className="flex justify-center">
            {!isWidgetLoaded ? (
              <div className="bg-gray-800 border-2 border-gray-700 rounded-2xl p-12 text-center">
                <svg className="animate-spin h-12 w-12 text-blue-500 mx-auto mb-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <p className="text-gray-400">Loading voice assistant...</p>
              </div>
            ) : (
              <elevenlabs-convai
                agent-id="agent_6401kdgp1fd7fmvax85zb5s0sa3s"
              />
            )}
          </div>

          {/* Conversation Metadata (hidden, for backend tracking) */}
          <div id="conversation-metadata" style={{ display: 'none' }}>
            {JSON.stringify({ conversationId, userName, userEmail })}
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="bg-gray-800 border-t border-gray-700 py-4 px-6">
        <div className="max-w-6xl mx-auto text-center">
          <p className="text-sm text-gray-400">
            Having issues? Refresh the page or contact support
          </p>
        </div>
      </div>
    </div>
  );
}

export default ConversationPage;
