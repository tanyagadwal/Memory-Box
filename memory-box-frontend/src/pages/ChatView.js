import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
  ArrowLeftIcon,
  PencilIcon,
  TrashIcon,
  TagIcon,
  CalendarIcon,
  ChatBubbleLeftRightIcon
} from '@heroicons/react/24/outline';
import ChatRenderer from '../components/ChatRenderer';

const ChatView = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [chat, setChat] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchChat = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`http://localhost:8000/chats/${id}`);
        setChat(response.data);
        setError(null);
      } catch (err) {
        console.error('Error fetching chat:', err);
        setError('Failed to load chat. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchChat();
  }, [id]);

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this chat? This action cannot be undone.')) {
      try {
        await axios.delete(`http://localhost:8000/chats/${id}`);
        navigate('/');
      } catch (err) {
        console.error('Error deleting chat:', err);
        setError('Failed to delete chat. Please try again.');
      }
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="container mx-auto p-4">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-4">
        <div className="bg-red-50 text-red-700 p-4 rounded-md">
          <p>{error}</p>
          <Link to="/" className="mt-2 inline-block text-red-700 underline">
            Return to all chats
          </Link>
        </div>
      </div>
    );
  }

  if (!chat) {
    return (
      <div className="container mx-auto p-4">
        <div className="bg-secondary-50 p-8 rounded-lg text-center">
          <ChatBubbleLeftRightIcon className="h-12 w-12 text-secondary-400 mx-auto mb-4" />
          <h2 className="text-2xl font-semibold text-secondary-700 mb-2">Chat not found</h2>
          <p className="text-secondary-600 mb-4">
            The chat you're looking for doesn't exist or has been deleted.
          </p>
          <Link to="/" className="btn btn-primary">
            Return to all chats
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <Link to="/" className="flex items-center text-secondary-600 hover:text-primary-600">
            <ArrowLeftIcon className="h-5 w-5 mr-1" />
            <span>Back to all chats</span>
          </Link>
          
          <div className="flex space-x-2">
            <Link
              to={`/edit/${id}`}
              className="btn btn-ghost-primary flex items-center"
            >
              <PencilIcon className="h-4 w-4 mr-1" />
              <span>Edit</span>
            </Link>
            
            <button
              onClick={handleDelete}
              className="btn btn-ghost-danger flex items-center"
            >
              <TrashIcon className="h-4 w-4 mr-1" />
              <span>Delete</span>
            </button>
          </div>
        </div>
        
        <h1 className="text-3xl font-bold text-secondary-800">{chat.title}</h1>
        
        <div className="flex flex-wrap gap-2 mt-2">
          <div className="flex items-center text-sm text-secondary-600">
            <CalendarIcon className="h-4 w-4 mr-1" />
            <span>{formatDate(chat.date)}</span>
          </div>
          
          <div className="flex items-center text-sm text-secondary-600">
            <ChatBubbleLeftRightIcon className="h-4 w-4 mr-1" />
            <span>{chat.messageCount || chat.messages.length} messages</span>
          </div>
          
          <div className="px-2 py-1 text-xs rounded-full bg-primary-50 text-primary-600">
            {chat.category}
          </div>
        </div>
        
        {chat.tags && chat.tags.length > 0 && (
          <div className="flex items-center mt-3">
            <TagIcon className="h-4 w-4 text-secondary-500 mr-2" />
            <div className="flex flex-wrap gap-2">
              {chat.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-2 py-1 text-xs rounded-full bg-secondary-100 text-secondary-700"
                >
                  #{tag}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
      
      {/* Chat Messages */}
      <div className="mt-8 bg-white shadow-sm rounded-lg p-4 md:p-6">
        <ChatRenderer messages={chat.messages} />
      </div>
    </div>
  );
};

export default ChatView; 