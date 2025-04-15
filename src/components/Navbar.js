import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function Navbar() {
  const location = useLocation();
  
  // Function to check if a path is active
  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <h1>Memory Box</h1>
      </div>
      <ul className="nav-links">
        <li>
          <Link 
            to="/" 
            className={isActive('/') ? 'active' : ''}
            style={isActive('/') ? { 
              backgroundColor: 'rgba(255, 255, 255, 0.3)',
              transform: 'translateY(-2px)',
              boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)'
            } : {}}
          >
            My Conversations
          </Link>
        </li>
        <li>
          <Link 
            to="/upload" 
            className={isActive('/upload') ? 'active' : ''}
            style={isActive('/upload') ? { 
              backgroundColor: 'rgba(255, 255, 255, 0.3)',
              transform: 'translateY(-2px)',
              boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)'
            } : {}}
          >
            Upload New
          </Link>
        </li>
      </ul>
    </nav>
  );
}

export default Navbar;