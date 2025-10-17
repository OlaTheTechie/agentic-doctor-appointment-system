import axios, { AxiosResponse } from 'axios';
import { UserQuery, BackendResponse } from '../types';

// environment-aware api configuration (applying lessons learned)
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000';
const API_TIMEOUT = parseInt(process.env.REACT_APP_API_TIMEOUT || '30000');
const ENVIRONMENT = process.env.REACT_APP_ENVIRONMENT || 'development';

console.log(`🔧 API Configuration:`, {
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  environment: ENVIRONMENT
});

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
  // enable credentials for cors if needed
  withCredentials: false,
});

// request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log('Response received:', response.data);
    return response;
  },
  (error) => {
    console.error('Response error:', error);

    if (error.response) {
      // server responded with error status
      const errorMessage = error.response.data?.message || error.response.data?.error || 'Server error occurred';
      throw new Error(errorMessage);
    } else if (error.request) {
      // request was made but no response received
      throw new Error('Unable to connect to the server. Please check your connection.');
    } else {
      // something else happened
      throw new Error('An unexpected error occurred');
    }
  }
);

export const appointmentApi = {
  /**
   * Execute a request to the appointment system
   */
  async execute(query: UserQuery): Promise<BackendResponse> {
    try {
      const response: AxiosResponse<BackendResponse> = await apiClient.post('/execute', query);
      return response.data;
    } catch (error) {
      console.error('API execution error:', error);
      throw error;
    }
  },

  /**
   * Book an appointment
   */
  async bookAppointment(data: {
    id_number: number;
    doctor_name: string;
    specialisation: string;
    date: string;
    time: string;
  }): Promise<BackendResponse> {
    const query: UserQuery = {
      id_number: data.id_number,
      messages: [{
        role: 'user',
        content: `I want to book an appointment with ${data.doctor_name} (${data.specialisation}) on ${data.date} at ${data.time}`
      }],
      intent: 'book_appointment',
      details: {
        patient_name: `Patient ${data.id_number}`,
        doctor_name: data.doctor_name,
        specialisation: data.specialisation,
        date: data.date,
        time: data.time
      }
    };

    return this.execute(query);
  },

  /**
   * Check doctor availability
   */
  async checkAvailability(data: {
    doctor_name: string;
    specialisation: string;
    date: string;
  }): Promise<BackendResponse> {
    const query: UserQuery = {
      id_number: 1234567, // default id for availability checks
      messages: [{
        role: 'user',
        content: `Can you check if ${data.doctor_name} (${data.specialisation}) is available on ${data.date}?`
      }],
      intent: 'info_request',
      details: {
        doctor_name: data.doctor_name,
        specialisation: data.specialisation,
        date: data.date
      }
    };

    return this.execute(query);
  },

  /**
   * Cancel or reschedule an appointment
   */
  async cancelReschedule(data: {
    id_number: number;
    doctor_name: string;
    old_date: string;
    new_date?: string;
    action: 'cancel' | 'reschedule';
  }): Promise<BackendResponse> {
    const intent = data.action === 'cancel' ? 'cancel_appointment' : 'reschedule_appointment';
    const content = data.action === 'cancel'
      ? `I want to cancel my appointment with ${data.doctor_name} on ${data.old_date}`
      : `I want to reschedule my appointment with ${data.doctor_name} from ${data.old_date} to ${data.new_date}`;

    const query: UserQuery = {
      id_number: data.id_number,
      messages: [{
        role: 'user',
        content
      }],
      intent,
      details: {
        doctor_name: data.doctor_name,
        date: data.old_date,
        appointment_id: `${data.id_number}-${data.doctor_name}-${data.old_date}`
      }
    };

    return this.execute(query);
  },

  /**
   * Send a general query
   */
  async generalQuery(data: { query: string; id_number?: number }): Promise<BackendResponse> {
    const query: UserQuery = {
      id_number: data.id_number || 1234567,
      messages: [{
        role: 'user',
        content: data.query
      }],
      intent: 'info_request',
      query: data.query
    };

    return this.execute(query);
  },

  /**
   * Test connection to the backend
   */
  async testConnection(): Promise<boolean> {
    try {
      // use the health endpoint (applying lessons learned)
      const response = await apiClient.get('/health', { timeout: 5000 });
      return response.status === 200;
    } catch (error) {
      console.error('Connection test failed:', error);
      return false;
    }
  },

  /**
   * Get backend status and agent information
   */
  async getStatus(): Promise<any> {
    try {
      const response = await apiClient.get('/agents/status');
      return response.data;
    } catch (error) {
      console.error('Status check failed:', error);
      throw error;
    }
  },
};

export default appointmentApi;
