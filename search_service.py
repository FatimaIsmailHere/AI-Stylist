import logging

logger = logging.getLogger(__name__)

class SearchService:
    def __init__(self):
        """Initialize search service - preserving existing code exactly"""
        try:
            # Import DDGS here to handle missing dependency gracefully
            from ddgs import DDGS
            # Initialize the DDGS search object - exact same as original
            self.search = DDGS()
        except ImportError as e:
            logger.error(f"DuckDuckGo search not available: {e}")
            self.search = None

    def rgb_to_simple_color(self, rgb):
        """Convert RGB to simple color name - exact same function as original"""
        r, g, b = rgb
        if r > 200 and g > 200 and b > 200: return "white"
        if r > 150 and g > 100 and b < 100: return "brown"
        if r > 150 and g < 100 and b < 100: return "red"
        if r < 100 and g > 150 and b < 100: return "green"
        if r < 100 and g < 100 and b > 150: return "blue"
        return "black"

    def find_similar_outfits(self, detected_items, rgb_values):
        """
        Find similar outfit images - preserving existing code exactly
        """
        if self.search is None:
            logger.warning("Search service not available, returning mock results")
            # Return mock results when search is not available
            mock_results = []
            for item, color in zip(detected_items, rgb_values):
                color_name = self.rgb_to_simple_color(color)
                query = f"{color_name} {item['type']}"
                mock_results.append({
                    'query': query,
                    'images': [
                        {
                            'url': 'https://via.placeholder.com/300x400?text=Similar+Outfit+1',
                            'title': f'Similar {query} style 1',
                            'source': 'Example Fashion Site'
                        },
                        {
                            'url': 'https://via.placeholder.com/300x400?text=Similar+Outfit+2',
                            'title': f'Similar {query} style 2',
                            'source': 'Example Fashion Site'
                        }
                    ]
                })
            return mock_results
        
        try:
            all_results = []
            
            # Iterate over items and fetch top 3 images - exact same logic as original
            for item, color in zip(detected_items, rgb_values):
                color_name = self.rgb_to_simple_color(color)
                query = f"{color_name} {item['type']}"
                logger.info(f"Searching for: '{query}'")

                item_results = {
                    'query': query,
                    'images': []
                }

                try:
                    # DDGS returns a generator - exact same as original
                    results = self.search.images(query, safesearch='Moderate', region='US')
                    for i, r in enumerate(results):
                        if i >= 3:  # limit to top 3 - exact same as original
                            break
                        item_results['images'].append({
                            'url': r['image'],
                            'title': r.get('title', ''),
                            'source': r.get('source', '')
                        })
                        
                except Exception as search_error:
                    logger.warning(f"Search failed for query '{query}': {search_error}")
                    # Continue with other items even if one search fails
                
                all_results.append(item_results)
            
            return all_results
            
        except Exception as e:
            logger.error(f"Error in image search: {e}")
            raise
