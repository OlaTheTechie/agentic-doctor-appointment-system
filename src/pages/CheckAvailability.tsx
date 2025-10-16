import React, { useState } from 'react';
import { motion } from 'framer-motion';
import AppointmentForm from '../components/AppointmentForm';
import ChatWindow from '../components/ChatWindow';
import { FormField, Message } from '../types';
import { appointmentApi } from '../api/agentApi';

const CheckAvailability: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const fields: FormField[] = [
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
      label: 'Check Date',
      type: 'date',
      required: true
    }
  ];

  const handleSubmit = async (data: Record<string, string>) => {
    setIsLoading(true);
    
    // Convert date to backend format (DD-MM-YYYY)
    const dateStr = data.date;
    const formattedDate = dateStr.split('-').reverse().join('-');
    
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: `Can you check if ${data.doctor_name} (${data.specialisation}) is available on ${data.date}?`,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await appointmentApi.checkAvailability({
        doctor_name: data.doctor_name,
        specialisation: data.specialisation,
        date: formattedDate
      });
      
      // Extract the last assistant message from the response
      const lastMessage = response.messages[response.messages.length - 1];
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: lastMessage?.content || 'Availability checked successfully',
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
            <span className="text-2xl">🕐</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-800">Check Availability</h1>
        </div>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Check doctor availability for your preferred date. Our system will help you find the best scheduling options.
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
            submitLabel="Check Availability"
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

export default CheckAvailability;
