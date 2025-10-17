import React, { useState } from 'react';
import { motion } from 'framer-motion';
import AppointmentForm from '../components/AppointmentForm';
import ChatWindow from '../components/ChatWindow';
import { FormField, Message } from '../types';
import { appointmentApi } from '../api/agentApi';

const CancelReschedule: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [action, setAction] = useState<'cancel' | 'reschedule'>('cancel');

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
      name: 'action',
      label: 'Action',
      type: 'select',
      required: true,
      options: [
        { value: 'cancel', label: 'Cancel Appointment' },
        { value: 'reschedule', label: 'Reschedule Appointment' }
      ]
    },
    {
      name: 'old_date',
      label: 'Current Appointment Date',
      type: 'date',
      required: true
    },
    {
      name: 'old_time',
      label: 'Current Appointment Time',
      type: 'time',
      required: true
    },
    ...(action === 'reschedule' ? [
      {
        name: 'new_date',
        label: 'New Date',
        type: 'date',
        required: true
      } as FormField,
      {
        name: 'new_time',
        label: 'New Time',
        type: 'time',
        required: true
      } as FormField
    ] : [])
  ];

  const handleFormChange = (data: Record<string, string>) => {
    if (data.action && data.action !== action) {
      setAction(data.action as 'cancel' | 'reschedule');
    }
  };

  const handleSubmit = async (data: Record<string, string>) => {
    setIsLoading(true);
    
    const selectedAction = data.action as 'cancel' | 'reschedule';
    
    // convert dates to backend format (dd-mm-yyyy hh:mm)
    const oldDateStr = data.old_date;
    const oldTimeStr = data.old_time;
    const formattedOldDateTime = `${oldDateStr.split('-').reverse().join('-')} ${oldTimeStr}`;
    
    let formattedNewDateTime = '';
    if (selectedAction === 'reschedule' && data.new_date && data.new_time) {
      const newDateStr = data.new_date;
      const newTimeStr = data.new_time;
      formattedNewDateTime = `${newDateStr.split('-').reverse().join('-')} ${newTimeStr}`;
    }
    
    // add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: `I want to ${selectedAction} my appointment with ${data.doctor_name} on ${data.old_date} at ${data.old_time}.${selectedAction === 'reschedule' ? ` New date: ${data.new_date} at ${data.new_time}.` : ''}`,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await appointmentApi.cancelReschedule({
        id_number: parseInt(data.id_number),
        doctor_name: data.doctor_name,
        old_date: formattedOldDateTime,
        new_date: selectedAction === 'reschedule' ? formattedNewDateTime : undefined,
        action: selectedAction
      });
      
      // extract the last assistant message from the response
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
          <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center">
            <span className="text-2xl">⚙️</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-800">Cancel / Reschedule</h1>
        </div>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Cancel or reschedule your existing appointment. Our system will help you manage your appointment changes efficiently.
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
            onChange={handleFormChange}
            isLoading={isLoading}
            submitLabel={action === 'cancel' ? 'Cancel Appointment' : 'Reschedule Appointment'}
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

export default CancelReschedule;
