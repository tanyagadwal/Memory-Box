import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { ArrowLeftIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/outline';
import { getChatById, updateChat, deleteChat } from '../api/chatService';

// Demo data - would normally come from API/database
const DEMO_CHATS = [
  {
    id: '1',
    title: 'Road Trip Planning',
    category: 'Friends',
    tags: ['vacation', 'summer'],
    date: '2023-06-15',
    messages: [
      {
        id: 'm1',
        sender: 'Sarah',
        content: 'Hey everyone! Are we still on for the road trip next weekend?',
        timestamp: '2023-06-10T09:30:00',
        isUser: false
      },
      {
        id: 'm2',
        sender: 'You',
        content: "Absolutely! I've already packed my bags 😁",
        timestamp: '2023-06-10T09:32:00',
        isUser: true
      },
      {
        id: 'm3',
        sender: 'Mike',
        content: 'Count me in. Should we meet at the usual spot?',
        timestamp: '2023-06-10T09:35:00',
        isUser: false
      },
      {
        id: 'm4',
        sender: 'Sarah',
        content: "Yes, let's meet at my place at 7am. We need to leave early to avoid traffic.",
        timestamp: '2023-06-10T09:38:00',
        isUser: false
      },
      {
        id: 'm5',
        sender: 'You',
        content: "Works for me! I'll bring some snacks and drinks for the trip.",
        timestamp: '2023-06-10T09:40:00',
        isUser: true
      },
      {
        id: 'm6',
        sender: 'Mike',
        content: "Great! I'll take care of the playlists 🎵",
        timestamp: '2023-06-10T09:42:00',
        isUser: false
      },
      {
        id: 'm7',
        sender: 'Sarah',
        content: "Perfect. Also, I checked the weather forecast. It's going to be sunny all weekend!",
        timestamp: '2023-06-10T09:45:00',
        isUser: false
      },
      {
        id: 'm8',
        sender: 'You',
        content: "Awesome! This is going to be epic. Can't wait!",
        timestamp: '2023-06-10T09:47:00',
        isUser: true
      },
      {
        id: 'm9',
        sender: 'Mike',
        content: 'By the way, Sarah, did you make those hotel reservations?',
        timestamp: '2023-06-10T10:15:00',
        isUser: false
      },
      {
        id: 'm10',
        sender: 'Sarah',
        content: 'Yes, all done. We have two rooms booked for Saturday and Sunday night.',
        timestamp: '2023-06-10T10:20:00',
        isUser: false
      },
      {
        id: 'm11',
        sender: 'You',
        content: "So we'll meet at 9am tomorrow, right?",
        timestamp: '2023-06-14T18:30:00',
        isUser: true
      }
    ]
  },
];

const ChatView = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [chat, setChat] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [editFormData, setEditFormData] = useState({
    title: '',
    category: ''
  });
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  
  // Fetch chat data
  useEffect(() => {
    const fetchChat = async () => {
      try {
        setIsLoading(true);
        const chatData = await getChatById(id);
        
        if (chatData) {
          setChat(chatData);
          setEditFormData({
            title: chatData.title,
            category: chatData.category
          });
        }
      } catch (error) {
        console.error('Error fetching chat:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchChat();
  }, [id]);
  
  // Format timestamp to readable time
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };
  
  // Format timestamp to date if it's a new day
  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' });
  };
  
  // Check if a message is on a different day than the previous message
  const isNewDay = (index, messages) => {
    if (index === 0) return true;
    
    const currentDate = new Date(messages[index].timestamp).toDateString();
    const prevDate = new Date(messages[index - 1].timestamp).toDateString();
    
    return currentDate !== prevDate;
  };
  
  // Handle edit form submission
  const handleEditSubmit = async (e) => {
    e.preventDefault();
    try {
      // Update chat data
      const updatedChatData = await updateChat(id, {
        ...chat,
        title: editFormData.title,
        category: editFormData.category
      });
      
      setChat(updatedChatData);
      setIsEditModalOpen(false);
    } catch (error) {
      console.error('Error updating chat:', error);
      alert('Failed to update chat. Please try again.');
    }
  };
  
  // Handle edit form change
  const handleEditChange = (e) => {
    const { name, value } = e.target;
    setEditFormData(prev => ({ ...prev, [name]: value }));
  };
  
  // Handle delete confirmation
  const handleDelete = async () => {
    try {
      await deleteChat(id);
      alert('Chat deleted successfully!');
      navigate('/chats');
    } catch (error) {
      console.error('Error deleting chat:', error);
      alert('Failed to delete chat. Please try again.');
    }
  };
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center text-secondary-600">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <p>Loading chat...</p>
        </div>
      </div>
    );
  }
  
  if (!chat) {
    return (
      <div className="text-center py-16">
        <h2 className="text-2xl font-bold text-secondary-800 mb-2">Chat Not Found</h2>
        <p className="text-secondary-600 mb-6">The chat you're looking for doesn't exist or has been deleted.</p>
        <Link to="/chats" className="btn btn-primary">
          View All Chats
        </Link>
      </div>
    );
  }
  
  return (
    <div>
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-6 pb-6 border-b border-secondary-200">
        <div className="flex items-center mb-4 md:mb-0">
          <Link to="/chats" className="p-2 rounded-full hover:bg-secondary-100 mr-2">
            <ArrowLeftIcon className="h-5 w-5 text-secondary-600" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-secondary-800">{chat.title}</h1>
            <div className="flex items-center mt-1">
              <span className="px-2 py-1 text-xs rounded-full bg-primary-50 text-primary-600 mr-3">
                {chat.category}
              </span>
              <span className="text-secondary-500 text-sm">
                {new Date(chat.date).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })}
              </span>
            </div>
          </div>
        </div>
        
        <div className="flex space-x-3">
          <button 
            onClick={() => setIsEditModalOpen(true)}
            className="btn btn-secondary flex items-center"
          >
            <PencilIcon className="h-4 w-4 mr-1" />
            Edit
          </button>
          <button 
            onClick={() => setIsDeleteModalOpen(true)}
            className="btn bg-red-50 text-red-600 hover:bg-red-100 flex items-center"
          >
            <TrashIcon className="h-4 w-4 mr-1" />
            Delete
          </button>
        </div>
      </div>
      
      {/* Chat Bubbles */}
      <div className="bg-secondary-50 rounded-lg p-4 md:p-6 min-h-[60vh] mb-6">
        <div className="max-w-3xl mx-auto space-y-4">
          {chat.messages.map((message, index) => (
            <React.Fragment key={message.id || index}>
              {isNewDay(index, chat.messages) && (
                <div className="flex justify-center my-6">
                  <span className="px-4 py-1 bg-secondary-200 text-secondary-700 text-sm rounded-full">
                    {formatDate(message.timestamp)}
                  </span>
                </div>
              )}
              
              <div className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}>
                <div className="flex flex-col max-w-[80%]">
                  {!message.isUser && (
                    <span className="text-xs text-secondary-500 mb-1 ml-2">{message.sender}</span>
                  )}
                  <div className={message.isUser ? 'chat-bubble-outgoing' : 'chat-bubble-incoming'}>
                    {message.content}
                  </div>
                  <span className={`text-xs text-secondary-500 mt-1 ${message.isUser ? 'text-right mr-2' : 'ml-2'}`}>
                    {formatTime(message.timestamp)}
                  </span>
                </div>
              </div>
            </React.Fragment>
          ))}
        </div>
      </div>
      
      {/* Tags */}
      {chat.tags && chat.tags.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-medium text-secondary-700 mb-2">Tags:</h3>
          <div className="flex flex-wrap gap-2">
            {chat.tags.map((tag, index) => (
              <span 
                key={index} 
                className="px-3 py-1 text-sm rounded-full bg-secondary-100 text-secondary-700"
              >
                #{tag}
              </span>
            ))}
          </div>
        </div>
      )}
      
      {/* Edit Modal */}
      {isEditModalOpen && (
        <div className="fixed inset-0 bg-secondary-900 bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6 shadow-xl">
            <h2 className="text-xl font-bold text-secondary-800 mb-4">Edit Chat Details</h2>
            <form onSubmit={handleEditSubmit}>
              <div className="mb-4">
                <label className="block mb-2 text-secondary-700 font-medium">Chat Title</label>
                <input
                  type="text"
                  name="title"
                  value={editFormData.title}
                  onChange={handleEditChange}
                  className="w-full p-2 rounded-md border border-secondary-300 focus:ring-2 focus:ring-primary-300 focus:border-primary-500 outline-none"
                  required
                />
              </div>
              <div className="mb-6">
                <label className="block mb-2 text-secondary-700 font-medium">Category</label>
                <select
                  name="category"
                  value={editFormData.category}
                  onChange={handleEditChange}
                  className="w-full p-2 rounded-md border border-secondary-300 focus:ring-2 focus:ring-primary-300 focus:border-primary-500 outline-none"
                  required
                >
                  <option value="Friends">Friends</option>
                  <option value="Family">Family</option>
                  <option value="Work">Work</option>
                  <option value="Relationship">Relationship</option>
                  <option value="Group Chats">Group Chats</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setIsEditModalOpen(false)}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                >
                  Save Changes
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      {/* Delete Confirmation Modal */}
      {isDeleteModalOpen && (
        <div className="fixed inset-0 bg-secondary-900 bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6 shadow-xl">
            <h2 className="text-xl font-bold text-secondary-800 mb-2">Delete Chat</h2>
            <p className="text-secondary-600 mb-6">
              Are you sure you want to delete this chat? This action cannot be undone.
            </p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setIsDeleteModalOpen(false)}
                className="btn btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                className="btn bg-red-500 text-white hover:bg-red-600"
              >
                Yes, Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatView; 