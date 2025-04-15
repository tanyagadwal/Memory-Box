import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './ConversationsList.css';

function ConversationsList() {
  const [conversations, setConversations] = useState([]);
  const [categories, setCategories] = useState([]);
  const [filteredCategory, setFilteredCategory] = useState('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchConversations();
  }, []);

  const fetchConversations = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/api/conversations');
      setConversations(response.data);
      
      // Extract unique categories
      const uniqueCategories = [...new Set(response.data.map(conv => conv.category))];
      setCategories(uniqueCategories);
      
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch conversations');
      setLoading(false);
      console.error(err);
    }
  };

  const deleteConversation = async (id) => {
    try {
      await axios.delete(`http://localhost:8000/api/conversations/${id}`);
      setConversations(conversations.filter(conv => conv.id !== id));
    } catch (err) {
      setError('Failed to delete conversation');
      console.error(err);
    }
  };

  const filteredConversations = filteredCategory === 'all' 
    ? conversations 
    : conversations.filter(conv => conv.category === filteredCategory);

  if (loading) return <div className="loading">Loading conversations...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="conversations-list">
      <div className="list-header">
        <h2>Memory Drops</h2>
        <div className="filter-container">
          <div className="filter-options">
            <label htmlFor="category-filter">Filter by:</label>
            <select 
              id="category-filter"
              value={filteredCategory}
              onChange={(e) => setFilteredCategory(e.target.value)}
            >
              <option value="all"><i>all categories</i></option>
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {filteredConversations.length === 0 ? (
        <div className="empty-state fade-in">
          <p>No conversations found. Upload some chat screenshots to get started!</p>
          <Link to="/upload" className="btn btn-primary">Upload Now</Link>
        </div>
      ) : (
        <div className="conversations-grid">
          {filteredConversations.map((conv, index) => (
            <div key={conv.id} className="conversation-card fade-in" style={{animationDelay: `${index * 0.1}s`}}>
              <h3>{conv.title}</h3>
              <div className="card-meta">
                <span className="category">{conv.category}</span>
                <span className="message-count">{conv.message_count} messages</span>
              </div>
              <p className="date">{new Date(conv.date_created).toLocaleDateString()}</p>
              <div className="card-actions">
                <Link to={`/conversation/${conv.id}`} className="btn-view">View</Link>
                <button 
                  className="btn-delete"
                  onClick={() => {
                    if (window.confirm('Are you sure you want to delete this conversation?')) {
                      deleteConversation(conv.id);
                    }
                  }}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ConversationsList;