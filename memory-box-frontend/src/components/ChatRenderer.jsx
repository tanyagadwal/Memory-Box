import React from 'react';
import { format } from 'date-fns';
import clsx from 'clsx';

const ChatRenderer = ({ messages }) => {
  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    
    // Handle various time formats
    let time = timestamp;
    try {
      // If it's an ISO string, format it nicely
      if (timestamp.includes('T') && timestamp.includes('Z')) {
        time = format(new Date(timestamp), 'h:mm a');
      }
    } catch (error) {
      // If it's not a valid date, just return as is
      time = timestamp;
    }
    
    return time;
  };

  return (
    <div className="flex flex-col space-y-4 py-4 px-2">
      {messages && messages.map((message, index) => {
        const isUser = message.sender === 'user';
        
        return (
          <div 
            key={index} 
            className={clsx(
              "flex flex-col",
              isUser ? "items-end" : "items-start"
            )}
          >
            {/* Message bubble */}
            <div 
              className={clsx(
                "max-w-[80%] px-4 py-2 rounded-2xl shadow-bubble",
                isUser 
                  ? "bg-primary-500 text-white rounded-tr-none" 
                  : "bg-secondary-100 text-secondary-800 rounded-tl-none"
              )}
            >
              {message.text}
            </div>
            
            {/* Timestamp */}
            {message.timestamp && (
              <span className="text-xs text-secondary-500 mt-1 px-2">
                {formatTime(message.timestamp)}
              </span>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default ChatRenderer; 