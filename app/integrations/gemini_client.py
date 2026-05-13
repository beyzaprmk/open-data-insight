import os
import google.genai as genai
from typing import Dict, List, Optional, Any
import json


class GeminiClient:
    """
    Client for interacting with Google's Gemini AI API.
    Handles text analysis, image processing, and AI-powered insights.
    """

    def __init__(self):
        """Initialize Gemini client with API key and configuration."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        # Initialize the client
        self.client = genai.Client(api_key=api_key)

        # Get model configuration
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.timeout = int(os.getenv("GEMINI_TIMEOUT", "30"))

    def analyze_text(self, text: str, task: str = "analyze") -> Dict[str, Any]:
        """
        Analyze text content using Gemini AI.

        Args:
            text: Text content to analyze
            task: Type of analysis ('analyze', 'summarize', 'classify', 'extract')

        Returns:
            Dict containing analysis results
        """
        try:
            # Create task-specific prompts
            prompts = {
                "analyze": f"Analyze this text and provide insights: {text}",
                "summarize": f"Summarize this text concisely: {text}",
                "classify": f"Classify this text by topic and type: {text}",
                "extract": f"Extract key information and entities from this text: {text}"
            }

            prompt = prompts.get(task, prompts["analyze"])

            # Generate response
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )

            return {
                "success": True,
                "task": task,
                "analysis": response.text,
                "model": self.model_name
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "task": task,
                "model": self.model_name
            }

    def analyze_image_with_text(self, image_data: bytes, text_context: str = "") -> Dict[str, Any]:
        """
        Analyze image content with optional text context using Gemini Vision.

        Args:
            image_data: Raw image bytes
            text_context: Optional text description or context

        Returns:
            Dict containing image analysis results
        """
        try:
            # For vision tasks, we need gemini-pro-vision model
            from PIL import Image
            import io
            image = Image.open(io.BytesIO(image_data))

            # Create prompt
            prompt = f"Analyze this image"
            if text_context:
                prompt += f" in the context of: {text_context}"
            prompt += ". Describe what you see, identify objects, and provide insights."

            # Generate response with image
            response = self.client.models.generate_content(
                model="gemini-1.5-flash",  # Vision model
                contents=[prompt, image]
            )

            return {
                "success": True,
                "analysis": response.text,
                "model": "gemini-1.5-flash",
                "has_text_context": bool(text_context)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": "gemini-1.5-flash"
            }

    def generate_insights(self, data_summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI-powered insights from dataset summary.

        Args:
            data_summary: Dictionary containing dataset statistics and info

        Returns:
            Dict containing AI-generated insights
        """
        try:
            # Create a comprehensive prompt from data summary
            prompt = f"""
            Based on this dataset summary, provide insights and recommendations:

            Dataset Info: {json.dumps(data_summary, indent=2)}

            Please provide:
            1. Key patterns or trends in the data
            2. Data quality assessment
            3. Potential use cases or applications
            4. Recommendations for improvement
            """

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )

            return {
                "success": True,
                "insights": response.text,
                "model": self.model_name,
                "data_summary_keys": list(data_summary.keys())
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": self.model_name
            }

    def validate_api_connection(self) -> Dict[str, Any]:
        """
        Test Gemini API connection and return status.

        Returns:
            Dict containing connection test results
        """
        try:
            # Simple test prompt
            test_prompt = "Hello, please respond with 'Gemini API is working' if you can read this."

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=test_prompt
            )

            return {
                "connected": True,
                "model": self.model_name,
                "response": response.text.strip(),
                "timeout": self.timeout
            }

        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
                "model": self.model_name
            }
