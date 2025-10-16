import React from 'react';
import { motion } from 'framer-motion';
import { Activity, WifiOff } from 'lucide-react';

interface StatusIndicatorProps {
  isOnline: boolean;
  backendUrl?: string;
  className?: string;
}

const StatusIndicator: React.FC<StatusIndicatorProps> = ({ 
  isOnline, 
  backendUrl,
  className = '' 
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className={`flex items-center space-x-2 ${className}`}
    >
      {isOnline ? (
        <>
          <motion.div
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="relative"
          >
            <div className="w-2 h-2 bg-green-400 rounded-full"></div>
            <div className="absolute inset-0 w-2 h-2 bg-green-400 rounded-full animate-ping opacity-75"></div>
          </motion.div>
          <div className="flex items-center space-x-1 text-green-600">
            <Activity className="w-4 h-4" />
            <span className="text-sm font-medium">Connected</span>
          </div>
          {backendUrl && (
            <span className="text-xs text-gray-500 hidden sm:inline">
              {backendUrl.replace('https://', '').replace('http://', '')}
            </span>
          )}
        </>
      ) : (
        <>
          <div className="w-2 h-2 bg-red-400 rounded-full"></div>
          <div className="flex items-center space-x-1 text-red-600">
            <WifiOff className="w-4 h-4" />
            <span className="text-sm font-medium">Offline</span>
          </div>
        </>
      )}
    </motion.div>
  );
};

export default StatusIndicator;