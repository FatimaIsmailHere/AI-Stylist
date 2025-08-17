from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        """Initialize AI service with Ollama client - preserving existing code exactly"""
        # Exact same client initialization as original code
        self.client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama"
        )

    def get_styling_suggestions(self, detected_items, rgb_values):
        """
        Get AI styling suggestions - preserving existing code exactly
        """
        try:
            # Build outfit summary - exact same logic as original
            outfit_summary = ""
            for i, item in enumerate(detected_items):
                color = rgb_values[i] if i < len(rgb_values) else [128, 128, 128]
                outfit_summary += f"{item['type']} (dominant color: {color}), "

            outfit_summary = outfit_summary.rstrip(', ')

            # Exact same prompt as original code
            prompt = (
                f"This is an outfit with the following items and their colors: {outfit_summary}. "
                f"Rate the vibe of this outfit from 1-10, suggest accessories, and give one styling tip. "
                f"Be concise in your response."
            )

            logger.info("AI Styling Suggestions")
            
            # Get response from AI - preserving streaming logic
            response_text = self.chat_with_chatgpt(prompt)
            return response_text
            
        except Exception as e:
            logger.error(f"Error getting AI suggestions: {e}")
            raise

    def chat_with_chatgpt(self, prompt):
        """
        Chat with ChatGPT - preserving existing streaming code exactly
        """
        try:
            response_text = ""
            stream = self.client.chat.completions.create(
                model="llama3.1",
                messages=[{"role": "user", "content": prompt}],
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    response_text += content
                    logger.debug(content)
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            raise
