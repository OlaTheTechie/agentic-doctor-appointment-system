import React, { useState } from 'react';
import { motion } from 'framer-motion';
import AppointmentForm from '../components/AppointmentForm';
import ChatWindow from '../components/ChatWindow';
import { FormField, Message } from '../types';
import { appointmentApi } from '../api/agentApi';

const GeneralQuery: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const fields: FormField[] = [
    {
      name: 'query',
      label: 'Your Question',
      type: 'textarea',
      required: true,
      placeholder: 'Ask me anything about appointments, doctors, scheduling, or general healthcare questions...'
    }
  ];

  const handleSubmit = async (data: Record<string, string>) => {
    setIsLoading(true);
    
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: data.query,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await appointmentApi.generalQuery({ 
        query: data.query,
        id_number: 1234567 // Default ID for general queries
      });
      
      // Extract the last assistant message from the response
      const lastMessage = response.messages[response.messages.length - 1];
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: lastMessage?.content || 'Query processed successfully',
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

  const quickQuestions = [
    "What are your operating hours?",
    "How do I prepare for my appointment?",
    "What should I bring to my appointment?",
    "How can I contact my doctor?",
    "What insurance do you accept?",
    "How far in advance should I book?"
  ];

  const handleQuickQuestion = (question: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: question,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    
    // Submit the question
    handleSubmit({ query: question });
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
          <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
            <span className="text-2xl">💬</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-800">General Query</h1>
        </div>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Ask me anything about appointments, doctors, scheduling, or general healthcare questions. I'm here to help!
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Form */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="space-y-6"
        >
          <AppointmentForm
            fields={fields}
            onSubmit={handleSubmit}
            isLoading={isLoading}
            submitLabel="Ask Question"
          />

          {/* Quick Questions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white rounded-xl border border-gray-200 shadow-sm p-6"
          >
            <div className="flex items-center space-x-2 mb-4">
              <span className="text-lg">❓</span>
              <h3 className="font-semibold text-gray-800">Quick Questions</h3>
            </div>
            <p className="text-sm text-gray-600 mb-4">Click on any question below to ask it:</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {quickQuestions.map((question, index) => (
                <motion.button
                  key={index}
                  onClick={() => handleQuickQuestion(question)}
                  disabled={isLoading}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="text-left p-3 text-sm bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {question}
                </motion.button>
              ))}
            </div>
          </motion.div>
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

export default GeneralQuery;
