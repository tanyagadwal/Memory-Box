# Memory Box

Memory Box is a web application that allows users to upload screenshots of chat conversations, extract structured messages using OCR (Optical Character Recognition), and store them in a searchable, organized manner.

## Features

- Upload and process chat screenshots (JPEG, PNG, WebP)
- Extract text from images using Google Cloud Vision OCR
- Organize chats with titles, categories, and tags
- View conversations in a beautiful chat bubble interface
- Filter and search through your saved chats
- Edit and delete chat metadata

## Tech Stack

### Frontend
- React.js
- Tailwind CSS
- React Router for navigation
- React Dropzone for file uploads
- Axios for API communication

### Backend
- FastAPI (Python)
- Google Cloud Vision API for OCR
- RESTful API architecture

## Setup and Installation

### Prerequisites
- Node.js and npm
- Python 3.8+
- Google Cloud Vision API credentials

### Frontend Setup
1. Navigate to the frontend directory:
   ```
   cd memory-box-frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Create a `.env` file with the following content:
   ```
   REACT_APP_API_URL=http://localhost:8000
   ```

4. Start the development server:
   ```
   npm start
   ```

### Backend Setup
1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up Google Cloud Vision credentials:
   - Create a service account and download the JSON key file
   - Set the environment variable:
     ```
     export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credentials.json
     ```

5. Start the server:
   ```
   python main.py
   ```

## Usage

1. **Upload Screenshots**: 
   - Go to the Upload page
   - Drag and drop your chat screenshots
   - Add title, category, and optional tags
   - Submit to process with OCR

2. **Browse Chats**:
   - View all your chats in a grid or list view
   - Filter by category or search by content
   - Click on any chat to view the full conversation

3. **View Conversations**:
   - See messages in a familiar chat bubble interface
   - Edit chat metadata or delete conversations as needed

## License

MIT

## Acknowledgements

- Google Cloud Vision API for OCR capabilities
- Tailwind CSS for beautiful styling
- Heroicons for UI icons