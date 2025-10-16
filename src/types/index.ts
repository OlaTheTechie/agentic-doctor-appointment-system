export interface UserMessage {
  role: 'user' | 'ai' | 'system';
  content: string;
}

export interface AppointmentDetails {
  patient_name?: string;
  doctor_name?: string;
  specialisation?: string;
  date?: string;
  time?: string;
  appointment_id?: string;
}

export interface UserQuery {
  id_number: number;
  messages: UserMessage[];
  intent?: 'info_request' | 'book_appointment' | 'cancel_appointment' | 'reschedule_appointment';
  details?: AppointmentDetails;
  next?: string;
  query?: string;
  current_reasoning?: string;
  step_count?: number;
}

export interface BackendResponse {
  id_number: number;
  intent?: string;
  details?: AppointmentDetails;
  messages: UserMessage[];
  next?: string;
  current_reasoning?: string;
}

export interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'date' | 'time' | 'select' | 'textarea' | 'number';
  required?: boolean;
  placeholder?: string;
  options?: { value: string; label: string }[];
}

export interface AppointmentFormData {
  id_number: number;
  doctor_name: string;
  specialisation: string;
  date: string;
  time: string;
}

export interface AvailabilityFormData {
  doctor_name: string;
  specialisation: string;
  date: string;
}

export interface CancelRescheduleFormData {
  id_number: number;
  doctor_name: string;
  old_date: string;
  new_date?: string;
  action: 'cancel' | 'reschedule';
}

export interface GeneralQueryFormData {
  query: string;
}
