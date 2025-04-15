import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './ConversationView.css';

function ConversationView() {
  const [conversation, setConversation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const { id } = useParams();
  const navigate = useNavigate();
  const messagesEndRef = React.useRef(null);

  useEffect(() => {
    const fetchConversation = async () => {
      try {
        const response = await axios.get(`http://localhost:8000/api/conversations/${id}`);
        setConversation(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to load conversation. Please try again.');
        setLoading(false);
        console.error(err);
      }
    };

    fetchConversation();
  }, [id]);

  // Scroll to bottom of messages when they load
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [conversation]);

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this conversation?')) {
      try {
        await axios.delete(`http://localhost:8000/api/conversations/${id}`);
        navigate('/');
      } catch (err) {
        setError('Failed to delete conversation. Please try again.');
        console.error(err);
      }
    }
  };

//   const handleEdit = () => {
//     // Implement edit functionality or navigate to edit page
//     console.log('Edit button clicked');
//   };

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    return timestamp;
  };

  if (loading) {
    return <div className="loading-container">Loading conversation...</div>;
  }

  if (error) {
    return <div className="error-container">{error}</div>;
  }

  if (!conversation) {
    return <div className="not-found-container">Conversation not found.</div>;
  }

  return (
    <div className="conversation-container">
      <div className="conversation-header">
        <h2>{conversation.title}</h2>
        <div className="conversation-meta">
          <span className="category-badge">{conversation.category}</span>
          <span className="date-info">{new Date(conversation.date_created).toLocaleDateString()}</span>
        </div>
        <div className="conversation-actions">
          <button className="back-button" onClick={() => navigate('/')}>
            ← Back to All
          </button>
          {/* <button className="edit-button" onClick={handleEdit}>
            ✏️ Edit
          </button> */}
          <button className="delete-button" onClick={handleDelete}>
            🗑️ Delete
          </button>
        </div>
      </div>

      <div className="messages-container">
        {conversation.messages.map((message, index) => (
          <div 
            key={index} 
            className={`message-bubble ${message.sender === 'You' ? 'message-outgoing' : 'message-incoming'}`}
            style={{ animationDelay: `${index * 0.05}s` }}
          >
            <div className="message-header">
              <span className="message-sender">{message.sender}</span>
              {message.timestamp && (
                <span className="message-timestamp">{formatTimestamp(message.timestamp)}</span>
              )}
            </div>
            <div className="message-content">{message.content}</div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}

export default ConversationView;