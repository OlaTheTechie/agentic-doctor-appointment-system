import React from 'react';
import { motion } from 'framer-motion';

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  className?: string;
}

const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange, className = '' }) => {
  const tabs = [
    {
      id: 'book',
      label: 'Book Appointment',
      icon: '📅',
      description: 'Schedule a new appointment'
    },
    {
      id: 'availability',
      label: 'Check Availability',
      icon: '🕐',
      description: 'View doctor schedules'
    },
    {
      id: 'cancel-reschedule',
      label: 'Cancel / Reschedule',
      icon: '⚙️',
      description: 'Modify existing appointments'
    },
    {
      id: 'general',
      label: 'General Query',
      icon: '💬',
      description: 'Ask questions'
    }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.5 }}
      className={`bg-white rounded-xl border border-gray-200 shadow-sm p-4 ${className}`}
    >
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center space-x-3 mb-2">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white text-lg">🏥</span>
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-800">Appointment System</h2>
            <p className="text-sm text-gray-600">Multi-Agent Assistant</p>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <nav className="space-y-2">
        {tabs.map((tab) => (
          <motion.button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className={`w-full text-left p-3 rounded-lg transition-all duration-200 ${
              activeTab === tab.id
                ? 'bg-blue-50 border border-blue-200 text-blue-700'
                : 'hover:bg-gray-50 text-gray-700 hover:text-gray-900'
            }`}
          >
            <div className="flex items-center space-x-3">
              <span className={`text-lg ${
                activeTab === tab.id ? 'text-blue-500' : 'text-gray-400'
              }`}>
                {tab.icon}
              </span>
              <div>
                <div className="font-medium text-sm">{tab.label}</div>
                <div className={`text-xs ${
                  activeTab === tab.id ? 'text-blue-600' : 'text-gray-500'
                }`}>
                  {tab.description}
                </div>
              </div>
            </div>
          </motion.button>
        ))}
      </nav>

      {/* Footer */}
      <div className="mt-8 pt-4 border-t border-gray-200">
        <div className="flex items-center space-x-2 text-xs text-gray-500">
          <div className="w-2 h-2 bg-green-400 rounded-full"></div>
          <span>System Online</span>
        </div>
      </div>
    </motion.div>
  );
};

export default Sidebar;
