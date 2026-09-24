"""
Model client for interacting with language models.
"""

import os
import time
from typing import Optional


class BedrockClient:
    """Client for interacting with Amazon Bedrock API."""

    def __init__(self, model_name: str, api_key: Optional[str] = None):
        """
        Initialize Bedrock client.

        Args:
            model_name: Bedrock model ID to use
            api_key: API key (if None, will try to get from environment)
        """
        self.model_name = model_name

        if api_key is None:
            api_key = os.getenv('AWS_BEARER_TOKEN_BEDROCK')
            if api_key is None:
                raise ValueError("AWS_BEARER_TOKEN_BEDROCK environment variable not set and no api_key provided")

        self.api_key = api_key
        self._setup_client()

    def _setup_client(self):
        """Setup the Bedrock client."""
        try:
            import boto3
            os.environ['AWS_BEARER_TOKEN_BEDROCK'] = self.api_key
            self.client = boto3.client('bedrock-runtime', region_name='us-east-1')
        except ImportError:
            raise ImportError("boto3 package not installed. Install with: pip install boto3")
        except Exception as e:
            raise RuntimeError(f"Failed to setup Bedrock client: {e}")

    def generate_content(self, prompt: str, timeout: int = 120, **kwargs) -> str:
        """
        Generate content using the Bedrock model.

        Args:
            prompt: The input prompt
            timeout: Maximum time to wait for response in seconds (default: 120)
            **kwargs: Additional parameters for generation

        Returns:
            Generated content as string
        """
        try:
            start_time = time.time()

            response = self.client.converse(
                modelId=self.model_name,
                messages=[
                    {'role': 'user', 'content': [{'text': prompt}]}
                ],
                inferenceConfig={
                    'temperature': 0.5,
                    'maxTokens': 6400,
                },
            )

            elapsed_time = time.time() - start_time

            program_text = ''.join(
                block['text']
                for block in response['output']['message']['content']
                if 'text' in block
            ).strip()

            if not program_text:
                raise RuntimeError("Empty response from Bedrock API")

            return program_text

        except Exception as e:
            elapsed_time = time.time() - start_time if 'start_time' in locals() else 0
            print(f"  API call failed after {elapsed_time:.2f}s: {str(e)}")
            raise RuntimeError(f"Failed to generate content: {e}")
