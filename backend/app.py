# from fastapi import FastAPI, File, UploadFile, HTTPException, Form
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from typing import List, Optional
# import pytesseract
# from PIL import Image, ImageDraw, UnidentifiedImageError
# import io
# import re
# import os
# import platform
# import json
# import shutil
# from datetime import datetime
# import uuid
# import string
# import sys

# # Configure Tesseract path on Windows
# if platform.system() == "Windows":
#     pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# app = FastAPI(title="Chat Memory App")

# # Configure CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # In production, replace with specific origins
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Models
# class Message(BaseModel):
#     sender: str
#     content: str
#     timestamp: Optional[str] = None

# class Conversation(BaseModel):
#     id: str
#     title: str
#     category: str
#     date_created: str
#     messages: List[Message]

# # In-memory storage (replace with database in production)
# CONVERSATIONS = {}
# UPLOAD_DIR = "uploads"
# DEBUG_DIR = "debug"

# # Ensure directories exist
# os.makedirs(UPLOAD_DIR, exist_ok=True)
# os.makedirs(DEBUG_DIR, exist_ok=True)

# def advanced_ocr_process(image_bytes, debug=False):
#     """
#     Advanced OCR process adapted from the first script to extract chat messages from screenshots
#     """
#     messages = []
#     other_speaker_name = "Other Speaker"  # Default fallback name
    
#     try:
#         # Open image and convert to grayscale for potentially better OCR
#         img_bytes_io = io.BytesIO(image_bytes)
#         img_base = Image.open(img_bytes_io)
#         img = img_base.convert('L')
        
#         img_width, img_height = img.size
#         center_x = img_width / 2
        
#         # --- 1. Attempt to Extract Other Speaker's Name ---
#         try:
#             # Define crop box for the top-left area (adjust percentages if needed)
#             name_crop_box = (int(img_width * 0.05),  # give small left margin
#                           int(img_height * 0.02),  # small top margin
#                           int(img_width * 0.35),  # up to 35% width
#                           int(img_height * 0.10))  # up to 10% height
#             name_crop_img = img.crop(name_crop_box)
            
#             if debug:
#                 # Save debug images if needed
#                 debug_id = uuid.uuid4()
#                 # Draw rectangle on original for context
#                 draw = ImageDraw.Draw(img_base)
#                 draw.rectangle(name_crop_box, outline="red", width=2)
#                 img_base.save(os.path.join(DEBUG_DIR, f"debug_name_crop_context_{debug_id}.png"))
#                 name_crop_img.save(os.path.join(DEBUG_DIR, f"debug_name_crop_{debug_id}.png"))
            
#             # OCR the cropped area
#             config = '--psm 6'
#             extracted_text = pytesseract.image_to_string(name_crop_img, config=config).strip()
            
#             # Clean the extracted text
#             if extracted_text:
#                 # Remove common trailing noise like "typing..."
#                 extracted_text = re.sub(r'\s*typing.*$', '', extracted_text, flags=re.IGNORECASE).strip()
#                 # Remove leading/trailing punctuation and known emojis/symbols
#                 extracted_text = extracted_text.strip(string.punctuation + string.whitespace + '🍞✓')
                
#                 # Take the first significant word found
#                 parts = extracted_text.split(None, 1)  # Split only on first whitespace
#                 if parts and parts[0] and len(parts[0]) > 1:  # Check if the first part is non-empty and longer than 1 char
#                     potential_name = parts[0]
#                     # Further check if it looks like a name (e.g., starts with uppercase)
#                     if potential_name[0].isupper():
#                         other_speaker_name = potential_name
#                         print(f"INFO: Detected speaker name: {other_speaker_name}")
#                     else:
#                         print(f"WARN: Extracted text '{potential_name}' from name area doesn't look like a typical name. Using fallback '{other_speaker_name}'.")
#                 else:
#                     print(f"WARN: Could not reliably extract speaker name from '{extracted_text}'. Using fallback '{other_speaker_name}'.")
#             else:
#                 print(f"WARN: OCR found no text in the name crop area. Using fallback '{other_speaker_name}'.")
                
#         except Exception as name_e:
#             print(f"WARN: Error during speaker name extraction: {name_e}. Using fallback '{other_speaker_name}'.")
            
