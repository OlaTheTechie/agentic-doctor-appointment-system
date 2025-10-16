import axios from 'axios';

// Environment-aware configuration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000';

const chatClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1/chat`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ChatSession {
  session_id: string;
  patient_id: number;
  title: string;
  created_at: string;
  updated_at?: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

export const chatApi = {
  /**
   * Create a new chat session
   */
  async createSession(patientId: number): Promise<ChatSession> {
    try {
      const response = await chatClient.post('/sessions', {
        patient_id: patientId
      });
      return response.data;
    } catch (error) {
      console.error('Failed to create chat session:', error);
      throw error;
    }
  },

  /**
   * Get all sessions for a patient
   */
  async getPatientSessions(patientId: number): Promise<ChatSession[]> {
    try {
      const response = await chatClient.get(`/sessions/${patientId}`);
      return response.data.sessions || [];
    } catch (error) {
      console.error('Failed to get patient sessions:', error);
      return [];
    }
  },

  /**
   * Send a message to a chat session
   */
  async sendMessage(sessionId: string, message: string): Promise<ChatMessage> {
    try {
      const response = await chatClient.post(`/sessions/${sessionId}/messages`, {
        session_id: sessionId,
        message: message,
        role: 'user'
      });
      return response.data;
    } catch (error) {
      console.error('Failed to send message:', error);
      throw error;
    }
  },

  /**
   * Get messages from a chat session
   */
  async getSessionMessages(sessionId: string): Promise<ChatMessage[]> {
    try {
      const response = await chatClient.get(`/sessions/${sessionId}/messages`);
      return response.data.messages || [];
    } catch (error) {
      console.error('Failed to get session messages:', error);
      return [];
    }
  },

  /**
   * Delete a chat session
   */
  async deleteSession(sessionId: string): Promise<void> {
    try {
      await chatClient.delete(`/sessions/${sessionId}`);
    } catch (error) {
      console.error('Failed to delete session:', error);
      throw error;
    }
  },
};

export default chatApi;