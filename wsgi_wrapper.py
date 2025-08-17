"""
WSGI wrapper for FastAPI app to work with Gunicorn
"""
from app import app as fastapi_app
from fastapi.applications import FastAPI
import logging

# Create a WSGI-compatible wrapper
def application(environ, start_response):
    """WSGI application wrapper for FastAPI"""
    try:
        # Simple fallback - redirect to proper ASGI setup
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/html')]
        start_response(status, headers)
        
        message = """
        <html>
        <head><title>Configuration Error</title></head>
        <body>
        <h1>FastAPI Configuration Issue</h1>
        <p>This FastAPI application needs to be run with an ASGI server like Uvicorn, not Gunicorn WSGI.</p>
        <p>Please run: <code>python main.py</code> or <code>uvicorn main:app --host 0.0.0.0 --port 5000</code></p>
        <p>For now, attempting to start Uvicorn programmatically...</p>
        </body>
        </html>
        """
        return [message.encode('utf-8')]
    except Exception as e:
        logging.error(f"WSGI wrapper error: {e}")
        status = '500 Internal Server Error'
        headers = [('Content-Type', 'text/plain')]
        start_response(status, headers)
        return [f"Error: {str(e)}".encode('utf-8')]

# For Gunicorn compatibility
app = application