/**
 * useConversation Hook
 * Manages conversation state and API interactions
 */

import { useState, useCallback } from 'react';
import api from '../services/api';

export function useConversation() {
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [phase, setPhase] = useState('greeting');
  const [recommendedShips, setRecommendedShips] = useState([]);
  const [isComplete, setIsComplete] = useState(false);

  /**
   * Start a new conversation
   */
  const startConversation = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.conversations.start();
      setConversationId(response.conversation_id);

      // Add welcome message
      setMessages([
        {
          role: 'assistant',
          content: response.message,
          timestamp: new Date().toISOString(),
        },
      ]);

      setPhase('discovery');
      return response;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Send a message
   */
  const sendMessage = useCallback(
    async (message, forceRecommendations = false) => {
      if (!conversationId) {
        throw new Error('No active conversation');
      }

      setIsLoading(true);
      setError(null);

      // Optimistically add user message
      const userMessage = {
        role: 'user',
        content: message,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMessage]);

      try {
        const response = await api.conversations.sendMessage(
          conversationId,
          message,
          forceRecommendations
        );

        // Add assistant response
        const assistantMessage = {
          role: 'assistant',
          content: response.message,
          timestamp: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, assistantMessage]);

        // Update state
        setPhase(response.phase);
        setRecommendedShips(response.recommended_ships || []);
        setIsComplete(response.is_complete);

        return response;
      } catch (err) {
        // Remove optimistic user message on error
        setMessages((prev) => prev.slice(0, -1));
        setError(err.message);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [conversationId]
  );

  /**
   * Complete conversation with email
   */
  const completeConversation = useCallback(
    async (email) => {
      if (!conversationId) {
        throw new Error('No active conversation');
      }

      setIsLoading(true);
      setError(null);

      try {
        const response = await api.conversations.complete(conversationId, email);
        setIsComplete(true);
        return response;
      } catch (err) {
        setError(err.message);
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    [conversationId]
  );

  /**
   * Reset conversation (start fresh)
   */
  const resetConversation = useCallback(() => {
    setConversationId(null);
    setMessages([]);
    setPhase('greeting');
    setRecommendedShips([]);
    setIsComplete(false);
    setError(null);
  }, []);

  return {
    // State
    conversationId,
    messages,
    isLoading,
    error,
    phase,
    recommendedShips,
    isComplete,

    // Actions
    startConversation,
    sendMessage,
    completeConversation,
    resetConversation,
  };
}

export default useConversation;
