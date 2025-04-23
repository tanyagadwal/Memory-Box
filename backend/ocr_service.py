import os
import base64
import json
from typing import List, Dict, Any, Optional
from google.cloud import vision
from google.cloud.vision_v1 import types
import numpy as np
import cv2
from PIL import Image
import io
import uuid
import pytesseract
import re
from datetime import datetime
from functools import reduce
import logging

# For Google Cloud Vision integration
try:
    from google.cloud import vision
    
    # Check for credentials in common locations if not set in environment
    credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    
    # Look in project directories if not set
    if not credentials_path or not os.path.exists(credentials_path):
        possible_paths = [
            # Current directory
            os.path.join(os.getcwd(), "mimetic-card-457310-n5-890f77604726.json"),
            # Parent directory
            os.path.join(os.path.dirname(os.getcwd()), "mimetic-card-457310-n5-890f77604726.json"),
            # Memory-Box directory
            os.path.join(os.path.dirname(os.getcwd()), "Memory-Box", "mimetic-card-457310-n5-890f77604726.json"),
            # Specific path for this project
            "/home/madhav/Desktop/memvol/Memory-Box/mimetic-card-457310-n5-890f77604726.json"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path
                credentials_path = path
                logging.info(f"Found credentials at: {path}")
                break
    
    VISION_API_AVAILABLE = credentials_path is not None and os.path.exists(credentials_path)
    if VISION_API_AVAILABLE:
        logging.info(f"Google Vision API enabled with credentials at: {credentials_path}")
    else:
        logging.warning("Google Vision API not available - credentials not found")
except ImportError:
    VISION_API_AVAILABLE = False
    logging.warning("Google Vision API not available - package not installed")

# Configure logging
logging.basicConfig(level=logging.INFO)

class OCRService:
    """
    Service for handling OCR operations using Google Cloud Vision API.
    """
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        Initialize the OCR service with Google Cloud credentials.
        
        Args:
            credentials_path: Path to Google Cloud credentials JSON file
        """
        if credentials_path and os.path.exists(credentials_path):
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
        try:
            self.client = vision.ImageAnnotatorClient()
        except Exception as e:
            print(f"Error initializing Vision client: {str(e)}")
            self.client = None
    
    def extract_text_from_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Extract text from an image using Google Cloud Vision API.
        
        Args:
            image_bytes: Binary image data
            
        Returns:
            Dict containing extracted text and metadata
        """
        if not self.client:
            return {"error": "Vision client not initialized"}
        
        try:
            image = vision.Image(content=image_bytes)
            response = self.client.document_text_detection(image=image)
            
            if response.error.message:
                return {
                    "success": False,
                    "error": response.error.message
                }
            
            full_text = response.full_text_annotation.text
            
            # Extract blocks, paragraphs, and words with their bounding boxes
            document = response.full_text_annotation
            blocks = []
            
            for page in document.pages:
                for block in page.blocks:
                    block_text = ""
                    paragraphs = []
                    
                    for paragraph in block.paragraphs:
                        para_text = ""
                        words = []
                        
                        for word in paragraph.words:
                            word_text = ''.join([symbol.text for symbol in word.symbols])
                            word_info = {
                                "text": word_text,
                                "confidence": word.confidence,
                                "bounds": self._get_bounding_box(word.bounding_box)
                            }
                            words.append(word_info)
                            para_text += word_text + " "
                        
                        para_info = {
                            "text": para_text.strip(),
                            "confidence": paragraph.confidence,
                            "bounds": self._get_bounding_box(paragraph.bounding_box),
                            "words": words
                        }
                        paragraphs.append(para_info)
                        block_text += para_text + "\n"
                    
                    block_info = {
                        "text": block_text.strip(),
                        "confidence": block.confidence,
                        "bounds": self._get_bounding_box(block.bounding_box),
                        "paragraphs": paragraphs
                    }
                    blocks.append(block_info)
            
            # Return structured result
            return {
                "success": True,
                "text": full_text,
                "locale": response.full_text_annotation.pages[0].property.detected_languages[0].language_code if response.full_text_annotation.pages and response.full_text_annotation.pages[0].property.detected_languages else None,
                "blocks": blocks
            }
            
        except Exception as e:
            print(f"Error in OCR processing: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_chat_screenshot(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Process a chat screenshot to extract conversation data.
        
        Args:
            image_bytes: Binary image data
            
        Returns:
            Dict containing structured chat data
        """
        # First, get the raw OCR results
        ocr_result = self.extract_text_from_image(image_bytes)
        
        if not ocr_result.get("success", False):
            return ocr_result
        
        try:
            # Process the OCR results to extract chat messages
            # This is a simplified implementation - a production system would use
            # more sophisticated NLP and pattern recognition
            
            full_text = ocr_result["text"]
            messages = []
            
            # Simplified parsing logic - real implementation would be more robust
            lines = full_text.split('\n')
            current_message = None
            
            for line in lines:
                # Try to detect if this is a new message (simplified heuristic)
                # Real implementation would use ML/pattern recognition for this
                if ':' in line and not line.strip().startswith('-'):
                    # If we already have a message in progress, save it
                    if current_message:
                        messages.append(current_message)
                    
                    # Start a new message
                    parts = line.split(':', 1)
                    sender = parts[0].strip()
                    content = parts[1].strip() if len(parts) > 1 else ""
                    
                    # Extract timestamp if present (simplified)
                    timestamp = None
                    if '[' in sender and ']' in sender:
                        try:
                            timestamp_part = sender[sender.find('['):sender.find(']')+1]
                            sender = sender.replace(timestamp_part, '').strip()
                            timestamp = timestamp_part[1:-1]  # Remove the brackets
                        except:
                            pass
                    
                    current_message = {
                        "sender": sender,
                        "timestamp": timestamp,
                        "content": content
                    }
                elif current_message:
                    # Continue the current message
                    current_message["content"] += "\n" + line
            
            # Don't forget the last message
            if current_message:
                messages.append(current_message)
            
            # Return the structured chat data
            return {
                "success": True,
                "messages": messages,
                "raw_text": full_text,
                "metadata": {
                    "message_count": len(messages),
                    "locale": ocr_result.get("locale")
                }
            }
            
        except Exception as e:
            print(f"Error processing chat screenshot: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "raw_ocr_result": ocr_result
            }
    
    def _get_bounding_box(self, bounding_box) -> List[Dict[str, int]]:
        """Helper method to convert bounding box to a list of coordinates"""
        return [
            {"x": vertex.x, "y": vertex.y}
            for vertex in bounding_box.vertices
        ]


# Simple test function
def test_ocr_service():
    """Test the OCR service with a sample image"""
    service = OCRService()
    
    # Load a test image
    with open("test_image.jpg", "rb") as image_file:
        image_bytes = image_file.read()
    
    result = service.process_chat_screenshot(image_bytes)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    test_ocr_service()

# Constants for chat region detection
LEFT_SIDEBAR_THRESHOLD = 0.30  # Assume left 30% of image could be sidebar
RIGHT_CONTENT_START = 0.25     # Start looking for content from 25% of width
MIN_BUBBLE_WIDTH = 100         # Minimum width of a chat bubble in pixels
MIN_BUBBLE_HEIGHT = 30         # Minimum height of a chat bubble in pixels

def extract_chat_region(image_data):
    """
    Detects and crops the main chat region from a messaging app screenshot.
    Ignores sidebars and headers to focus only on the conversation area.
    
    Args:
        image_data: Bytes or numpy array of the image
        
    Returns:
        Cropped image focusing only on the chat region
    """
    # Convert image bytes to numpy array if needed
    if isinstance(image_data, bytes):
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    else:
        image = image_data
    
    height, width = image.shape[:2]
    
    # Convert to grayscale for easier processing
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply threshold to highlight potential chat regions
    _, thresh = cv2.threshold(gray, 230, 255, cv2.THRESH_BINARY_INV)
    
    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Analyze contours to find the main chat area
    # Filter out small contours and those in the sidebar region
    sidebar_width = int(width * LEFT_SIDEBAR_THRESHOLD)
    potential_chat_contours = []
    
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        area = w * h
        
        # Skip small contours
        if w < MIN_BUBBLE_WIDTH or h < MIN_BUBBLE_HEIGHT:
            continue
            
        # Skip contours that are entirely in the sidebar area
        if x < sidebar_width and x + w < sidebar_width:
            continue
            
        # Contours that are in the main content area
        if x > width * RIGHT_CONTENT_START:
            potential_chat_contours.append((x, y, w, h, area))
    
    if not potential_chat_contours:
        # If no suitable contours found, make a guess based on layout
        # Assume chat region starts after sidebar and takes up most of the width
        chat_x = int(width * RIGHT_CONTENT_START)
        chat_width = width - chat_x
        chat_height = int(height * 0.85)  # Exclude possible headers
        chat_y = int(height * 0.1)  # Start below potential header
        
        return image[chat_y:chat_y+chat_height, chat_x:chat_x+chat_width]
    
    # Find the largest contiguous region
    potential_chat_contours.sort(key=lambda c: c[4], reverse=True)
    
    # Take the largest area as the chat region
    x, y, w, h, _ = potential_chat_contours[0]
    
    # Add some padding
    padding = 10
    x = max(0, x - padding)
    y = max(0, y - padding)
    w = min(width - x, w + 2 * padding)
    h = min(height - y, h + 2 * padding)
    
    chat_region = image[y:y+h, x:x+w]
    return chat_region

def detect_chat_bubbles(image_bytes, client=None):
    """
    Detect chat bubbles in an image using Google Cloud Vision API.
    
    Args:
        image_bytes (bytes): The image data in bytes
        client: A Google Cloud Vision API client instance
        
    Returns:
        list: A list of dictionaries containing message data
    """
    if client is None and VISION_API_AVAILABLE:
        client = vision.ImageAnnotatorClient()
    elif client is None:
        logging.error("No Vision API client provided and credentials not available")
        return []
        
    try:
        image = vision.Image(content=image_bytes)
        
        # Detect text
        response = client.text_detection(image=image)
        if response.error.message:
            logging.error(f"Error from Vision API: {response.error.message}")
            return []
            
        # Get the full text annotation
        document = response.full_text_annotation
        
        # Process text annotations to extract messages
        all_text = document.text
        
        # Use the extracted text to identify messages
        messages = []
        
        # Process blocks of text
        for page in document.pages:
            for block in page.blocks:
                block_text = ""
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        word_text = ''.join([symbol.text for symbol in word.symbols])
                        block_text += word_text + " "
                
                # Try to identify if this block contains a message
                block_text = block_text.strip()
                if not block_text:
                    continue
                    
                # Simple heuristic: check if the block looks like a message
                # Look for patterns like "Name: Message" or timestamps
                sender_match = re.search(r'^([A-Za-z0-9_]+):', block_text)
                time_match = re.search(r'(\d{1,2}:\d{2}(?:\s?[AP]M)?)', block_text)
                
                if sender_match:
                    sender = sender_match.group(1)
                    # Extract message content (everything after the sender)
                    text = block_text[sender_match.end():].strip()
                    
                    # Extract timestamp if present
                    timestamp = None
                    if time_match:
                        timestamp = time_match.group(1)
                        # Remove timestamp from message if it's in the text
                        text = text.replace(timestamp, "").strip()
                    
                    messages.append({
                        "sender": sender,
                        "text": text,
                        "timestamp": timestamp
                    })
        
        # If structured parsing failed, fall back to simpler text processing
        if not messages and all_text:
            messages = extract_text_messages(all_text)
            
        return messages
            
    except Exception as e:
        logging.error(f"Error in detect_chat_bubbles: {str(e)}")
        return []

def extract_messages_from_image(image_bytes):
    """
    Extract chat messages from an image.
    
    Args:
        image_bytes (bytes): The image data in bytes
        
    Returns:
        list: A list of dictionaries containing message data
    """
    try:
        if VISION_API_AVAILABLE:
            logging.info("Using Google Cloud Vision API for OCR")
            client = vision.ImageAnnotatorClient()
            return detect_chat_bubbles(image_bytes, client)
        else:
            logging.info("Vision API not available, falling back to Tesseract OCR")
            # Use Tesseract OCR as fallback
            image = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(image)
            return extract_text_messages(text)
    except Exception as e:
        logging.error(f"Error extracting messages from image: {str(e)}")
        return []

def extract_text_messages(text):
    """
    Extract structured messages from plain text.
    
    Args:
        text (str): The text to extract messages from
        
    Returns:
        list: A list of dictionaries containing message data
    """
    if not text:
        return []
        
    messages = []
    current_sender = None
    current_text = []
    time_pattern = r'(\d{1,2}:\d{2}(?:\s?[AP]M)?)'
    sender_pattern = r'^([A-Za-z0-9_]+):'
    
    # Process the text line by line
    lines = text.split('\n')
    
    for line in lines:
        # Check if this line starts a new message
        sender_match = re.search(sender_pattern, line)
        
        if sender_match:
            # If we were building a previous message, save it
            if current_sender and current_text:
                # Extract timestamp from the text if present
                time_match = re.search(time_pattern, ' '.join(current_text))
                timestamp = time_match.group(1) if time_match else None
                
                # Remove timestamp from message text if found
                message_text = ' '.join(current_text)
                if timestamp:
                    message_text = message_text.replace(timestamp, '').strip()
                
                messages.append({
                    'sender': current_sender,
                    'text': message_text,
                    'timestamp': timestamp
                })
            
            # Start a new message
            current_sender = sender_match.group(1)
            current_text = [line[sender_match.end():].strip()]
        else:
            # Continue with the current message
            if current_sender:  # Ensure we have a current message
                current_text.append(line.strip())
    
    # Don't forget the last message
    if current_sender and current_text:
        # Extract timestamp from the text if present
        time_match = re.search(time_pattern, ' '.join(current_text))
        timestamp = time_match.group(1) if time_match else None
        
        # Remove timestamp from message text if found
        message_text = ' '.join(current_text)
        if timestamp:
            message_text = message_text.replace(timestamp, '').strip()
        
        messages.append({
            'sender': current_sender,
            'text': message_text,
            'timestamp': timestamp
        })
    
    return messages

def verify_vision_api_credentials():
    """
    Verify that the Google Cloud Vision API credentials are properly configured.
    
    Returns:
        bool: True if credentials are valid and API is accessible, False otherwise
    """
    if not VISION_API_AVAILABLE:
        logging.warning("Vision API is not available. Check your credentials.")
        return False
        
    try:
        # Create a client and try a simple operation
        client = vision.ImageAnnotatorClient()
        
        # Create a tiny test image (1x1 pixel) to minimize data transfer
        tiny_image = Image.new('RGB', (1, 1), color='white')
        img_byte_arr = io.BytesIO()
        tiny_image.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
        
        # Try to analyze the image
        image = vision.Image(content=img_bytes)
        response = client.label_detection(image=image)
        
        if response.error.message:
            logging.error(f"Error from Vision API: {response.error.message}")
            return False
            
        logging.info("Vision API credentials verified successfully")
        return True
    except Exception as e:
        logging.error(f"Error verifying Vision API credentials: {str(e)}")
        return False

# Export these functions for use in other modules
__all__ = [
    'OCRService', 
    'extract_chat_region', 
    'detect_chat_bubbles', 
    'extract_messages_from_image',
    'VISION_API_AVAILABLE',
    'verify_vision_api_credentials'
] 