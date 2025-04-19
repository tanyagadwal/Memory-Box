import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { CloudArrowUpIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { useNavigate } from 'react-router-dom';
import { processImageWithOCR } from '../api/ocrService';
import { saveChat } from '../api/chatService';

const Upload = () => {
  const navigate = useNavigate();
  const [files, setFiles] = useState([]);
  const [formData, setFormData] = useState({
    title: '',
    category: '',
    tags: ''
  });
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);
  const [processingStatus, setProcessingStatus] = useState('');

  const categories = [
    'Friends',
    'Family',
    'Work',
    'Relationship',
    'Group Chats',
    'Other'
  ];

  const onDrop = useCallback(acceptedFiles => {
    // Filter for only image files
    const imageFiles = acceptedFiles.filter(file => file.type.startsWith('image/'));
    
    // Map files to add preview URLs
    const newFiles = imageFiles.map(file => Object.assign(file, {
      preview: URL.createObjectURL(file)
    }));
    
    setFiles(prevFiles => [...prevFiles, ...newFiles]);
    setError(null);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': [],
      'image/png': [],
      'image/webp': []
    },
    multiple: true
  });

  const removeFile = (index) => {
    const newFiles = [...files];
    URL.revokeObjectURL(newFiles[index].preview);
    newFiles.splice(index, 1);
    setFiles(newFiles);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (files.length === 0) {
      setError('Please upload at least one image');
      return;
    }
    
    if (!formData.title.trim()) {
      setError('Please provide a title');
      return;
    }
    
    if (!formData.category) {
      setError('Please select a category');
      return;
    }
    
    setIsUploading(true);
    setProcessingStatus('Uploading files...');
    setError(null);
    
    try {
      // Process each file with OCR
      const allMessages = [];
      
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        setProcessingStatus(`Processing image ${i + 1} of ${files.length}...`);
        
        try {
          // Process the image with OCR using the backend API
          const result = await processImageWithOCR(file);
          
          if (!result.success) {
            throw new Error(result.error || 'OCR processing failed');
          }
          
          // Add the extracted messages to our collection
          if (result.messages && result.messages.length > 0) {
            // Format the messages with proper IDs
            const formattedMessages = result.messages.map((msg, msgIndex) => ({
              id: `msg_${i}_${msgIndex}`,
              sender: msg.sender || 'Unknown',
              content: msg.content || '',
              timestamp: msg.timestamp || new Date().toISOString(),
              isUser: msg.sender === 'You' || msg.sender === 'Me'
            }));
            
            allMessages.push(...formattedMessages);
          }
        } catch (err) {
          console.error('Error processing image:', err);
          setError(`Failed to process image ${file.name}. ${err.message}`);
          setIsUploading(false);
          return;
        }
      }
      
      setProcessingStatus('Saving chat data...');
      
      // Parse tags from comma-separated string
      const tags = formData.tags
        ? formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag)
        : [];
      
      // Create chat object
      const chatData = {
        title: formData.title,
        category: formData.category,
        tags,
        messages: allMessages
      };
      
      // Save chat data
      // In a real app, we would call the backend API
      // For demo, we'll use our local storage service
      const savedChat = await saveChat(chatData);
      
      // Show success message
      alert('Upload successful! Chat data extracted and saved.');
      
      // Redirect to the chat view
      navigate(`/chat/${savedChat.id}`);
    } catch (err) {
      setError('Upload failed. Please try again.');
      console.error('Upload error:', err);
    } finally {
      setIsUploading(false);
      setProcessingStatus('');
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-8 text-secondary-800">Upload Chat Screenshots</h1>
      
      {error && (
        <div className="mb-6 p-4 bg-red-50 border-l-4 border-red-500 text-red-700">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-8">
        {/* File Dropzone */}
        <div 
          {...getRootProps()} 
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive 
              ? 'border-primary-400 bg-primary-50' 
              : 'border-secondary-300 hover:border-primary-300 hover:bg-secondary-50'
          }`}
        >
          <input {...getInputProps()} />
          <CloudArrowUpIcon className="h-12 w-12 text-secondary-400 mx-auto mb-4" />
          <p className="text-lg text-secondary-600 mb-2">
            {isDragActive
              ? 'Drop the files here...'
              : 'Drag & drop your chat screenshots here'}
          </p>
          <p className="text-sm text-secondary-500">
            Supported formats: JPG, PNG, WebP
          </p>
          <button
            type="button"
            className="mt-4 btn btn-secondary"
            onClick={e => {
              e.stopPropagation();
              document.querySelector('input[type="file"]').click();
            }}
          >
            Browse Files
          </button>
        </div>
        
        {/* File Previews */}
        {files.length > 0 && (
          <div className="space-y-4">
            <h3 className="font-medium text-secondary-700">Selected Files ({files.length})</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
              {files.map((file, index) => (
                <div key={index} className="relative rounded-md overflow-hidden border border-secondary-200 bg-white">
                  <img 
                    src={file.preview} 
                    alt={`Preview ${index}`}
                    className="w-full h-32 object-cover"
                  />
                  <button
                    type="button"
                    onClick={() => removeFile(index)}
                    className="absolute top-1 right-1 p-1 rounded-full bg-secondary-800 bg-opacity-60 text-white hover:bg-opacity-80 transition-opacity"
                  >
                    <XMarkIcon className="h-4 w-4" />
                  </button>
                  <div className="p-2 text-xs truncate text-secondary-600">
                    {file.name}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Form Fields */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="col-span-full">
            <label htmlFor="title" className="block mb-2 font-medium text-secondary-700">
              Chat Title *
            </label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              className="w-full p-3 rounded-md border border-secondary-300 focus:ring-2 focus:ring-primary-300 focus:border-primary-500 outline-none transition"
              placeholder="E.g., Road Trip Planning with Friends"
              required
            />
          </div>
          
          <div>
            <label htmlFor="category" className="block mb-2 font-medium text-secondary-700">
              Category *
            </label>
            <select
              id="category"
              name="category"
              value={formData.category}
              onChange={handleChange}
              className="w-full p-3 rounded-md border border-secondary-300 focus:ring-2 focus:ring-primary-300 focus:border-primary-500 outline-none transition"
              required
            >
              <option value="">Select a category</option>
              {categories.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label htmlFor="tags" className="block mb-2 font-medium text-secondary-700">
              Tags (optional)
            </label>
            <input
              type="text"
              id="tags"
              name="tags"
              value={formData.tags}
              onChange={handleChange}
              className="w-full p-3 rounded-md border border-secondary-300 focus:ring-2 focus:ring-primary-300 focus:border-primary-500 outline-none transition"
              placeholder="E.g., vacation, summer, friends (comma-separated)"
            />
          </div>
        </div>
        
        {/* Submit Button */}
        <div className="pt-4">
          <button
            type="submit"
            disabled={isUploading}
            className={`btn btn-primary py-3 px-6 w-full md:w-auto ${
              isUploading ? 'opacity-70 cursor-not-allowed' : ''
            }`}
          >
            {isUploading ? processingStatus || 'Processing...' : 'Upload and Process'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default Upload; 