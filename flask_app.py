"""
Flask version of the AI Stylist backend
"""

import os
import tempfile
import logging
import json
import numpy as np
from flask import Flask, request, jsonify, render_template
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Outfit, ClothingItem, Recommendation
from detection_service import DetectionService
from color_service import ColorService
from ai_service import AIService
from search_service import SearchService
from evaluation_metrics import compute_yolo_metrics, compute_kmeans_metrics, save_metrics

# Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "demo-secret-key")

# Services
detection_service = DetectionService()
color_service = ColorService()
ai_service = AIService()
search_service = SearchService()

# --- Routes ---

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_image():
    db = SessionLocal()
    temp_path = None
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "detail": "No file provided"}), 400

        file = request.files['file']
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()

        if not username or not email:
            return jsonify({"success": False, "detail": "Username and email are required"}), 400

        # Find or create user
        user = db.query(User).filter((User.username == username) | (User.email == email)).first()
        if user:
            if user.username != username:
                user.username = username
            if user.email != email:
                user.email = email
            db.commit()
            user_id = user.user_id
        else:
            new_user = User(username=username, email=email)
            db.add(new_user)
            db.flush()
            user_id = new_user.user_id

        # Save temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        file.save(temp_file.name)
        temp_path = temp_file.name
        temp_file.close()

        logger.info(f"Processing image: {temp_path}")

        detected_items = detection_service.detect_items(temp_path)
        rgb_values = color_service.get_dominant_colors(temp_path)

        outfit = Outfit(user_id=user_id, photo_url=temp_path)
        db.add(outfit)
        db.flush()

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

        try:
            os.unlink(temp_path)
        except:
            pass

        return jsonify({
            "success": True,
            "outfit_id": outfit.outfit_id,
            "detected_items": detected_items,
            "dominant_colors": rgb_values
        })

    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        if temp_path:
            try: os.unlink(temp_path)
            except: pass
        db.rollback()
        return jsonify({"success": False, "detail": str(e)}), 500
    finally:
        db.close()


@app.route("/generate-suggestions", methods=["POST"])
def generate_suggestions():
    """Single, clean version with metrics and LLM integration"""
    db = SessionLocal()
    try:
        outfit_id = request.form.get('outfit_id', type=int)
        if not outfit_id:
            return jsonify({"success": False, "detail": "Missing outfit_id"}), 400

        outfit = db.query(Outfit).filter(Outfit.outfit_id == outfit_id).first()
        if not outfit:
            return jsonify({"success": False, "detail": "Outfit not found"}), 404

        clothing_items = db.query(ClothingItem).filter(ClothingItem.outfit_id == outfit_id).all()

        detected_items = []
        rgb_values = []
        y_true_labels = []

        for item in clothing_items:
            detected_items.append({'type': item.type, 'confidence': 0.95})
            rgb_values.append(item.color_palette if item.color_palette else [128, 128, 128])
            y_true_labels.append(item.type)

        # AI suggestion
        ai_suggestion = ai_service.get_styling_suggestions(detected_items, rgb_values)
        similar_images = search_service.find_similar_outfits(detected_items, rgb_values)

        # Save recommendation
        recommendation = Recommendation(
            outfit_id=outfit_id,
            suggestion=ai_suggestion,
            reasoning="AI-generated styling advice"
        )
        db.add(recommendation)
        db.commit()

        # --- Metrics ---
        y_pred_labels = [item['type'] for item in detected_items]
        precision, recall = compute_yolo_metrics(y_true_labels, y_pred_labels)
        kmeans_labels = np.array([0]*len(rgb_values))  # replace with real cluster labels
        silhouette = compute_kmeans_metrics(np.array(rgb_values), kmeans_labels)
        metrics_dict = {"yolo_precision": precision, "yolo_recall": recall, "kmeans_silhouette": silhouette}
        save_metrics(metrics_dict)

        return jsonify({
            "success": True,
            "ai_suggestions": ai_suggestion,
            "similar_images": similar_images,
            "recommendation_id": recommendation.rec_id,
            "metrics": metrics_dict
        })

    except Exception as e:
        logger.error(f"Error generating suggestions: {str(e)}")
        db.rollback()
        return jsonify({"success": False, "detail": str(e)}), 500
    finally:
        db.close()


@app.route("/results/<int:outfit_id>")
def results_page(outfit_id):
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


@app.route("/metrics", methods=["GET"])
def get_metrics():
    try:
        with open("metrics/metrics.json") as f:
            data = json.load(f)
        return jsonify({"success": True, "metrics": data})
    except:
        return jsonify({"success": False, "detail": "No metrics found"}), 404


@app.route("/health")
def health_check():
    return jsonify({"status": "healthy", "message": "AI Stylist Backend is running"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
