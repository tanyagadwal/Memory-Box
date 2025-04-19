from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import uvicorn
from ocr_service import OCRService

# Initialize FastAPI app
app = FastAPI(
    title="Memory Box API",
    description="API for processing chat screenshots with OCR",
    version="1.0.0"
)

# Add CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OCR service
ocr_service = OCRService(credentials_path="/home/madhav/Downloads/mimetic-card-457310-n5-890f77604726.json")

@app.get("/")
async def root():
    return {"message": "Welcome to Memory Box API"}

@app.post("/api/ocr")
async def process_image(image: UploadFile = File(...)):
    """
    Process an image using OCR to extract chat messages
    """
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # Read the image file
        contents = await image.read()
        
        # Process the image with OCR
        result = ocr_service.process_chat_screenshot(contents)
        
        if not result.get("success", False):
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": result.get("error", "OCR processing failed")}
            )
        
        return result
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

if __name__ == "__main__":
    # Run the server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