#         # --- 2. Process Full Image for Messages ---
#         print("INFO: Starting OCR processing for messages...")
#         ocr_data = pytesseract.image_to_data(img, config='--psm 3', output_type=pytesseract.Output.DATAFRAME)
#         print(f"INFO: OCR processing complete. Found {len(ocr_data)} initial words/symbols.")
        
#         # --- Data Cleaning and Structuring ---
#         # Filter low confidence, NaN text, empty strings
#         ocr_data = ocr_data[ocr_data.conf > 40]  # Confidence threshold
#         ocr_data = ocr_data.dropna(subset=['text'])
#         ocr_data['text'] = ocr_data['text'].astype(str).str.strip()
#         ocr_data = ocr_data[ocr_data.text != '']
#         print(f"INFO: Filtered down to {len(ocr_data)} words with confidence > 40.")
        
#         current_line_text = []
#         last_block, last_par, last_line, last_top = -1, -1, -1, -1
#         line_top, line_left, line_width, line_height = -1, -1, -1, -1
#         line_words_coords = []  # Could be used for more advanced line merging
        
#         for index, row in ocr_data.sort_values(by=['block_num', 'par_num', 'line_num', 'word_num']).iterrows():
#             # Skip text likely part of the header/name area we already processed (use a slightly larger margin than name crop)
#             # Also skip potential footer elements if they exist
#             if row['top'] < int(img_height * 0.11) or row['top'] > int(img_height * 0.95):
#                 continue
                
#             # Determine if it's a new line
#             # Condition: Different block/para/line OR large vertical gap relative to text height
#             is_new_ocr_line = row['block_num'] != last_block or row['par_num'] != last_par or row['line_num'] != last_line
#             vertical_gap = (row['top'] - last_top) > (line_height * 1.5) if line_height > 0 and last_top > 0 else False
#             is_new_line = is_new_ocr_line or vertical_gap
            
#             if is_new_line:
#                 # --- Process the previously buffered line ---
#                 if current_line_text:
#                     full_text = " ".join(current_line_text)
#                     # Clean timestamps, checkmarks etc.
#                     full_text = re.sub(r'\b\d{1,2}:\d{2}\b', '', full_text).strip()  # HH:MM
#                     full_text = re.sub(r'[✓✔]{1,2}\s*$', '', full_text).strip()  # Trailing checkmarks unicode
#                     full_text = re.sub(r'\s+[vV][vV]?\s*$', '', full_text).strip()  # Trailing checkmarks as V/VV
                    
#                     # Filter out lines that are likely just speaker name labels (common in replies)
#                     is_speaker_label = False
#                     lower_text = full_text.lower()
#                     lower_other_name = other_speaker_name.lower()
#                     # Check if the text IS the speaker name (allow slight variations) and is short
#                     if len(full_text) < len(other_speaker_name) + 5:
#                         # Simple check if the name appears in the short text
#                         if lower_other_name in lower_text:
#                             is_speaker_label = True
#                     # Check if it's just "You" (case insensitive)
#                     if len(full_text) < 6 and "you" == lower_text:
#                         is_speaker_label = True
                        
#                     # Add message if it's reasonably long and not identified as just a speaker label
#                     if full_text and len(full_text) > 1 and not is_speaker_label:
#                         line_center = line_left + (line_width / 2)
#                         speaker = "Unknown"
#                         # Determine speaker based on horizontal position relative to center
#                         margin = img_width * 0.05  # Margin around the center line
#                         if line_center > center_x + margin:
#                             speaker = "You"
#                         elif line_center < center_x - margin:
#                             speaker = other_speaker_name  # Use extracted/fallback name
                            
#                         if speaker != "Unknown":
#                             # Get approximate timestamp if available in the text
#                             timestamp_match = re.search(r'\b(\d{1,2}:\d{2})\b', full_text)
#                             timestamp = timestamp_match.group(1) if timestamp_match else None
                            
#                             messages.append(Message(
#                                 sender=speaker,
#                                 content=full_text,
#                                 timestamp=timestamp
#                             ))
#                 # --- End processing previous line ---
                
#                 # Reset for the new line starting with the current word
#                 current_line_text = [row['text']]
#                 line_top = row['top']
#                 line_left = row['left']
#                 line_width = row['width']
#                 line_height = row['height']
#                 last_top = row['top'] + row['height']  # Use bottom edge for vertical gap check
#                 last_block, last_par, last_line = row['block_num'], row['par_num'], row['line_num']
#             else:
#                 # Continue accumulating text for the current line
#                 current_line_text.append(row['text'])
#                 # Update line bounding box
#                 line_width = (row['left'] + row['width']) - line_left  # Width from start of line to end of current word
#                 line_height = max(line_height, row['height'])  # Max height observed in line
#                 last_top = max(last_top, row['top'] + row['height'])  # Furthest bottom edge
                
