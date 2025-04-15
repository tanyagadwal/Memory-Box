import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import './UploadForm.css';

function UploadForm() {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('');
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [preview, setPreview] = useState([]);
  const [dragActive, setDragActive] = useState(false);

  const handleFileChange = (e) => {
    if (e.target.files) {
      const fileList = Array.from(e.target.files);
      setFiles(fileList);
      
      // Generate previews
      const previews = fileList.map(file => ({
        name: file.name,
        url: URL.createObjectURL(file)
      }));
      
      setPreview(previews);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const fileList = Array.from(e.dataTransfer.files);
      setFiles(fileList);
      
      // Generate previews
      const previews = fileList.map(file => ({
        name: file.name,
        url: URL.createObjectURL(file)
      }));
      
      setPreview(previews);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!title || !category || files.length === 0) {
      setError('Please fill all fields and upload at least one image');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('title', title);
      formData.append('category', category);
      
      files.forEach(file => {
        formData.append('files', file);
      });
      
      const response = await axios.post('http://localhost:8000/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setLoading(false);
      navigate(`/conversation/${response.data.conversation_id}`);
    } catch (err) {
      setError('Failed to upload files. Please try again.');
      setLoading(false);
      console.error(err);
    }
  };

  return (
    <div className="upload-form-container">
      <h2>Upload Chat Screenshots</h2>
      
      {error && <div className="error">{error}</div>}
      
      <form onSubmit={handleSubmit} className="upload-form">
        <div className="form-group">
          <label htmlFor="title">Conversation Title</label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g., Trip Planning with Friends"
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="category">Category</label>
          <input
            type="text"
            id="category"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            placeholder="e.g., Friends, Family, Work"
            required
            list="category-suggestions"
          />
          <datalist id="category-suggestions">
            <option value="Friends" />
            <option value="Family" />
            <option value="Work" />
            <option value="School" />
            <option value="Travel" />
          </datalist>
        </div>
        
        <div 
          className={`form-group file-upload-area ${dragActive ? 'drag-active' : ''}`}
          onDragEnter={handleDrag}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
        >
          <label htmlFor="files">Upload Screenshots</label>
          <div className="file-input-container">
            <input
              type="file"
              id="files"
              onChange={handleFileChange}
              accept="image/*"
              multiple
              required
              className="file-input"
            />
            <div className="file-placeholder">
              <div className="upload-icon">📸</div>
              <p>Drag & drop image files here or click to select</p>
              <p className="input-helper">Select multiple screenshots of your chat in order</p>
            </div>
          </div>
        </div>
        
        {preview.length > 0 && (
          <div className="image-previews fade-in">
            <h3>Selected Images ({preview.length})</h3>
            <div className="preview-grid">
              {preview.map((item, index) => (
                <div key={index} className="preview-item" style={{animationDelay: `${index * 0.1}s`}}>
                  <img src={item.url} alt={`Preview ${index + 1}`} />
                  <p>{item.name}</p>
                </div>
              ))}
            </div>
          </div>
        )}
        
        <div className="form-actions">
          <button 
            type="button" 
            className="btn btn-cancel"
            onClick={() => navigate('/')}
          >
            Cancel
          </button>
          <button 
            type="submit" 
            className="btn btn-submit"
            disabled={loading}
          >
            {loading ? 
              <>
                <span className="spinner"></span>
                Processing...
              </> : 
              <>Upload and Process</>
            }
          </button>
        </div>
      </form>
    </div>
  );
}

export default UploadForm;