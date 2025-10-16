import React from 'react';
import { motion } from 'framer-motion';
import { Message } from '../types';

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.type === 'user';
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
    >
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? 'bg-blue-500 text-white rounded-br-md'
            : 'bg-white text-gray-800 border border-gray-200 rounded-bl-md shadow-sm'
        }`}
      >
        <div className="flex items-start space-x-2">
          {!isUser && (
            <div className="flex-shrink-0 w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center text-white text-xs font-semibold">
              SYS
            </div>
          )}
          <div className="flex-1">
            <p className="text-sm leading-relaxed whitespace-pre-wrap">
              {message.content}
            </p>
            <p className={`text-xs mt-1 ${
              isUser ? 'text-blue-100' : 'text-gray-500'
            }`}>
              {message.timestamp.toLocaleTimeString()}
            </p>
          </div>
          {isUser && (
            <div className="flex-shrink-0 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center text-white text-xs font-semibold">
              YOU
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default MessageBubble;
