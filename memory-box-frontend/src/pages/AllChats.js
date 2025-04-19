import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { MagnifyingGlassIcon, AdjustmentsHorizontalIcon, ChevronDownIcon } from '@heroicons/react/24/outline';
import { ChatBubbleLeftRightIcon } from '@heroicons/react/24/solid';
import { getAllChats } from '../api/chatService';

const AllChats = () => {
  const [chats, setChats] = useState([]);
  const [filteredChats, setFilteredChats] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [sortBy, setSortBy] = useState('date');
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [isLoading, setIsLoading] = useState(true);
  const [categories, setCategories] = useState(['All']);
  
  // Load chats on component mount
  useEffect(() => {
    const fetchChats = async () => {
      try {
        setIsLoading(true);
        // Fetch chats from API/localStorage
        const chatData = await getAllChats();
        setChats(chatData);
        
        // Extract unique categories
        const uniqueCategories = ['All'];
        chatData.forEach(chat => {
          if (chat.category && !uniqueCategories.includes(chat.category)) {
            uniqueCategories.push(chat.category);
          }
        });
        setCategories(uniqueCategories);
        
        setFilteredChats(chatData);
      } catch (error) {
        console.error('Error fetching chats:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchChats();
  }, []);
  
  // Apply filters and search
  useEffect(() => {
    let result = [...chats];
    
    // Apply category filter
    if (selectedCategory && selectedCategory !== 'All') {
      result = result.filter(chat => chat.category === selectedCategory);
    }
    
    // Apply search term
    if (searchTerm) {
      const lowercasedTerm = searchTerm.toLowerCase();
      result = result.filter(chat => {
        // Search in title
        if (chat.title?.toLowerCase().includes(lowercasedTerm)) {
          return true;
        }
        
        // Search in messages
        if (chat.messages && chat.messages.length > 0) {
          const hasMatchingMessage = chat.messages.some(message => 
            message.content?.toLowerCase().includes(lowercasedTerm)
          );
          if (hasMatchingMessage) {
            return true;
          }
        }
        
        // Search in tags
        if (chat.tags && chat.tags.length > 0) {
          const hasMatchingTag = chat.tags.some(tag => 
            tag.toLowerCase().includes(lowercasedTerm)
          );
          if (hasMatchingTag) {
            return true;
          }
        }
        
        return false;
      });
    }
    
    // Apply sorting
    result.sort((a, b) => {
      switch (sortBy) {
        case 'date':
          return new Date(b.date || 0) - new Date(a.date || 0);
        case 'title':
          return (a.title || '').localeCompare(b.title || '');
        case 'messages':
          return (b.messages?.length || 0) - (a.messages?.length || 0);
        default:
          return 0;
      }
    });
    
    setFilteredChats(result);
  }, [chats, searchTerm, selectedCategory, sortBy]);
  
  // Format date to a more readable format
  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown date';
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };
  
  // Get message preview text
  const getPreviewText = (chat) => {
    if (!chat.messages || chat.messages.length === 0) {
      return 'No messages';
    }
    
    // Get the last message
    const lastMessage = chat.messages[chat.messages.length - 1];
    return lastMessage.content || 'Empty message';
  };
  
  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-secondary-800">My Chats</h1>
        <Link to="/upload" className="btn btn-primary">
          Upload New
        </Link>
      </div>
      
      {/* Search and Filter Bar */}
      <div className="mb-8 space-y-4">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search Input */}
          <div className="relative flex-grow">
            <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-500" />
            <input
              type="text"
              placeholder="Search chats..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 p-3 w-full rounded-md border border-secondary-300 focus:ring-2 focus:ring-primary-300 focus:border-primary-500 outline-none"
            />
          </div>
          
          {/* Toggle Filter Button */}
          <button
            onClick={() => setIsFilterOpen(!isFilterOpen)}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <AdjustmentsHorizontalIcon className="h-5 w-5" />
            <span>Filters</span>
            <ChevronDownIcon className={`h-4 w-4 transition-transform ${isFilterOpen ? 'rotate-180' : ''}`} />
          </button>
          
          {/* View Mode Toggle */}
          <div className="flex rounded-md overflow-hidden border border-secondary-300">
            <button
              onClick={() => setViewMode('grid')}
              className={`px-4 py-2 ${viewMode === 'grid' ? 'bg-primary-100 text-primary-600' : 'bg-white text-secondary-600'}`}
            >
              Grid
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-4 py-2 ${viewMode === 'list' ? 'bg-primary-100 text-primary-600' : 'bg-white text-secondary-600'}`}
            >
              List
            </button>
          </div>
        </div>
        
        {/* Filter Panel */}
        {isFilterOpen && (
          <div className="bg-white p-5 rounded-md shadow-sm border border-secondary-200 grid grid-cols-1 md:grid-cols-2 gap-5">
            <div>
              <label className="block mb-2 text-secondary-700 font-medium">Category</label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full p-2 rounded-md border border-secondary-300 focus:ring-2 focus:ring-primary-300 focus:border-primary-500 outline-none"
              >
                <option value="">All Categories</option>
                {categories.map((category) => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block mb-2 text-secondary-700 font-medium">Sort By</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full p-2 rounded-md border border-secondary-300 focus:ring-2 focus:ring-primary-300 focus:border-primary-500 outline-none"
              >
                <option value="date">Newest First</option>
                <option value="title">Title (A-Z)</option>
                <option value="messages">Most Messages</option>
              </select>
            </div>
          </div>
        )}
      </div>
      
      {/* No Results Message */}
      {filteredChats.length === 0 && (
        <div className="text-center py-12 bg-secondary-50 rounded-lg">
          <ChatBubbleLeftRightIcon className="h-12 w-12 text-secondary-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-secondary-700 mb-2">No chats found</h3>
          <p className="text-secondary-600">
            Try changing your search or filters, or upload new chat screenshots.
          </p>
          <Link to="/upload" className="btn btn-primary mt-4 inline-block">
            Upload New Chat
          </Link>
        </div>
      )}
      
      {/* Grid View */}
      {viewMode === 'grid' && filteredChats.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredChats.map((chat) => (
            <Link to={`/chat/${chat.id}`} key={chat.id} className="card hover:shadow-lg transition-shadow group">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-secondary-800 group-hover:text-primary-600 transition-colors">
                    {chat.title}
                  </h3>
                  <p className="text-sm text-secondary-500">
                    {formatDate(chat.date)} • {chat.messageCount} messages
                  </p>
                </div>
                <span className="px-2 py-1 text-xs rounded-full bg-primary-50 text-primary-600">
                  {chat.category}
                </span>
              </div>
              
              <p className="text-secondary-700 mb-4 line-clamp-2">
                {chat.previewText}
              </p>
              
              {chat.tags.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {chat.tags.map((tag) => (
                    <span key={tag} className="px-2 py-1 text-xs rounded-full bg-secondary-100 text-secondary-700">
                      #{tag}
                    </span>
                  ))}
                </div>
              )}
            </Link>
          ))}
        </div>
      )}
      
      {/* List View */}
      {viewMode === 'list' && filteredChats.length > 0 && (
        <div className="space-y-4">
          {filteredChats.map((chat) => (
            <Link 
              to={`/chat/${chat.id}`} 
              key={chat.id} 
              className="block card hover:shadow-lg transition-shadow flex flex-col md:flex-row justify-between group"
            >
              <div className="flex-grow">
                <h3 className="text-lg font-semibold text-secondary-800 group-hover:text-primary-600 transition-colors mb-1">
                  {chat.title}
                </h3>
                <p className="text-secondary-700 mb-3">
                  {chat.previewText}
                </p>
                <div className="flex flex-wrap gap-2">
                  {chat.tags.map((tag) => (
                    <span key={tag} className="px-2 py-1 text-xs rounded-full bg-secondary-100 text-secondary-700">
                      #{tag}
                    </span>
                  ))}
                </div>
              </div>
              
              <div className="mt-4 md:mt-0 md:ml-6 flex flex-col items-end justify-between">
                <span className="px-2 py-1 text-xs rounded-full bg-primary-50 text-primary-600 mb-2">
                  {chat.category}
                </span>
                <div className="text-sm text-secondary-500">
                  {formatDate(chat.date)} • {chat.messageCount} messages
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default AllChats; 