#         # --- Process the very last buffered line after the loop ends ---
#         if current_line_text:
#             full_text = " ".join(current_line_text)
#             full_text = re.sub(r'\b\d{1,2}:\d{2}\b', '', full_text).strip()
#             full_text = re.sub(r'[✓✔]{1,2}\s*$', '', full_text).strip()
#             full_text = re.sub(r'\s+[vV][vV]?\s*$', '', full_text).strip()
            
#             is_speaker_label = False
#             lower_text = full_text.lower()
#             lower_other_name = other_speaker_name.lower()
#             if len(full_text) < len(other_speaker_name) + 5:
#                 if lower_other_name in lower_text:
#                     is_speaker_label = True
#             if len(full_text) < 6 and "you" == lower_text:
#                 is_speaker_label = True
                
#             if full_text and len(full_text) > 1 and not is_speaker_label:
#                 line_center = line_left + (line_width / 2)
#                 speaker = "Unknown"
#                 margin = img_width * 0.05
#                 if line_center > center_x + margin:
#                     speaker = "You"
#                 elif line_center < center_x - margin:
#                     speaker = other_speaker_name
                    
#                 if speaker != "Unknown":
#                     # Get approximate timestamp if available in the text
#                     timestamp_match = re.search(r'\b(\d{1,2}:\d{2})\b', full_text)
#                     timestamp = timestamp_match.group(1) if timestamp_match else None
                    
#                     messages.append(Message(
#                         sender=speaker,
#                         content=full_text,
#                         timestamp=timestamp
#                     ))
#         # --- End processing last line ---
        
#         # --- 3. Sort messages chronologically based on vertical position ---
#         messages.sort(key=lambda m: m.dict()['timestamp'] if m.timestamp else 0)
        
#     except UnidentifiedImageError:
#         raise HTTPException(status_code=400, detail="Cannot identify image file. It might be corrupted or an unsupported format.")
#     except pytesseract.TesseractNotFoundError:
#         raise HTTPException(status_code=500, detail="Tesseract is not installed or not properly configured.")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
        
#     return messages

# def fallback_parse_chat_text(text):
#     """Parse raw text into structured messages - original method as fallback"""
#     messages = []
#     lines = text.split('\n')
    
#     # WhatsApp patterns
#     # Pattern for timestamp followed by message on the same line
#     timestamp_pattern = r'(\d{1,2}:\d{2})(?:\s+|$)'
    
#     current_sender = None
#     current_message = None
#     current_timestamp = None
#     message_continuation = False
    
#     for line in lines:
#         line = line.strip()
#         if not line:
#             continue
            
#         # Check for patterns that indicate a new message
        
#         # Check for quoted message format (WhatsApp quoted replies)
#         quoted_match = re.search(r'(.+) 🔹(.+)', line)
#         if quoted_match:
#             # This is likely a quoted message reference, we can skip or handle specially
#             continue
            
#         # Check for username followed by message
#         sender_match = re.match(r'^([A-Za-z0-9_\s]+)(?:\s*[😊🙂👍🏻\u200d♂️🌮]+)?\s*(.+)$', line)
        
#         # Look for timestamp in the line
#         timestamp_match = re.search(timestamp_pattern, line)
        
#         # Special case for WhatsApp formatting
#         if ":" in line and timestamp_match:
#             ts = timestamp_match.group(1)
#             # Try to extract sender and content
#             parts = line.split(ts, 1)
#             if len(parts) > 1 and parts[0].strip():
#                 current_sender = parts[0].strip()
#                 current_message = parts[1].strip() if len(parts) > 1 else ""
#                 current_timestamp = ts
#                 message_continuation = False
                
#                 # Don't create the message yet, wait for complete content
#                 continue
        
#         # If we have a sender/timestamp but are getting continuation lines
#         elif current_sender and current_message is not None:
#             # This is likely a continuation of the previous message
#             current_message += " " + line
#             message_continuation = True
            
