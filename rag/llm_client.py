import os
import time
import requests
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMClient:
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize LLM client with API configuration.
        
        Args:
            api_key: API key for the LLM service
            model: Model name to use
        """
        # Try to get API key from different sources
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("Warning: OPENAI_API_KEY not found in environment variables")
            self.api_key = "dummy_key"  # Set a dummy key to allow initialization
        elif not (self.api_key.startswith("sk-") or self.api_key.startswith("sk-proj-")):
            print("Warning: OPENAI_API_KEY does not start with 'sk-' or 'sk-proj-'. This may indicate an invalid key format.")
            
        self.model = model
        self.api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    
    def generate_response(self, query: str, context_chunks: List[str], max_retries: int = 3) -> str:
        """
        Generate a response using the LLM with the provided context.
        
        Args:
            query: User query
            context_chunks: List of relevant context chunks
            max_retries: Maximum number of retries for rate-limited requests
            
        Returns:
            Generated response from the LLM
        """
        if self.api_key == "dummy_key":
            return "Error: OpenAI API key not configured. Please set OPENAI_API_KEY in your environment variables."
            
        # Format context chunks
        context = "\n\n".join(context_chunks)
        
        # Create the prompt
        prompt = f"""Use the following context to answer the query. If the context doesn't contain relevant information, say so.

Context:
{context}

Query: {query}

Answer:"""
        
        # Prepare the API request
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that provides accurate and concise answers based on the given context."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        for attempt in range(max_retries):
            try:
                print(f"Making API request to {self.api_base}/chat/completions (attempt {attempt + 1}/{max_retries})")
                response = requests.post(
                    f"{self.api_base}/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 401:
                    error_detail = response.json().get('error', {}).get('message', 'Unknown error')
                    print(f"Authentication error: {error_detail}")
                    return f"Error: Invalid OpenAI API key. Details: {error_detail}"
                elif response.status_code == 429:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        print(f"Rate limited. Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    error_detail = response.json().get('error', {}).get('message', 'Unknown error')
                    print(f"Rate limit error: {error_detail}")
                    return f"Error: OpenAI API rate limit exceeded. Details: {error_detail}"
                elif response.status_code != 200:
                    error_detail = response.json().get('error', {}).get('message', 'Unknown error')
                    print(f"API error (status {response.status_code}): {error_detail}")
                    return f"Error: OpenAI API request failed with status code {response.status_code}. Details: {error_detail}"
                    
                response_data = response.json()
                return response_data["choices"][0]["message"]["content"]
                
            except requests.exceptions.RequestException as e:
                error_msg = str(e)
                print(f"Request exception: {error_msg}")
                if "401" in error_msg:
                    return "Error: Invalid OpenAI API key. Please check your API key configuration."
                elif attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"Request failed. Waiting {wait_time} seconds before retry...")
                    time.sleep(wait_time)
                    continue
                return f"Error calling LLM API: {error_msg}"
        
        return "Error: Failed to get response after multiple retries"
    
    def set_model(self, model: str):
        """
        Change the model being used.
        
        Args:
            model: New model name
        """
        self.model = model 