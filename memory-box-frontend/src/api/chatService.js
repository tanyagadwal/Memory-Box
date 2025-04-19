import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// In a real application, these would be API calls to a backend server
// For the demo, we'll use localStorage to persist data

/**
 * Get all saved chats
 * @returns {Promise<Array>} - Array of chat objects
 */
export const getAllChats = async () => {
  // In a real app: const response = await axios.get(`${API_URL}/api/chats`);
  // For demo, use localStorage
  try {
    const chats = localStorage.getItem('memory_box_chats');
    return chats ? JSON.parse(chats) : [];
  } catch (error) {
    console.error('Error fetching chats:', error);
    return [];
  }
};

/**
 * Get a specific chat by ID
 * @param {string} id - The chat ID
 * @returns {Promise<Object>} - The chat object
 */
export const getChatById = async (id) => {
  // In a real app: const response = await axios.get(`${API_URL}/api/chats/${id}`);
  try {
    const chats = await getAllChats();
    return chats.find(chat => chat.id === id) || null;
  } catch (error) {
    console.error(`Error fetching chat with ID ${id}:`, error);
    return null;
  }
};

/**
 * Save a new chat
 * @param {Object} chatData - The chat data to save
 * @returns {Promise<Object>} - The saved chat with ID
 */
export const saveChat = async (chatData) => {
  // In a real app: const response = await axios.post(`${API_URL}/api/chats`, chatData);
  try {
    const chats = await getAllChats();
    const newChat = {
      ...chatData,
      id: Date.now().toString(), // Simple ID generation
      date: new Date().toISOString()
    };
    
    localStorage.setItem('memory_box_chats', JSON.stringify([...chats, newChat]));
    return newChat;
  } catch (error) {
    console.error('Error saving chat:', error);
    throw new Error('Failed to save chat. Please try again.');
  }
};

/**
 * Update an existing chat
 * @param {string} id - The chat ID
 * @param {Object} chatData - The updated chat data
 * @returns {Promise<Object>} - The updated chat
 */
export const updateChat = async (id, chatData) => {
  // In a real app: const response = await axios.put(`${API_URL}/api/chats/${id}`, chatData);
  try {
    const chats = await getAllChats();
    const index = chats.findIndex(chat => chat.id === id);
    
    if (index === -1) {
      throw new Error('Chat not found');
    }
    
    const updatedChat = { ...chats[index], ...chatData };
    chats[index] = updatedChat;
    
    localStorage.setItem('memory_box_chats', JSON.stringify(chats));
    return updatedChat;
  } catch (error) {
    console.error(`Error updating chat with ID ${id}:`, error);
    throw new Error('Failed to update chat. Please try again.');
  }
};

/**
 * Delete a chat
 * @param {string} id - The chat ID to delete
 * @returns {Promise<boolean>} - Success/failure
 */
export const deleteChat = async (id) => {
  // In a real app: const response = await axios.delete(`${API_URL}/api/chats/${id}`);
  try {
    const chats = await getAllChats();
    const filteredChats = chats.filter(chat => chat.id !== id);
    
    localStorage.setItem('memory_box_chats', JSON.stringify(filteredChats));
    return true;
  } catch (error) {
    console.error(`Error deleting chat with ID ${id}:`, error);
    throw new Error('Failed to delete chat. Please try again.');
  }
};

export default {
  getAllChats,
  getChatById,
  saveChat,
  updateChat,
  deleteChat
}; 