/**
 * Thank You Page Component
 * Displayed after conversation ends, confirms email delivery
 */

import { useLocation, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';

function ThankYouPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [countdown, setCountdown] = useState(10);

  const { userName, userEmail, pdfUrls, error } = location.state || {};

  // Redirect to landing page if no user info
  useEffect(() => {
    if (!userName || !userEmail) {
      navigate('/');
    }
  }, [userName, userEmail, navigate]);

  // Countdown to redirect
  useEffect(() => {
    if (countdown === 0) {
      navigate('/');
      return;
    }

    const timer = setTimeout(() => {
      setCountdown(countdown - 1);
    }, 1000);

    return () => clearTimeout(timer);
  }, [countdown, navigate]);

  if (!userName) {
    return null; // Will redirect in useEffect
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-blue-900 to-gray-900 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        {/* Success Card */}
        <div className="bg-gray-800 border-2 border-green-500 rounded-2xl p-8 shadow-2xl">
          {/* Success Icon */}
          <div className="text-center mb-6">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-green-500 rounded-full mb-4">
              <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <h1 className="text-3xl font-bold text-white mb-2">
              Fleet Guide Sent!
            </h1>
            <p className="text-xl text-gray-300">
              Thanks for chatting with Nova, {userName}!
            </p>
          </div>

          {/* Email Confirmation */}
          {!error ? (
            <div className="bg-gray-700 border border-gray-600 rounded-lg p-6 mb-6">
              <div className="flex items-start space-x-3">
                <svg className="w-6 h-6 text-blue-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-white mb-2">
                    Check Your Inbox
                  </h3>
                  <p className="text-gray-300 mb-2">
                    We've sent your personalized fleet guide to:
                  </p>
                  <p className="text-blue-400 font-semibold text-lg">
                    {userEmail}
                  </p>
                  <p className="text-sm text-gray-400 mt-3">
                    You'll receive two PDF attachments:
                  </p>
                  <ul className="mt-2 space-y-1 text-sm text-gray-300">
                    <li className="flex items-center space-x-2">
                      <svg className="w-4 h-4 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <span>Conversation Transcript - Full record of your chat with Nova</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <svg className="w-4 h-4 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <span>Fleet Composition Guide - Detailed ship specs and recommendations</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-yellow-900 border border-yellow-600 rounded-lg p-6 mb-6">
              <div className="flex items-start space-x-3">
                <svg className="w-6 h-6 text-yellow-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-yellow-200 mb-2">
                    Processing Issue
                  </h3>
                  <p className="text-gray-300 mb-2">
                    We encountered an issue processing your fleet guide:
                  </p>
                  <p className="text-yellow-200 text-sm bg-yellow-950 p-3 rounded mt-2 font-mono">
                    {error}
                  </p>
                  <p className="text-sm text-gray-400 mt-3">
                    Don't worry! Your conversation was saved. We'll send your fleet guide to <span className="text-white font-semibold">{userEmail}</span> shortly.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* What's Next */}
          <div className="border-t border-gray-700 pt-6">
            <h3 className="text-lg font-semibold text-white mb-4">
              What's Next?
            </h3>
            <div className="space-y-3 text-gray-300">
              <div className="flex items-start space-x-3">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                  1
                </span>
                <p>Review your fleet guide and ship recommendations</p>
              </div>
              <div className="flex items-start space-x-3">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                  2
                </span>
                <p>Visit the Star Citizen pledge store to purchase your ships</p>
              </div>
              <div className="flex items-start space-x-3">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
                  3
                </span>
                <p>Start building your fleet in-game and explore the verse!</p>
              </div>
            </div>
          </div>

          {/* Download Links (if available) */}
          {pdfUrls && (pdfUrls.transcript || pdfUrls.fleet_guide) && (
            <div className="mt-6 bg-gray-700 border border-gray-600 rounded-lg p-4">
              <h4 className="text-sm font-semibold text-gray-300 mb-3">
                Download Your PDFs
              </h4>
              <div className="space-y-2">
                {pdfUrls.transcript && (
                  <a
                    href={pdfUrls.transcript}
                    download
                    className="flex items-center justify-between bg-gray-600 hover:bg-gray-500 text-white px-4 py-2 rounded transition-colors"
                  >
                    <span className="text-sm">Conversation Transcript</span>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </a>
                )}
                {pdfUrls.fleet_guide && (
                  <a
                    href={pdfUrls.fleet_guide}
                    download
                    className="flex items-center justify-between bg-gray-600 hover:bg-gray-500 text-white px-4 py-2 rounded transition-colors"
                  >
                    <span className="text-sm">Fleet Composition Guide</span>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </a>
                )}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 mt-6">
            <button
              onClick={() => navigate('/')}
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              <span>Start New Consultation</span>
            </button>
          </div>

          {/* Auto-redirect countdown */}
          <p className="text-center text-sm text-gray-500 mt-4">
            Redirecting to home in {countdown} seconds...
          </p>
        </div>

        {/* Footer */}
        <div className="text-center mt-6">
          <p className="text-gray-400 text-sm">
            Questions? Contact support at{' '}
            <a href="mailto:support@starcitisales.com" className="text-blue-400 hover:text-blue-300">
              support@starcitisales.com
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}

export default ThankYouPage;
