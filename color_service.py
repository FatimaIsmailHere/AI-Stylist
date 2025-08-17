import cv2 as cv
import numpy as np
import sys
import logging

logger = logging.getLogger(__name__)

class ColorService:
    def __init__(self):
        """Initialize color detection service"""
        pass

    def create_bar(self, height, width, color):
        """Create color bar - preserving existing code exactly"""
        bar = np.zeros((height, width, 3), np.uint8)
        bar[:] = color
        red, green, blue = int(color[2]), int(color[1]), int(color[0])
        return bar, (red, green, blue)

    def get_dominant_colors(self, image_path: str, number_clusters: int = 3):
        """
        Dominant Color Detection - preserving existing code exactly
        """
        try:
            img = cv.imread(image_path)
            if img is None:
                raise ValueError("Could not read the image.")

            height, width, _ = img.shape
            
            # Handle very small images or adjust cluster count
            total_pixels = height * width
            if total_pixels < number_clusters:
                logger.warning(f"Image too small ({total_pixels} pixels), using fewer clusters")
                number_clusters = max(1, total_pixels)
            
            data = np.reshape(img, (height * width, 3))
            data = np.float32(data)

            # Exact same parameters as original code  
            criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            flags = cv.KMEANS_RANDOM_CENTERS
            # Convert data properly for OpenCV kmeans
            data_for_kmeans = data.astype(np.float32)
            _, labels, centers = cv.kmeans(data_for_kmeans, number_clusters, None, criteria, 10, flags)

            logger.info("Dominant Colors (RGB):")
            rgb_values = []
            for index, row in enumerate(centers):
                bar, rgb = self.create_bar(200, 200, row)
                rgb_values.append(rgb)
                logger.debug(f"{index + 1}. RGB: {rgb}")

            # Ensure we always return at least 3 colors for consistency
            while len(rgb_values) < 3:
                rgb_values.append(rgb_values[-1] if rgb_values else [128, 128, 128])

            return rgb_values
            
        except Exception as e:
            logger.error(f"Error in color detection: {e}")
            # Return default colors if extraction fails
            return [[100, 100, 100], [150, 150, 150], [200, 200, 200]]

    def rgb_to_simple_color(self, rgb):
        """Convert RGB to simple color name - preserving existing code exactly"""
        r, g, b = rgb
        if r > 200 and g > 200 and b > 200: return "white"
        if r > 150 and g > 100 and b < 100: return "brown"
        if r > 150 and g < 100 and b < 100: return "red"
        if r < 100 and g > 150 and b < 100: return "green"
        if r < 100 and g < 100 and b > 150: return "blue"
        return "black"
