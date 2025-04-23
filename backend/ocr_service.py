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

def detect_chat_bubbles(image_data):
    """
    Detects individual chat bubbles in the image and identifies sender
    based on position (left=them, right=you)
    
    Args:
        image_data: Image containing only the chat region
        
    Returns:
        List of bubble objects with sender and text information
    """
    # First extract just the chat region
    chat_region = extract_chat_region(image_data)
    height, width = chat_region.shape[:2]
    mid_x = width / 2
    
    bubbles = []
    
    if VISION_API_AVAILABLE:
        # Use Google Vision API for more accurate text detection
        # Initialize Vision API client
        client = vision.ImageAnnotatorClient()
        
        # Convert image to format needed by Vision API
        success, encoded_image = cv2.imencode('.jpg', chat_region)
        image_content = encoded_image.tobytes()
        
        image = vision.Image(content=image_content)
        response = client.text_detection(image=image)
        texts = response.text_annotations
        
        # Skip the first element which is the entire text
        if texts:
            blocks = texts[1:]
            
            for block in blocks:
                # Get bounding box coordinates
                vertices = [(vertex.x, vertex.y) for vertex in block.bounding_poly.vertices]
                
                # Calculate center of the bounding box
                center_x = sum(x for x, _ in vertices) / 4
                
                # Determine sender based on position
                sender = "user" if center_x > mid_x else "other"
                
                bubbles.append({
                    "sender": sender,
                    "text": block.description,
                    "bounding_box": vertices
                })
    else:
        # Fallback to Tesseract OCR
        # Convert to PIL Image for Tesseract
        pil_img = Image.fromarray(cv2.cvtColor(chat_region, cv2.COLOR_BGR2RGB))
        
        # Get OCR data with bounding boxes
        ocr_data = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DICT)
        
        # Group text by lines/blocks
        n_boxes = len(ocr_data['text'])
        current_line = []
        current_line_y = None
        line_threshold = 10  # Pixels tolerance for same line
        
        for i in range(n_boxes):
            if not ocr_data['text'][i].strip():
                continue
                
            x = ocr_data['left'][i]
            y = ocr_data['top'][i]
            w = ocr_data['width'][i]
            h = ocr_data['height'][i]
            text = ocr_data['text'][i]
            
            # If this is a new line or the first item
            if current_line_y is None or abs(y - current_line_y) > line_threshold:
                # Process the previous line if it exists
                if current_line:
                    # Calculate center of the line
                    line_x = sum(item[0] for item in current_line) / len(current_line)
                    line_text = " ".join(item[4] for item in current_line)
                    sender = "user" if line_x > mid_x else "other"
                    
                    # Create bounding box list
                    bbox = []
                    for item in current_line:
                        bbox.append((item[0], item[1]))
                        bbox.append((item[0] + item[2], item[1]))
                        bbox.append((item[0] + item[2], item[1] + item[3]))
                        bbox.append((item[0], item[1] + item[3]))
                    
                    bubbles.append({
                        "sender": sender,
                        "text": line_text,
                        "bounding_box": bbox
                    })
                
                # Start a new line
                current_line = [(x, y, w, h, text)]
                current_line_y = y
            else:
                # Add to current line
                current_line.append((x, y, w, h, text))
        
        # Process the last line
        if current_line:
            line_x = sum(item[0] for item in current_line) / len(current_line)
            line_text = " ".join(item[4] for item in current_line)
            sender = "user" if line_x > mid_x else "other"
            
            # Create bounding box list
            bbox = []
            for item in current_line:
                bbox.append((item[0], item[1]))
                bbox.append((item[0] + item[2], item[1]))
                bbox.append((item[0] + item[2], item[1] + item[3]))
                bbox.append((item[0], item[1] + item[3]))
            
            bubbles.append({
                "sender": sender,
                "text": line_text,
                "bounding_box": bbox
            })
    
    # Sort bubbles by y-coordinate to maintain conversation order
    bubbles.sort(key=lambda b: b["bounding_box"][0][1])
    
    return bubbles

def extract_messages_from_image(image_data):
    """
    Main function to extract chat messages from an image
    
    Args:
        image_data: Image bytes
        
    Returns:
        List of message objects with sender, text, and timestamp
    """
    # Get chat bubbles
    bubbles = detect_chat_bubbles(image_data)
    
    # Process bubbles to extract additional info like timestamps
    messages = []
    for bubble in bubbles:
        # Try to identify timestamps within the text
        text = bubble["text"]
        timestamp = None
        
        # Look for common timestamp patterns
        time_patterns = [
            r'(\d{1,2}:\d{2}(?:\s?[AP]M)?)',  # matches "1:23 PM", "13:45"
            r'(\d{1,2}:\d{2}:\d{2})',         # matches "13:45:30"
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text)
            if match:
                timestamp = match.group(1)
                # Remove timestamp from text if found
                text = re.sub(pattern, '', text).strip()
                break
        
        messages.append({
            "sender": bubble["sender"],
            "text": text,
            "timestamp": timestamp
        })
    
    return messages 