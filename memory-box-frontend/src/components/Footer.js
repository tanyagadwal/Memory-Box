import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-white py-6 border-t border-secondary-200">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-4 md:mb-0">
            <p className="text-secondary-600 text-sm">
              © {new Date().getFullYear()} Memory Box - Preserve your conversations
            </p>
          </div>
          <div className="flex space-x-4">
            <a 
              href="#" 
              className="text-secondary-600 hover:text-primary-500 transition-colors duration-200 text-sm"
            >
              Privacy Policy
            </a>
            <a 
              href="#" 
              className="text-secondary-600 hover:text-primary-500 transition-colors duration-200 text-sm"
            >
              Terms of Service
            </a>
            <a 
              href="#" 
              className="text-secondary-600 hover:text-primary-500 transition-colors duration-200 text-sm"
            >
              Contact
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 