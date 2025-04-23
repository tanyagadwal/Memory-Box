import React from 'react';
import { Link } from 'react-router-dom';
import { ChatBubbleLeftRightIcon } from '@heroicons/react/24/outline';

const NotFound = () => {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <ChatBubbleLeftRightIcon className="h-16 w-16 text-secondary-400 mb-6" />
      <h1 className="text-3xl font-bold text-secondary-800 mb-4">
        404 - Page Not Found
      </h1>
      <p className="text-secondary-600 max-w-md mb-8">
        The page you're looking for doesn't exist or has been moved.
      </p>
      <Link to="/" className="btn btn-primary">
        Return to Home
      </Link>
    </div>
  );
};

export default NotFound; 