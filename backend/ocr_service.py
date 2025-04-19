import os
import base64
import json
from typing import List, Dict, Any, Optional
from google.cloud import vision
from google.cloud.vision_v1 import types

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