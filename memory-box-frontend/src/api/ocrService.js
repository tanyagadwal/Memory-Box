import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Processes an image with OCR using Google Cloud Vision API
 * @param {File} imageFile - The image file to process
 * @returns {Promise<Object>} - The extracted messages and metadata
 */
export const processImageWithOCR = async (imageFile) => {
  try {
    // Create a FormData object to send the file
    const formData = new FormData();
    formData.append('image', imageFile);
    
    // Call the backend API which integrates with Google Cloud Vision
    const response = await axios.post(`${API_URL}/api/ocr`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('Error processing image with OCR:', error);
    throw new Error('Failed to process image. Please try again.');
  }
};

/**
 * Extracts structured chat data from OCR results
 * @param {Object} ocrResults - The raw OCR results
 * @returns {Object} - Structured chat data including messages, timestamps, and senders
 */
export const extractChatData = (ocrResults) => {
  // This function would normally implement complex logic to parse OCR results
  // For demo purposes, we'll return a simplified structure
  const { text } = ocrResults;
  
  // Basic example of message extraction
  // In a real application, this would use more sophisticated NLP or pattern matching
  const messages = text.split('\n\n')
    .filter(line => line.trim().length > 0)
    .map((line, index) => {
      // Simple pattern matching to identify message parts
      // Real implementation would be much more sophisticated
      const parts = line.split('\n');
      const sender = parts[0].split(':')[0].trim();
      const timestamp = parts[0].includes('[') ? parts[0].match(/\[(.*?)\]/)[1] : 'Unknown time';
      const content = parts.slice(1).join('\n').trim();
      
      return {
        id: `msg_${index}`,
        sender,
        timestamp,
        content,
        isUser: sender.toLowerCase().includes('you') || sender === 'Me',
      };
    });
  
  return {
    messages,
    metadata: {
      totalMessages: messages.length,
      extractedAt: new Date().toISOString(),
    }
  };
};

export default {
  processImageWithOCR,
  extractChatData,
}; 