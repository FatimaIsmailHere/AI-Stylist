import os
import tempfile
import shutil
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from database import get_db
from models import User, Outfit, ClothingItem, Recommendation
from detection_service import DetectionService
from color_service import ColorService
from ai_service import AIService
from search_service import SearchService
import json
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="AI Stylist Backend", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize services
detection_service = DetectionService()
color_service = ColorService()
ai_service = AIService()
search_service = SearchService()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main frontend page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    user_id: int = Form(default=1),  # Default user for demo
    db: Session = Depends(get_db)
):
    """
    Upload and process an image using the existing YOLO detection code
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_path = temp_file.name
        
        logger.info(f"Processing image: {temp_path}")
        
        # Run YOLO detection using existing code
        detected_items = detection_service.detect_items(temp_path)
        
        # Extract dominant colors using existing code
        rgb_values = color_service.get_dominant_colors(temp_path)
        
        # Save to database
        outfit = Outfit(user_id=user_id, photo_url=temp_path)
        db.add(outfit)
        db.flush()  # Get the outfit_id
        
        # Save detected items to database
        for i, item in enumerate(detected_items):
            color_palette = rgb_values[i] if i < len(rgb_values) else None
            clothing_item = ClothingItem(
                outfit_id=outfit.outfit_id,
                type=item['type'],
                color_palette=color_palette,
                bounding_box=item['bbox']
            )
            db.add(clothing_item)
        
        db.commit()
        
        # Clean up temp file
        try:
            os.unlink(temp_path)
        except:
            pass
        
        return JSONResponse({
            "success": True,
            "outfit_id": outfit.outfit_id,
            "detected_items": detected_items,
            "dominant_colors": rgb_values,
            "message": "Image processed successfully. Please review detections."
        })
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        # Clean up temp file if it exists
        try:
            if 'temp_path' in locals() and temp_path:
                os.unlink(temp_path)
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/correct-detection")
async def correct_detection(
    outfit_id: int = Form(...),
    item_index: int = Form(...),
    corrected_type: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Allow manual correction of detected items (preserving existing workflow)
    """
    try:
        # Get the outfit and its items
        outfit = db.query(Outfit).filter(Outfit.outfit_id == outfit_id).first()
        if not outfit:
            raise HTTPException(status_code=404, detail="Outfit not found")
        
        clothing_items = db.query(ClothingItem).filter(ClothingItem.outfit_id == outfit_id).all()
        
        if item_index >= len(clothing_items):
            raise HTTPException(status_code=400, detail="Invalid item index")
        
        # Update the item type
        clothing_items[item_index].type = corrected_type
        db.commit()
        
        return JSONResponse({
            "success": True,
            "message": f"Item {item_index} updated to {corrected_type}"
        })
        
    except Exception as e:
        logger.error(f"Error correcting detection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error correcting detection: {str(e)}")

@app.post("/generate-suggestions")
async def generate_suggestions(
    outfit_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """
    Generate AI styling suggestions and similar outfit images using existing code
    """
    try:
        # Get outfit and items from database
        outfit = db.query(Outfit).filter(Outfit.outfit_id == outfit_id).first()
        if not outfit:
            raise HTTPException(status_code=404, detail="Outfit not found")
        
        clothing_items = db.query(ClothingItem).filter(ClothingItem.outfit_id == outfit_id).all()
        
        # Prepare data for existing AI service code
        detected_items = []
        rgb_values = []
        
        for item in clothing_items:
            detected_items.append({
                'type': item.type,
                'confidence': 0.95  # Default since we don't store confidence after correction
            })
            rgb_values.append(item.color_palette if item.color_palette else [128, 128, 128])
        
        # Generate AI styling suggestions using existing code
        ai_suggestion = ai_service.get_styling_suggestions(detected_items, rgb_values)
        
        # Get similar outfit images using existing search code
        similar_images = search_service.find_similar_outfits(detected_items, rgb_values)
        
        # Save recommendation to database
        recommendation = Recommendation(
            outfit_id=outfit_id,
            suggestion=ai_suggestion,
            reasoning="AI-generated styling advice based on detected items and colors"
        )
        db.add(recommendation)
        db.commit()
        
        return JSONResponse({
            "success": True,
            "ai_suggestions": ai_suggestion,
            "similar_images": similar_images,
            "recommendation_id": recommendation.rec_id
        })
        
    except Exception as e:
        logger.error(f"Error generating suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating suggestions: {str(e)}")

@app.get("/results/{outfit_id}", response_class=HTMLResponse)
async def results_page(request: Request, outfit_id: int, db: Session = Depends(get_db)):
    """Serve the results page with outfit analysis"""
    outfit = db.query(Outfit).filter(Outfit.outfit_id == outfit_id).first()
    if not outfit:
        raise HTTPException(status_code=404, detail="Outfit not found")
    
    clothing_items = db.query(ClothingItem).filter(ClothingItem.outfit_id == outfit_id).all()
    recommendations = db.query(Recommendation).filter(Recommendation.outfit_id == outfit_id).all()
    
    return templates.TemplateResponse("results.html", {
        "request": request,
        "outfit": outfit,
        "clothing_items": clothing_items,
        "recommendations": recommendations
    })

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "AI Stylist Backend is running"}

# Import database dependency
from fastapi import Depends
