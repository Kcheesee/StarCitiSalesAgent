/**
 * API Client for StarCiti Sales Agent Backend
 * Handles all communication with FastAPI server
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Generic fetch wrapper with error handling
 */
async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;

  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}

/**
 * API Methods
 */
export const api = {
  /**
   * Health check
   */
  healthCheck: async () => {
    return fetchAPI('/health');
  },

  /**
   * Get API stats
   */
  getStats: async () => {
    return fetchAPI('/api/stats');
  },

  /**
   * Conversation Methods
   */
  conversations: {
    /**
     * Start a new conversation
     * @returns {Promise<{conversation_id: number, conversation_uuid: string, status: string, started_at: string, message: string}>}
     */
    start: async () => {
      return fetchAPI('/api/conversations/start', {
        method: 'POST',
      });
    },

    /**
     * Send a message in a conversation
     * @param {number} conversationId - Conversation ID
     * @param {string} message - User message
     * @param {boolean} forceRecommendations - Force recommendation phase
     * @returns {Promise<{conversation_id: number, message: string, phase: string, has_recommendations: boolean, is_complete: boolean, recommended_ships: Array}>}
     */
    sendMessage: async (conversationId, message, forceRecommendations = false) => {
      return fetchAPI(`/api/conversations/${conversationId}/message`, {
        method: 'POST',
        body: JSON.stringify({
          message,
          force_recommendations: forceRecommendations,
        }),
      });
    },

    /**
     * Get conversation history
     * @param {number} conversationId - Conversation ID
     * @returns {Promise<{conversation_id: number, transcript: Array, recommended_ships: Array, status: string}>}
     */
    getHistory: async (conversationId) => {
      return fetchAPI(`/api/conversations/${conversationId}`);
    },

    /**
     * Complete conversation and provide email
     * @param {number} conversationId - Conversation ID
     * @param {string} email - User email
     * @returns {Promise<{conversation_id: number, status: string, message: string, recommended_ships: Array}>}
     */
    complete: async (conversationId, email) => {
      return fetchAPI(`/api/conversations/${conversationId}/complete`, {
        method: 'POST',
        body: JSON.stringify({ email }),
      });
    },

    /**
     * Get recommendations for a conversation
     * @param {number} conversationId - Conversation ID
     * @returns {Promise<{conversation_id: number, recommended_ships: Array, has_recommendations: boolean}>}
     */
    getRecommendations: async (conversationId) => {
      return fetchAPI(`/api/conversations/${conversationId}/recommendations`);
    },
  },

  /**
   * Voice Methods
   */
  voice: {
    /**
     * Transcribe audio to text
     * @param {Blob} audioBlob - Audio blob from recording
     * @returns {Promise<{text: string, success: boolean}>}
     */
    transcribe: async (audioBlob) => {
      const formData = new FormData();
      formData.append('audio', audioBlob, 'recording.webm');

      const response = await fetch(`${API_BASE_URL}/api/voice/transcribe`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return await response.json();
    },

    /**
     * Synthesize speech from text
     * @param {string} text - Text to convert to speech
     * @returns {Promise<Blob>} Audio blob (MP3)
     */
    synthesize: async (text) => {
      const response = await fetch(`${API_BASE_URL}/api/voice/synthesize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return await response.blob();
    },
  },
};

export default api;
