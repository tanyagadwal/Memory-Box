import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import {
  CloudArrowUpIcon,
  DocumentTextIcon,
  XMarkIcon,
  PhotoIcon,
  CheckCircleIcon,
  ExclamationCircleIcon
} from '@heroicons/react/24/outline';

const Upload = () => {
  const navigate = useNavigate();
  const [files, setFiles] = useState([]);
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('');
  const [tags, setTags] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  
  const onDrop = useCallback(acceptedFiles => {
    // Add preview URLs to the files for display
    const newFiles = acceptedFiles.map(file => 
      Object.assign(file, {
        preview: URL.createObjectURL(file)
      })
    );
    
    setFiles(prev => [...prev, ...newFiles]);
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
    setFiles(prev => {
      const newFiles = [...prev];
      // Revoke the URL to prevent memory leaks
      URL.revokeObjectURL(newFiles[index].preview);
      newFiles.splice(index, 1);
      return newFiles;
    });
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (files.length === 0) {
      setError('Please upload at least one screenshot.');
      return;
    }
    
    if (!title) {
      setError('Please enter a title for this chat.');
      return;
    }
    
    if (!category) {
      setError('Please select a category.');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Create form data
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });
      formData.append('title', title);
      formData.append('category', category);
      formData.append('tags', tags);
      
      // Send request to API
      const response = await axios.post('http://localhost:8000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setSuccess(true);
      
      // Clear form after successful upload
      setFiles([]);
      setTitle('');
      setCategory('');
      setTags('');
      
      // Navigate to the new chat after a delay
      setTimeout(() => {
        navigate(`/chat/${response.data.id}`);
      }, 1500);
      
    } catch (err) {
      console.error('Error uploading files:', err);
      setError(err.response?.data?.detail || 'Failed to process your screenshots. Please try again.');
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold text-secondary-800 mb-6">Upload Chat Screenshots</h1>
      
      {success && (
        <div className="bg-green-50 border border-green-200 text-green-800 rounded-lg p-4 mb-6 flex items-start">
          <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium">Success!</p>
            <p>Your chat has been processed successfully. Redirecting you to view it...</p>
          </div>
        </div>
      )}
      
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 rounded-lg p-4 mb-6 flex items-start">
          <ExclamationCircleIcon className="h-5 w-5 text-red-500 mr-2 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium">Error</p>
            <p>{error}</p>
          </div>
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Dropzone */}
        <div 
          {...getRootProps()} 
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive ? 'border-primary-400 bg-primary-50' : 'border-secondary-300 hover:border-primary-400 hover:bg-secondary-50'
          }`}
        >
          <input {...getInputProps()} />
          <CloudArrowUpIcon className="h-12 w-12 text-secondary-400 mx-auto mb-4" />
          <p className="text-secondary-700 font-medium mb-1">
            {isDragActive ? 'Drop screenshots here' : 'Drag & drop chat screenshots here'}
          </p>
          <p className="text-secondary-500 text-sm mb-3">
            or click to browse files
          </p>
          <p className="text-xs text-secondary-500">
            Supports: JPG, PNG, WebP
          </p>
        </div>
        
        {/* Preview Files */}
        {files.length > 0 && (
          <div>
            <h3 className="text-secondary-700 font-medium mb-3">Uploaded Screenshots ({files.length})</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {files.map((file, index) => (
                <div key={index} className="relative">
                  <div className="relative bg-secondary-100 rounded-lg overflow-hidden aspect-square">
                    <img 
                      src={file.preview} 
                      alt={`Screenshot ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                    <button
                      type="button"
                      onClick={() => removeFile(index)}
                      className="absolute top-2 right-2 bg-secondary-800 bg-opacity-70 text-white rounded-full p-1 hover:bg-opacity-100 transition-opacity"
                    >
                      <XMarkIcon className="h-4 w-4" />
                    </button>
                  </div>
                  <p className="mt-1 text-xs text-secondary-600 truncate">
                    {file.name}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Form Fields */}
        <div className="space-y-4">
          <div>
            <label htmlFor="title" className="block text-secondary-700 font-medium mb-1">
              Chat Title
            </label>
            <input
              type="text"
              id="title"
              value={title}
              onChange={e => setTitle(e.target.value)}
              placeholder="E.g., Family Group Chat, Work Project Team, etc."
              className="w-full"
              required
            />
          </div>
          
          <div>
            <label htmlFor="category" className="block text-secondary-700 font-medium mb-1">
              Category
            </label>
            <select
              id="category"
              value={category}
              onChange={e => setCategory(e.target.value)}
              className="w-full"
              required
            >
              <option value="">Select a category</option>
              <option value="WhatsApp">WhatsApp</option>
              <option value="Messenger">Messenger</option>
              <option value="Telegram">Telegram</option>
              <option value="Instagram">Instagram</option>
              <option value="WeChat">WeChat</option>
              <option value="Discord">Discord</option>
              <option value="Slack">Slack</option>
              <option value="iMessage">iMessage</option>
              <option value="Friends">Friends</option>
              <option value="Family">Family</option>
              <option value="Work">Work</option>
              <option value="Other">Other</option>
            </select>
          </div>
          
          <div>
            <label htmlFor="tags" className="block text-secondary-700 font-medium mb-1">
              Tags <span className="text-secondary-500 font-normal">(optional, comma-separated)</span>
            </label>
            <input
              type="text"
              id="tags"
              value={tags}
              onChange={e => setTags(e.target.value)}
              placeholder="E.g., family, vacation, project, etc."
              className="w-full"
            />
          </div>
        </div>
        
        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || success}
          className={`w-full btn ${loading || success ? 'bg-secondary-400 cursor-not-allowed' : 'btn-primary'}`}
        >
          {loading ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Processing...
            </>
          ) : success ? (
            <>
              <CheckCircleIcon className="h-5 w-5 mr-1" />
              Processed Successfully
            </>
          ) : (
            <>
              <DocumentTextIcon className="h-5 w-5 mr-1" />
              Process Chat
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default Upload; 