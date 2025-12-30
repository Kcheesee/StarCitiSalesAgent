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
    script.src = 'https://unpkg.com/@elevenlabs/convai-widget-embed@beta';
    script.async = true;
    script.type = 'text/javascript';

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
        <div className="max-w-2xl w-full">
          {/* Centered Widget Container - Main Focus */}
          <div className="flex flex-col items-center space-y-8">
            {/* Title */}
            <div className="text-center space-y-2">
              <h2 className="text-3xl font-bold text-white">
                Talk to Nova
              </h2>
              <p className="text-gray-400">
                Your AI Ship Consultant is ready to help you build the perfect fleet
              </p>
            </div>

            {/* ElevenLabs Widget - Centered as Primary Focus */}
            {!isWidgetLoaded ? (
              <div className="bg-gray-800 border-2 border-gray-700 rounded-2xl p-16 text-center w-full">
                <svg className="animate-spin h-16 w-16 text-blue-500 mx-auto mb-6" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <p className="text-gray-400 text-lg">Loading voice assistant...</p>
              </div>
            ) : (
              <div className="w-full flex flex-col items-center space-y-6">
                {/* Widget */}
                <elevenlabs-convai
                  agent-id="agent_6401kdgp1fd7fmvax85zb5s0sa3s"
                />

                {/* Finish Button */}
                {!conversationEnded && (
                  <button
                    onClick={() => {
                      // Fire the conversation ended event
                      window.dispatchEvent(new Event('elevenlabs-conversation-ended'));
                    }}
                    className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-bold px-10 py-5 rounded-xl shadow-2xl hover:shadow-blue-500/50 hover:scale-105 transition-all duration-200 flex items-center space-x-3 border-2 border-blue-500"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="text-lg">Finish & Get My Fleet Guide</span>
                  </button>
                )}
              </div>
            )}

            {/* Quick Tips */}
            <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6 w-full">
              <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-4">
                Quick Tips
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm text-gray-300">
                <div className="flex items-center space-x-2">
                  <svg className="w-4 h-4 text-blue-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Mention your budget</span>
                </div>
                <div className="flex items-center space-x-2">
                  <svg className="w-4 h-4 text-blue-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Describe your playstyle</span>
                </div>
                <div className="flex items-center space-x-2">
                  <svg className="w-4 h-4 text-blue-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Talk about crew size</span>
                </div>
                <div className="flex items-center space-x-2">
                  <svg className="w-4 h-4 text-blue-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Ask questions freely</span>
                </div>
              </div>
            </div>
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
