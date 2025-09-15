"""
Model client for interacting with language models.
"""

import os
import time
from typing import Optional


class GeminiClient:
    """Client for interacting with Google's Gemini API."""
    
    def __init__(self, model_name: str, api_key: Optional[str] = None):
        """
        Initialize Gemini client.
        
        Args:
            model_name: Name of the Gemini model to use
            api_key: API key (if None, will try to get from environment)
        """
        self.model_name = model_name
        
        # Get API key from environment or parameter
        if api_key is None:
            api_key = os.getenv('GEMINI_API_KEY')
            if api_key is None:
                raise ValueError("GEMINI_API_KEY environment variable not set and no api_key provided")
        
        self.api_key = api_key
        self._setup_client()
    
    def _setup_client(self):
        """Setup the Gemini client."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model_name)
        except ImportError:
            raise ImportError("google-generativeai package not installed. Install with: pip install google-generativeai")
        except Exception as e:
            raise RuntimeError(f"Failed to setup Gemini client: {e}")
    
    def generate_content(self, prompt: str, timeout: int = 120, **kwargs) -> str:
        """
        Generate content using the Gemini model.
        
        Args:
            prompt: The input prompt
            timeout: Maximum time to wait for response in seconds (default: 120)
            **kwargs: Additional parameters for generation
            
        Returns:
            Generated content as string
        """
        try:
            start_time = time.time()
            
            # Set generation config with timeout
            generation_config = kwargs.get('generation_config', {})
            generation_config.update({ 
                'temperature': 0.5, 
                'max_output_tokens': 6400,
            })
            kwargs['generation_config'] = generation_config
            
            response = self.client.generate_content(prompt, **kwargs)
            
            elapsed_time = time.time() - start_time

            if response.text is None:
                raise RuntimeError("Empty response from Gemini API")
                
            return response.text
            
        except Exception as e:
            elapsed_time = time.time() - start_time if 'start_time' in locals() else 0
            print(f"  API call failed after {elapsed_time:.2f}s: {str(e)}")
            raise RuntimeError(f"Failed to generate content: {e}")