#             # If this line contains a timestamp, it might be the end
#             if timestamp_match and not line.startswith(timestamp_match.group(1)):
#                 messages.append(Message(
#                     sender=current_sender,
#                     content=current_message.replace(timestamp_match.group(1), "").strip(),
#                     timestamp=current_timestamp
#                 ))
#                 current_sender = None
#                 current_message = None
#                 current_timestamp = None
#                 message_continuation = False
        
#         # If we detected a new sender
#         elif sender_match and not message_continuation:
#             # If we have a previous message pending, save it
#             if current_sender and current_message:
#                 messages.append(Message(
#                     sender=current_sender,
#                     content=current_message,
#                     timestamp=current_timestamp
#                 ))
            
#             # Start a new message
#             current_sender = sender_match.group(1).strip()
#             current_message = sender_match.group(2).strip() if len(sender_match.groups()) > 1 else ""
#             current_timestamp = timestamp_match.group(1) if timestamp_match else None
#             message_continuation = False
    
#     # Don't forget to add the last message if there is one
#     if current_sender and current_message:
#         messages.append(Message(
#             sender=current_sender,
#             content=current_message,
#             timestamp=current_timestamp
#         ))
    
#     # Additional fallback logic from original function
#     # (Omitted for brevity - refer to original code for the remaining complex text parsing logic)
    
#     return messages

# def process_image(image_file, use_advanced=True):
#     """
#     Extract text from image using OCR with option to use advanced processing
#     """
#     try:
#         if use_advanced:
#             messages = advanced_ocr_process(image_file)
#             # If no messages were successfully extracted with advanced method, try fallback
#             if not messages:
#                 image = Image.open(io.BytesIO(image_file))
#                 text = pytesseract.image_to_string(image)
#                 messages = fallback_parse_chat_text(text)
#             return messages
#         else:
#             # Original simpler method
#             image = Image.open(io.BytesIO(image_file))
#             text = pytesseract.image_to_string(image)
#             messages = fallback_parse_chat_text(text)
#             return messages
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

# def merge_conversations(existing_messages, new_messages):
#     """Merge messages, handling duplicates from multiple screenshots"""
#     if not existing_messages:
#         return new_messages
        
#     # Simple deduplication logic - can be improved
#     all_messages = existing_messages.copy()
    
#     for new_msg in new_messages:
#         # Check if message is already in the conversation
#         duplicate = False
#         for existing_msg in existing_messages:
#             if (existing_msg.content == new_msg.content and 
#                 existing_msg.sender == new_msg.sender):
#                 duplicate = True
#                 break
        
#         if not duplicate:
#             all_messages.append(new_msg)
            
#     return all_messages

# @app.post("/api/upload")
# async def upload_chat_images(
#     conversation_id: Optional[str] = Form(None),
#     title: str = Form(...),
#     category: str = Form(...),
#     use_advanced_ocr: bool = Form(True),  # Default to advanced OCR
#     debug_mode: bool = Form(False),       # Generate debug images
#     files: List[UploadFile] = File(...)
# ):
#     """Upload and process chat screenshots"""
#     # Generate a new conversation ID if not provided
#     if not conversation_id:
#         conversation_id = str(uuid.uuid4())
    
#     # Get existing messages if conversation already exists
#     existing_messages = []
#     if conversation_id in CONVERSATIONS:
#         existing_messages = CONVERSATIONS[conversation_id].messages
    
#     all_messages = []
    
#     # Process each uploaded file
#     for file in files:
#         # Save file to disk
#         file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
#         with open(file_path, "wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)
        
#         # Process the image
#         with open(file_path, "rb") as f:
#             image_bytes = f.read()
        
#         if use_advanced_ocr:
#             # Use the advanced OCR processing
#             messages = advanced_ocr_process(image_bytes, debug=debug_mode)
#         else:
#             # Use the original simpler method
#             image = Image.open(io.BytesIO(image_bytes))
#             text = pytesseract.image_to_string(image)
#             print(f"Extracted text: {text}")  # Debug output
#             messages = fallback_parse_chat_text(text)
            
#         print(f"Parsed messages: {messages}")  # Debug output
        
#         # Merge with existing messages
#         all_messages = merge_conversations(all_messages, messages)
    
#     # Create or update the conversation
#     CONVERSATIONS[conversation_id] = Conversation(
#         id=conversation_id,
#         title=title,
#         category=category,
#         date_created=datetime.now().isoformat(),
#         messages=merge_conversations(existing_messages, all_messages)
#     )
    
