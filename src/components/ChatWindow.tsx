import React, { useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import MessageBubble from './MessageBubble';
import { Message } from '../types';

interface ChatWindowProps {
  messages: Message[];
  isLoading?: boolean;
  className?: string;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ 
  messages, 
  isLoading = false, 
  className = '' 
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className={`bg-gray-50 rounded-xl border border-gray-200 overflow-hidden ${className}`}>
      {/* Chat Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-3">
        <h3 className="text-lg font-semibold text-gray-800">Conversation</h3>
        <p className="text-sm text-gray-600">Chat with the appointment system</p>
      </div>

      {/* Messages Container */}
      <div className="h-96 overflow-y-auto p-4 space-y-2">
        <AnimatePresence>
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}
        </AnimatePresence>

        {/* Loading Indicator */}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="flex justify-start mb-4"
          >
            <div className="bg-white text-gray-800 border border-gray-200 rounded-2xl rounded-bl-md shadow-sm px-4 py-3">
              <div className="flex items-center space-x-2">
                <div className="flex-shrink-0 w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center text-white text-xs font-semibold">
                  SYS
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                  <span className="text-sm text-gray-600">System is processing...</span>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Empty State */}
        {messages.length === 0 && !isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex flex-col items-center justify-center h-full text-center py-8"
          >
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
              <span className="text-2xl font-bold text-blue-600">CHAT</span>
            </div>
            <h4 className="text-lg font-medium text-gray-700 mb-2">Start a conversation</h4>
            <p className="text-gray-500 max-w-sm">
              Fill out the form and submit your request to begin chatting with the appointment system.
            </p>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default ChatWindow;
