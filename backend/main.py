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
from ocr_service import extract_messages_from_image, VISION_API_AVAILABLE

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
    
    # Check if we have OCR capabilities
    if not VISION_API_AVAILABLE:
        # We'll use our fallback OCR, but let the client know
        print("Warning: Google Vision API not available, using fallback OCR")
        
    # Process tags
    tag_list = [tag.strip() for tag in tags.split(",")] if tags else []
    
    # Process images in order
    all_messages = []
    try:
        for file in files:
            contents = await file.read()
            try:
                # Extract chat messages using our OCR service
                messages = extract_messages_from_image(contents)
                all_messages.extend(messages)
            except Exception as e:
                # Log the error and continue with other files
                print(f"Error processing file {file.filename}: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
                
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
        
        return {"id": chat_id, "messageCount": len(all_messages)}
    except Exception as e:
        # Catch-all exception handler
        print(f"Unexpected error in upload_chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

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