#     return {"conversation_id": conversation_id, "message_count": len(all_messages), "advanced_ocr_used": use_advanced_ocr}

# @app.get("/api/conversations")
# async def get_conversations():
#     """Get all conversations metadata"""
#     result = []
#     for conv_id, conv in CONVERSATIONS.items():
#         result.append({
#             "id": conv_id,
#             "title": conv.title,
#             "category": conv.category,
#             "date_created": conv.date_created,
#             "message_count": len(conv.messages)
#         })
#     return result

# @app.get("/api/conversations/{conversation_id}")
# async def get_conversation(conversation_id: str):
#     """Get a specific conversation with all messages"""
#     if conversation_id not in CONVERSATIONS:
#         raise HTTPException(status_code=404, detail="Conversation not found")
    
#     return CONVERSATIONS[conversation_id]

# @app.delete("/api/conversations/{conversation_id}")
# async def delete_conversation(conversation_id: str):
#     """Delete a conversation"""
#     if conversation_id not in CONVERSATIONS:
#         raise HTTPException(status_code=404, detail="Conversation not found")
    
#     del CONVERSATIONS[conversation_id]
#     return {"status": "success"}

# @app.put("/api/conversations/{conversation_id}")
# async def update_conversation(conversation_id: str, conversation: Conversation):
#     """Update conversation metadata"""
#     if conversation_id not in CONVERSATIONS:
#         raise HTTPException(status_code=404, detail="Conversation not found")
    
#     existing_conv = CONVERSATIONS[conversation_id]
#     existing_conv.title = conversation.title
#     existing_conv.category = conversation.category
    
#     return existing_conv

# @app.get("/")
# async def root():
#     return {"message": "Welcome to the Chat Memory App API with Advanced OCR"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import base64
import io
import re
import os
import json
import shutil
from datetime import datetime
import uuid
import string
import sys
from huggingface_hub import InferenceClient

app = FastAPI(title="Memory Box")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class Message(BaseModel):
    sender: str
    content: str
    timestamp: Optional[str] = None

class Conversation(BaseModel):
    id: str
    title: str
    category: str
    date_created: str
    messages: List[Message]

# In-memory storage (replace with database in production)
CONVERSATIONS = {}
UPLOAD_DIR = "uploads"

# HuggingFace Configuration
HUGGINGFACE_API_KEY = "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"  # Replace with your actual API key
MODEL_ID = "meta-llama/Llama-4-Scout-17B-16E-Instruct"  # Visual language model 

# Initialize HuggingFace client
hf_client = InferenceClient(
    provider="together",
    api_key=HUGGINGFACE_API_KEY,
)

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

def extract_text_with_llm(image_bytes):
    """
    Extract text from image using LLM instead of OCR
    """
    try:
        # Convert image to base64
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        
        # Create prompt with the image for the LLM
        prompt = """
These images are screenshots of a chat conversation from an application like Whatsapp.

Your task is to extract all the text messages from the image **in the correct chronological order**, **in the order that the images are uploaded**.

For each message, identify and format the following:
1. **Sender's name** (Use the exact name shown in the chat. If aligned right, it's from "You"; if aligned left, it's from the other person. Their name is usually shown at the top next to their profile picture.)
2. **Timestamp** in HH:MM format (if available)
3. **Message content**

📌 **Formatting Instructions (very important):**
Format the output like this:

**Sender Name**  
HH:MM — Message 1  
HH:MM — Message 2 (if another message by same sender follows)

**Other Sender Name**  
HH:MM — Their message 1  
HH:MM — Their message 2  

🧠 Use visual layout cues:
- Messages aligned to the **right** necessarily belong to **"You"**.
- Messages aligned to the **left** necessarily belong to the **other sender**, whose name is shown at the top of the chat.
- Maintain the **exact order** in which messages appear.
- If a message has **no timestamp**, just write the message below the previous one by the same sender.
- If a message appears quoted, dont quote it

        """
        
        # Create messages for the chat completion
        messages = [
            {"role": "system", "content": "You are a helpful assistant that extracts text from images."},
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
            ]}
        ]
        
        # Call LLM API with chat_completion instead
        response = hf_client.chat_completion(
            model=MODEL_ID,
            messages=messages,
            max_tokens=1000,
            temperature=0.2
        )
        
        # Parse the LLM response into messages
        extracted_text = response.choices[0].message.content
        print(f"LLM extracted text: {extracted_text}")
        
        # Parse the formatted text into structured messages
        return parse_llm_chat_response(extracted_text)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image with LLM: {str(e)}")

