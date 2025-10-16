import React, { useState } from 'react';
import { motion } from 'framer-motion';
import AppointmentForm from '../components/AppointmentForm';
import ChatWindow from '../components/ChatWindow';
import { FormField, Message } from '../types';
import { appointmentApi } from '../api/agentApi';

const BookAppointment: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const fields: FormField[] = [
    {
      name: 'id_number',
      label: 'Patient ID Number',
      type: 'number',
      required: true,
      placeholder: 'Enter your 7-8 digit ID number'
    },
    {
      name: 'doctor_name',
      label: 'Doctor Name',
      type: 'select',
      required: true,
      options: [
        { value: 'kevin anderson', label: 'Kevin Anderson' },
        { value: 'robert martinez', label: 'Robert Martinez' },
        { value: 'susan davis', label: 'Susan Davis' },
        { value: 'daniel miller', label: 'Daniel Miller' },
        { value: 'sarah wilson', label: 'Sarah Wilson' },
        { value: 'michael green', label: 'Michael Green' },
        { value: 'lisa brown', label: 'Lisa Brown' },
        { value: 'jane smith', label: 'Jane Smith' },
        { value: 'emily johnson', label: 'Emily Johnson' },
        { value: 'john doe', label: 'John Doe' }
      ]
    },
    {
      name: 'specialisation',
      label: 'Specialization',
      type: 'select',
      required: true,
      options: [
        { value: 'general_dentist', label: 'General Dentist' },
        { value: 'cosmetic_dentist', label: 'Cosmetic Dentist' },
        { value: 'prosthodontist', label: 'Prosthodontist' },
        { value: 'pediatric_dentist', label: 'Pediatric Dentist' },
        { value: 'emergency_dentist', label: 'Emergency Dentist' },
        { value: 'oral_surgeon', label: 'Oral Surgeon' },
        { value: 'orthodontist', label: 'Orthodontist' }
      ]
    },
    {
      name: 'date',
      label: 'Preferred Date',
      type: 'date',
      required: true
    },
    {
      name: 'time',
      label: 'Preferred Time',
      type: 'time',
      required: true
    }
  ];

  const handleSubmit = async (data: Record<string, string>) => {
    setIsLoading(true);
    
    // Convert date and time to backend format (DD-MM-YYYY HH:MM)
    const dateStr = data.date;
    const timeStr = data.time;
    const formattedDateTime = `${dateStr.split('-').reverse().join('-')} ${timeStr}`;
    
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: `I want to book an appointment with ${data.doctor_name} (${data.specialisation}) on ${data.date} at ${data.time}`,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await appointmentApi.bookAppointment({
        id_number: parseInt(data.id_number),
        doctor_name: data.doctor_name,
        specialisation: data.specialisation,
        date: formattedDateTime,
        time: timeStr
      });
      
      // Extract the last assistant message from the response
      const lastMessage = response.messages[response.messages.length - 1];
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: lastMessage?.content || 'Appointment processed successfully',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error occurred'}`,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <div className="flex items-center justify-center space-x-3 mb-4">
          <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
            <span className="text-2xl">📅</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-800">Book Appointment</h1>
        </div>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Schedule a new appointment with your preferred doctor. Fill out the form below and our system will help you find the best available time.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Form */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <AppointmentForm
            fields={fields}
            onSubmit={handleSubmit}
            isLoading={isLoading}
            submitLabel="Book Appointment"
          />
        </motion.div>

        {/* Chat */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
        >
          <ChatWindow
            messages={messages}
            isLoading={isLoading}
          />
        </motion.div>
      </div>
    </div>
  );
};

export default BookAppointment;
