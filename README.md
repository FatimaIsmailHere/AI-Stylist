# AI Stylist - Computer Vision Fashion Analysis System

## Overview

AI Stylist is a FastAPI-based web application that analyzes outfit photos using computer vision and AI. The system detects clothing items, extracts dominant colors, and provides styling suggestions through a combination of YOLO object detection, color analysis, and OpenAI-compatible AI models. Users can upload outfit photos and receive comprehensive fashion analysis including detected items, color palettes, AI styling recommendations, and similar outfit suggestions from web searches.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: FastAPI with async/await support for high-performance API endpoints
- **Database**: PostgreSQL with SQLAlchemy ORM for data persistence
- **Computer Vision**: YOLO (You Only Look Once) model for real-time clothing item detection
- **Color Analysis**: OpenCV-based K-means clustering for dominant color extraction
- **AI Integration**: OpenAI-compatible client configured for local Ollama deployment

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap dark theme
- **UI Framework**: Bootstrap 5 with Font Awesome icons
- **Styling**: Responsive design with mobile-first approach
- **File Upload**: HTML5 file input with JavaScript form handling

### Service Layer Design
The application follows a service-oriented architecture with specialized components:

- **DetectionService**: Handles YOLO model initialization and clothing item detection
- **ColorService**: Manages color palette extraction using K-means clustering
- **AIService**: Interfaces with Ollama-hosted language models for styling suggestions
- **SearchService**: Provides web search functionality using DuckDuckGo for similar outfits

### Data Model Structure
- **User Management**: Simplified user system with username and email only - no passwords or authentication
- **Outfit Storage**: Photo URLs with detection timestamps and user associations
- **Clothing Items**: Detailed item records with type, color palette, and bounding box data
- **Recommendations**: AI-generated styling suggestions linked to specific outfits
- **Fashion Trends**: Seasonal trend data storage for future enhancements

### User System
The system uses a simplified approach where users are created/identified by username and email combination. No authentication or password storage is implemented - users simply provide their username and email when uploading outfit images. The system automatically creates new users or associates uploads with existing users based on these credentials.

### File Processing Pipeline
1. Image upload through FastAPI file handling
2. YOLO model inference for clothing detection
3. Color extraction using OpenCV K-means clustering
4. AI model querying for styling suggestions
5. Web search for similar outfit images
6. Database persistence of analysis results

## External Dependencies

### AI and Machine Learning
- **Ollama**: Local LLM deployment for styling suggestions (OpenAI-compatible API)
- **YOLO (Ultralytics)**: Pre-trained object detection model for clothing recognition
- **OpenCV**: Computer vision library for image processing and color analysis

### Database
- **PostgreSQL**: Primary database for persistent data storage
- **SQLAlchemy**: ORM for database operations and schema management

### Web Services
- **DuckDuckGo Search (DDGS)**: Web search API for finding similar outfit images
- **FastAPI**: Web framework with automatic API documentation

### Frontend Libraries
- **Bootstrap 5**: CSS framework with dark theme support
- **Font Awesome**: Icon library for UI elements
- **Jinja2**: Template engine for server-side rendering

### Development and Deployment
- **Uvicorn**: ASGI server for FastAPI application
- **Python Logging**: Built-in logging for debugging and monitoring
- **CORS Middleware**: Cross-origin resource sharing for API access

### File Processing
- **Pillow/PIL**: Image processing capabilities
- **NumPy**: Numerical computing for color analysis algorithms
- **Tempfile**: Temporary file handling for uploaded images

The system is designed to run locally with Ollama for AI inference, making it suitable for development environments while maintaining the flexibility to deploy with cloud-based AI services in production.
<img width="1483" height="857" alt="image" src="https://github.com/user-attachments/assets/86656673-11ee-4d77-af7b-f8b6ce2029b5" />
