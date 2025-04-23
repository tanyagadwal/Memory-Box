from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import os
import uuid
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import io
from datetime import datetime
from ocr_service import extract_messages_from_image, VISION_API_AVAILABLE, verify_vision_api_credentials

# Set Google Cloud credentials
# Path to service account credentials file
GOOGLE_CREDENTIALS_PATH = "/home/madhav/Desktop/memvol/Memory-Box/mimetic-card-457310-n5-890f77604726.json"
if os.path.exists(GOOGLE_CREDENTIALS_PATH):
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GOOGLE_CREDENTIALS_PATH
    print(f"Google Cloud credentials set from: {GOOGLE_CREDENTIALS_PATH}")
else:
    print(f"Warning: Google Cloud credentials file not found at: {GOOGLE_CREDENTIALS_PATH}")
    print("Will use fallback OCR method (Tesseract)")

# Verify the credentials are working
vision_api_working = verify_vision_api_credentials()
if vision_api_working:
    print("✅ Google Vision API is properly configured and working")
else:
    print("⚠️ Google Vision API is not working, will use Tesseract OCR as fallback")

# Initialize FastAPI app
app = FastAPI(
    title="Memory Box API",
    description="API for processing chat screenshots with OCR",
    version="1.0.0"
)

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define data models
class Message(BaseModel):
    sender: str  # "user" or "other"
    text: str
    timestamp: Optional[str] = None

class Chat(BaseModel):
    id: str
    title: str
    category: str
    date: str
    messages: List[Message]
    tags: List[str] = []

# In-memory storage (replace with a proper database in production)
chats_db = {}

def save_chat(chat_data):
    """Save chat data to our storage"""
    chat_id = chat_data.get("id", str(uuid.uuid4()))
    if "id" not in chat_data:
        chat_data["id"] = chat_id
    
    # Ensure we have a date
    if "date" not in chat_data:
        chat_data["date"] = datetime.now().isoformat()
        
    chats_db[chat_id] = chat_data
    return chat_id

@app.get("/")
def read_root():
    return {"message": "Memory Box API is running"}

@app.post("/upload")
async def upload_chat(
    files: List[UploadFile] = File(...),
    title: str = Form(...),
    category: str = Form(...),
    tags: str = Form("")
):
    """
    Upload chat screenshots and extract messages
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    # Process tags
    tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
    
    # Process images in order
    all_messages = []
    processed_files = 0
    failed_files = 0
    
    for file in files:
        try:
            contents = await file.read()
            try:
                # Extract chat messages using our OCR service
                messages = extract_messages_from_image(contents)
                if messages:
                    all_messages.extend(messages)
                    processed_files += 1
                else:
                    print(f"Warning: No messages extracted from {file.filename}")
                    failed_files += 1
            except Exception as e:
                print(f"Error processing file {file.filename}: {str(e)}")
                failed_files += 1
        except Exception as e:
            print(f"Error reading file {file.filename}: {str(e)}")
            failed_files += 1
    
    if not all_messages and failed_files > 0:
        # All files failed to process
        raise HTTPException(
            status_code=500, 
            detail="Failed to extract any messages from your screenshots. Please try with different images."
        )
    
    # Sort messages by timestamp if available, otherwise keep original order
    if all(msg.get("timestamp") for msg in all_messages):
        all_messages.sort(key=lambda msg: msg["timestamp"])
    
    # Create chat object
    chat_data = {
        "id": str(uuid.uuid4()),
        "title": title,
        "category": category,
        "date": datetime.now().isoformat(),
        "messages": all_messages,
        "tags": tag_list,
        "messageCount": len(all_messages)
    }
    
    # Save chat
    chat_id = save_chat(chat_data)
    
    # Provide a detailed response with warnings if some files couldn't be processed
    response = {
        "id": chat_id, 
        "messageCount": len(all_messages),
        "filesProcessed": processed_files,
        "filesFailed": failed_files,
        "totalFiles": processed_files + failed_files
    }
    
    if failed_files > 0:
        response["warning"] = f"{failed_files} out of {processed_files + failed_files} files couldn't be processed correctly."
    
    return response

@app.get("/chats")
def get_all_chats():
    """Get all chats"""
    chats = []
    for chat_id, chat_data in chats_db.items():
        # Add a preview text from first few messages
        preview_text = ""
        if chat_data.get("messages"):
            messages = chat_data["messages"][:3]  # First 3 messages
            preview_text = ". ".join([m["text"][:30] for m in messages])
            if len(preview_text) > 120:
                preview_text = preview_text[:117] + "..."
                
        chats.append({
            "id": chat_id,
            "title": chat_data.get("title", "Untitled Chat"),
            "category": chat_data.get("category", "Uncategorized"),
            "date": chat_data.get("date"),
            "messageCount": len(chat_data.get("messages", [])),
            "tags": chat_data.get("tags", []),
            "previewText": preview_text
        })
    
    return chats

@app.get("/chats/{chat_id}")
def get_chat(chat_id: str):
    """Get a specific chat by ID"""
    if chat_id not in chats_db:
        raise HTTPException(status_code=404, detail="Chat not found")
        
    return chats_db[chat_id]

@app.put("/chats/{chat_id}")
def update_chat(chat_id: str, chat: Dict[str, Any]):
    """Update a chat"""
    if chat_id not in chats_db:
        raise HTTPException(status_code=404, detail="Chat not found")
        
    # Update only allowed fields
    allowed_fields = ["title", "category", "tags"]
    for field in allowed_fields:
        if field in chat:
            chats_db[chat_id][field] = chat[field]
            
    return {"message": "Chat updated successfully"}

@app.delete("/chats/{chat_id}")
def delete_chat(chat_id: str):
    """Delete a chat"""
    if chat_id not in chats_db:
        raise HTTPException(status_code=404, detail="Chat not found")
        
    del chats_db[chat_id]
    return {"message": "Chat deleted successfully"}

@app.get("/status")
def check_status():
    """Check the API and OCR service status"""
    return {
        "status": "running",
        "vision_api_available": VISION_API_AVAILABLE,
        "vision_api_working": verify_vision_api_credentials(),
        "fallback_ocr": "Tesseract",
        "credentials_path": os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'Not set')
    }

# For demo/testing - add some sample data
if __name__ == "__main__":
    # Create a few sample chats
    sample_chat = {
        "id": "sample-1",
        "title": "Sample WhatsApp Chat",
        "category": "WhatsApp",
        "date": "2023-05-15T12:30:45",
        "messages": [
            {"sender": "other", "text": "Hey, how are you?", "timestamp": "10:30 AM"},
            {"sender": "user", "text": "I'm good! How about you?", "timestamp": "10:32 AM"},
            {"sender": "other", "text": "Doing well. Want to meet up later?", "timestamp": "10:33 AM"},
            {"sender": "user", "text": "Sure, what time?", "timestamp": "10:35 AM"}
        ],
        "tags": ["friends", "meetup"],
        "messageCount": 4
    }
    
    save_chat(sample_chat)
# Added Vision API verification