def parse_llm_chat_response(text):
    """
    Parse the formatted chat text from LLM into Message objects
    """
    messages = []
    current_sender = None
    
    # Split text by lines
    lines = text.strip().split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Check if this line is just a sender name (not surrounded by ** which might be missing)
        if i < len(lines) - 1 and re.match(r'^[A-Za-z0-9\s]+$', line) and "—" in lines[i+1]:
            current_sender = line
            continue
        
        # Also check for sender format with asterisks
        sender_match = re.match(r'\*\*([^*]+)\*\*', line)
        if sender_match:
            current_sender = sender_match.group(1).strip()
            continue
            
        # Check for timestamp and message format with various dash types
        # Handle different dash characters and formats
        message_match = re.match(r'(\d{1,2}:\d{2})?\s*(?:—|-|–)?\s*(.+)', line)
        
        if message_match and current_sender:
            timestamp = message_match.group(1) if message_match.group(1) else None
            content = message_match.group(2).strip() if message_match.group(2) else ""
            
            if content:  # Only add if there's actual content
                messages.append(Message(
                    sender=current_sender,
                    content=content,
                    timestamp=timestamp
                ))
    
    # Debug print each message for troubleshooting
    for msg in messages:
        print(f"Parsed: {msg.sender} at {msg.timestamp}: {msg.content}")
        
    return messages

def merge_conversations(existing_messages, new_messages):
    """Merge messages, handling duplicates from multiple screenshots"""
    if not existing_messages:
        return new_messages
        
    # Simple deduplication logic - can be improved
    all_messages = existing_messages.copy()
    
    for new_msg in new_messages:
        # Check if message is already in the conversation
        duplicate = False
        for existing_msg in existing_messages:
            if (existing_msg.content == new_msg.content and 
                existing_msg.sender == new_msg.sender):
                duplicate = True
                break
        
        if not duplicate:
            all_messages.append(new_msg)
            
    return all_messages

@app.post("/api/upload")
async def upload_chat_images(
    conversation_id: Optional[str] = Form(None),
    title: str = Form(...),
    category: str = Form(...),
    files: List[UploadFile] = File(...)
):
    """Upload and process chat screenshots using LLM"""
    # Generate a new conversation ID if not provided
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
    
    # Get existing messages if conversation already exists
    existing_messages = []
    if conversation_id in CONVERSATIONS:
        existing_messages = CONVERSATIONS[conversation_id].messages
    
    all_messages = []
    
    # Process each uploaded file
    for file in files:
        # Save file to disk
        file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the image with LLM
        with open(file_path, "rb") as f:
            image_bytes = f.read()
        
        messages = extract_text_with_llm(image_bytes)
        print(f"Parsed messages: {messages}")  # Debug output
        
        # Merge with existing messages
        all_messages = merge_conversations(all_messages, messages)
    
    # Create or update the conversation
    CONVERSATIONS[conversation_id] = Conversation(
        id=conversation_id,
        title=title,
        category=category,
        date_created=datetime.now().isoformat(),
        messages=merge_conversations(existing_messages, all_messages)
    )
    
    return {"conversation_id": conversation_id, "message_count": len(all_messages)}

@app.get("/api/conversations")
async def get_conversations():
    """Get all conversations metadata"""
    result = []
    for conv_id, conv in CONVERSATIONS.items():
        result.append({
            "id": conv_id,
            "title": conv.title,
            "category": conv.category,
            "date_created": conv.date_created,
            "message_count": len(conv.messages)
        })
    return result

@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get a specific conversation with all messages"""
    if conversation_id not in CONVERSATIONS:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return CONVERSATIONS[conversation_id]

@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    if conversation_id not in CONVERSATIONS:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    del CONVERSATIONS[conversation_id]
    return {"status": "success"}

@app.put("/api/conversations/{conversation_id}")
async def update_conversation(conversation_id: str, conversation: Conversation):
    """Update conversation metadata"""
    if conversation_id not in CONVERSATIONS:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    existing_conv = CONVERSATIONS[conversation_id]
    existing_conv.title = conversation.title
    existing_conv.category = conversation.category
    
    return existing_conv
