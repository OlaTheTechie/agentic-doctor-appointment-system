import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Calendar, MessageCircle, Clock, Stethoscope, Sparkles, LucideIcon } from 'lucide-react';
import ChatInterface, { ChatInterfaceRef } from './components/ChatInterface';
import ErrorBoundary from './components/ErrorBoundary';
import { appointmentApi } from './api/agentApi';
import './App.css';

interface QuickActionCardProps {
  icon: LucideIcon;
  title: string;
  description: string;
  color: string;
  onClick: () => void;
}

const QuickActionCard: React.FC<QuickActionCardProps> = ({ icon: Icon, title, description, color, onClick }) => (
  <motion.div
    whileHover={{ y: -2, scale: 1.02 }}
    whileTap={{ scale: 0.98 }}
    onClick={onClick}
    className="bg-white rounded-2xl p-6 shadow-lg border border-gray-100 cursor-pointer group hover:shadow-xl transition-all duration-300"
  >
    <div className={`w-12 h-12 bg-gradient-to-br ${color} rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
      <Icon className="w-6 h-6 text-white" />
    </div>
    <h3 className="font-semibold text-gray-900 mb-2">{title}</h3>
    <p className="text-sm text-gray-600">{description}</p>
    <div className="mt-4 text-xs text-blue-600 opacity-0 group-hover:opacity-100 transition-opacity">
      Click to start →
    </div>
  </motion.div>
);

const App: React.FC = () => {
  const [isOnline, setIsOnline] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const chatRef = useRef<ChatInterfaceRef | null>(null);

  // Test connection
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const online = await appointmentApi.testConnection();
        setIsOnline(online);
      } catch (error) {
        setIsOnline(false);
      } finally {
        setIsLoading(false);
      }
    };
    
    checkConnection();
    const interval = setInterval(checkConnection, 30000);
    return () => clearInterval(interval);
  }, []);

  // Scroll to chat and send message
  const scrollToChat = (message: string) => {
    // Scroll to chat interface
    const chatElement = document.getElementById('chat-interface');
    if (chatElement) {
      chatElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    // Send message to chat
    if (chatRef.current) {
      setTimeout(() => {
        chatRef.current?.sendMessage(message);
      }, 500); // Small delay for smooth scroll
    }
  };

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
        {/* Header */}
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white/80 backdrop-blur-sm border-b border-gray-100 sticky top-0 z-50"
        >
          <div className="max-w-4xl mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <motion.div
                  whileHover={{ rotate: 5 }}
                  className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg"
                >
                  <Stethoscope className="w-5 h-5 text-white" />
                </motion.div>
                <div>
                  <h1 className="text-xl font-semibold text-gray-900">HealthChat</h1>
                  <p className="text-sm text-gray-500">AI Doctor Assistant</p>
                </div>
              </div>
              
              {/* Status */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center space-x-2"
              >
                <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-400' : 'bg-red-400'}`} />
                <span className="text-sm text-gray-600">
                  {isLoading ? 'Connecting...' : isOnline ? 'Online' : 'Offline'}
                </span>
              </motion.div>
            </div>
          </div>
        </motion.header>

        {/* Main Content */}
        <main className="max-w-4xl mx-auto px-6 py-8">
          {/* Welcome Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-center mb-8"
          >
            <motion.div
              animate={{ 
                rotate: [0, 5, -5, 0],
                scale: [1, 1.05, 1]
              }}
              transition={{ 
                duration: 4,
                repeat: Infinity,
                repeatType: "reverse"
              }}
              className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl mb-4 shadow-xl"
            >
              <Sparkles className="w-8 h-8 text-white" />
            </motion.div>
            
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Welcome to HealthChat
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Your intelligent medical assistant powered by advanced AI. 
              Book appointments, check availability, or ask any health-related questions.
            </p>
          </motion.div>

          {/* Quick Actions */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8"
          >
            <QuickActionCard
              icon={Calendar}
              title="Book Appointment"
              description="Schedule with your preferred doctor"
              color="from-blue-500 to-blue-600"
              onClick={() => scrollToChat("I want to book an appointment with a doctor. Can you help me?")}
            />
            <QuickActionCard
              icon={Clock}
              title="Check Availability"
              description="See when doctors are available"
              color="from-green-500 to-green-600"
              onClick={() => scrollToChat("Can you check doctor availability for me?")}
            />
            <QuickActionCard
              icon={MessageCircle}
              title="Ask Questions"
              description="Get instant medical guidance"
              color="from-purple-500 to-purple-600"
              onClick={() => scrollToChat("I have some health questions. Can you help me?")}
            />
          </motion.div>

          {/* Chat Interface */}
          <motion.div
            id="chat-interface"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <ChatInterface ref={chatRef} isOnline={isOnline} />
          </motion.div>
        </main>

        {/* Footer */}
        <motion.footer
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="text-center py-8 text-sm text-gray-500 space-y-2"
        >
          <p>Powered by LangGraph, FastAPI, GROQ • Always consult with healthcare professionals</p>
          <motion.p 
            whileHover={{ scale: 1.05 }}
            className="text-xs text-gray-400 hover:text-blue-500 transition-colors cursor-default"
          >
            Developed with ❤️ by <span className="font-medium text-blue-600">Oladimeji</span>
          </motion.p>
        </motion.footer>
      </div>
    </ErrorBoundary>
  );
};

export default App;