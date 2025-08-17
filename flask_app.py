"""
Flask version of the AI Stylist backend for Gunicorn compatibility
Using your existing code logic with Flask instead of FastAPI
"""
import os
import tempfile
import shutil
import json
import logging
from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from sqlalchemy.orm import Session
from database import get_db, SessionLocal
from models import User, Outfit, ClothingItem, Recommendation
from detection_service import DetectionService
from color_service import ColorService
from ai_service import AIService
from search_service import SearchService

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "demo-secret-key")

# Initialize services
detection_service = DetectionService()
color_service = ColorService()
ai_service = AIService()
search_service = SearchService()

@app.route("/")
def home():
    """Serve the main frontend page"""
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_image():
    """
    Upload and process an image using the existing YOLO detection code
    """
    db = SessionLocal()
    temp_path = None
    
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({"success": False, "detail": "No file provided"}), 400
        
        file = request.files['file']
        user_id = request.form.get('user_id', 1, type=int)
        
        if file.filename == '':
            return jsonify({"success": False, "detail": "No file selected"}), 400
        
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            return jsonify({"success": False, "detail": "File must be an image"}), 400
        
        # Save uploaded file temporarily
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        file.save(temp_file.name)
        temp_path = temp_file.name
        temp_file.close()
        
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
        
        return jsonify({
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
            if temp_path:
                os.unlink(temp_path)
        except:
            pass
        db.rollback()
        return jsonify({"success": False, "detail": f"Error processing image: {str(e)}"}), 500
    finally:
        db.close()

@app.route("/correct-detection", methods=["POST"])
def correct_detection():
    """
    Allow manual correction of detected items (preserving existing workflow)
    """
    db = SessionLocal()
    try:
        outfit_id = request.form.get('outfit_id', type=int)
        item_index = request.form.get('item_index', type=int)
        corrected_type = request.form.get('corrected_type')
        
        if not all([outfit_id, item_index is not None, corrected_type]):
            return jsonify({"success": False, "detail": "Missing required parameters"}), 400
        
        # Get the outfit and its items
        outfit = db.query(Outfit).filter(Outfit.outfit_id == outfit_id).first()
        if not outfit:
            return jsonify({"success": False, "detail": "Outfit not found"}), 404
        
        clothing_items = db.query(ClothingItem).filter(ClothingItem.outfit_id == outfit_id).all()
        
        if item_index >= len(clothing_items):
            return jsonify({"success": False, "detail": "Invalid item index"}), 400
        
        # Update the item type
        clothing_items[item_index].type = corrected_type
        db.commit()
        
        return jsonify({
            "success": True,
            "message": f"Item {item_index} updated to {corrected_type}"
        })
        
    except Exception as e:
        logger.error(f"Error correcting detection: {str(e)}")
        db.rollback()
        return jsonify({"success": False, "detail": f"Error correcting detection: {str(e)}"}), 500
    finally:
        db.close()

@app.route("/generate-suggestions", methods=["POST"])
def generate_suggestions():
    """
    Generate AI styling suggestions and similar outfit images using existing code
    """
    db = SessionLocal()
    try:
        outfit_id = request.form.get('outfit_id', type=int)
        
        if not outfit_id:
            return jsonify({"success": False, "detail": "Missing outfit_id"}), 400
        
        # Get outfit and items from database
        outfit = db.query(Outfit).filter(Outfit.outfit_id == outfit_id).first()
        if not outfit:
            return jsonify({"success": False, "detail": "Outfit not found"}), 404
        
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
        
        return jsonify({
            "success": True,
            "ai_suggestions": ai_suggestion,
            "similar_images": similar_images,
            "recommendation_id": recommendation.rec_id
        })
        
    except Exception as e:
        logger.error(f"Error generating suggestions: {str(e)}")
        db.rollback()
        return jsonify({"success": False, "detail": f"Error generating suggestions: {str(e)}"}), 500
    finally:
        db.close()

@app.route("/results/<int:outfit_id>")
def results_page(outfit_id):
    """Serve the results page with outfit analysis"""
    db = SessionLocal()
    try:
        outfit = db.query(Outfit).filter(Outfit.outfit_id == outfit_id).first()
        if not outfit:
            return "Outfit not found", 404
        
        clothing_items = db.query(ClothingItem).filter(ClothingItem.outfit_id == outfit_id).all()
        recommendations = db.query(Recommendation).filter(Recommendation.outfit_id == outfit_id).all()
        
        return render_template("results.html", 
                             outfit=outfit,
                             clothing_items=clothing_items,
                             recommendations=recommendations)
    finally:
        db.close()

@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "AI Stylist Backend is running"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)