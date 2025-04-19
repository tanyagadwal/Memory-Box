import React from 'react';
import { Link } from 'react-router-dom';
import { CloudArrowUpIcon, MagnifyingGlassIcon, ArchiveBoxIcon } from '@heroicons/react/24/outline';

const Feature = ({ icon, title, description }) => {
  return (
    <div className="flex flex-col items-center text-center p-6 bg-white rounded-lg shadow-sm">
      <div className="p-3 rounded-full bg-primary-50 mb-4">
        {icon}
      </div>
      <h3 className="text-lg font-semibold mb-2 text-secondary-800">{title}</h3>
      <p className="text-secondary-600">{description}</p>
    </div>
  );
};

const Home = () => {
  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="relative py-16 md:py-24 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-lavender-200 to-primary-100 opacity-20"></div>
        <div className="relative container mx-auto px-4 flex flex-col lg:flex-row items-center">
          <div className="lg:w-1/2 mb-10 lg:mb-0">
            <h1 className="text-4xl md:text-5xl font-bold text-secondary-900 mb-6">
              Save Your Precious Conversations
            </h1>
            <p className="text-xl text-secondary-700 mb-8">
              Memory Box lets you upload screenshots of your favorite chat conversations, extract their content, and store them in a beautiful, searchable archive.
            </p>
            <div className="flex flex-col sm:flex-row space-y-4 sm:space-y-0 sm:space-x-4">
              <Link to="/upload" className="btn btn-primary text-center">
                Start Uploading
              </Link>
              <Link to="/chats" className="btn btn-secondary text-center">
                View My Chats
              </Link>
            </div>
          </div>
          <div className="lg:w-1/2 lg:pl-16">
            <div className="bg-white p-2 rounded-xl shadow-lg">
              <div className="bg-secondary-100 rounded-lg p-6 space-y-4">
                <div className="chat-bubble-incoming">
                  Hey! How's your day going?
                </div>
                <div className="chat-bubble-outgoing">
                  Pretty good! Just finished that project I was telling you about.
                </div>
                <div className="chat-bubble-incoming">
                  That's amazing! So proud of you 🎉
                </div>
                <div className="chat-bubble-outgoing">
                  Thanks! Couldn't have done it without your support ❤️
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-12">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12 text-secondary-800">How It Works</h2>
          <div className="grid md:grid-cols-3 gap-8">
            <Feature 
              icon={<CloudArrowUpIcon className="h-8 w-8 text-primary-500" />}
              title="Upload Screenshots"
              description="Drag and drop your chat screenshots in various formats (JPG, PNG, WebP) and organize them with titles and categories."
            />
            <Feature 
              icon={<MagnifyingGlassIcon className="h-8 w-8 text-primary-500" />}
              title="Extract Content"
              description="Our advanced OCR technology extracts text, timestamps, and sender information, maintaining the conversation flow."
            />
            <Feature 
              icon={<ArchiveBoxIcon className="h-8 w-8 text-primary-500" />}
              title="Store & Access"
              description="Browse your memory collection, filter by categories, search for specific conversations, and relive your precious moments."
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-12 bg-gradient-to-r from-primary-500 to-primary-600 rounded-lg text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-6">Ready to Preserve Your Memories?</h2>
          <p className="text-xl mb-8 max-w-2xl mx-auto">
            Don't let your important conversations get lost in the endless scroll of your chat apps.
          </p>
          <Link to="/upload" className="btn bg-white text-primary-600 hover:bg-secondary-100 inline-block">
            Get Started Now
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Home; 