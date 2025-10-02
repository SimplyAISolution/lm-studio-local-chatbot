import os
import json
import requests
from typing import Optional, Generator, Dict, Any, Union
from dotenv import load_dotenv

load_dotenv()

class LMStudioClient:
    """Client for connecting to LM Studio local server"""
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = base_url or os.getenv('LM_STUDIO_BASE_URL', 'http://localhost:1234/v1')
        self.api_key = api_key or os.getenv('LM_STUDIO_API_KEY', 'lm-studio')
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
    
    def check_connection(self) -> bool:
        """Check if LM Studio server is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/models", headers=self.headers, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def get_models(self) -> list:
        """Get list of available models from LM Studio"""
        try:
            response = requests.get(f"{self.base_url}/models", headers=self.headers)
            response.raise_for_status()
            return response.json().get('data', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching models: {e}")
            return []
    
    def chat_completion(self, 
                       messages: list, 
                       model: Optional[str] = None,
                       temperature: float = 0.7,
                       max_tokens: int = 1000,
                       stream: bool = False) -> Union[Dict[Any, Any], Generator[str, None, None]]:
        """Send chat completion request to LM Studio"""
        
        payload = {
            "model": model or os.getenv('DEFAULT_MODEL', 'local-model'),
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        try:
            if stream:
                return self._stream_chat_completion(payload)
            else:
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {e}"}
    
    def _stream_chat_completion(self, payload: dict) -> Generator[str, None, None]:
        """Stream chat completion from LM Studio"""
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=self.headers,
                stream=True
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]
                        if data != '[DONE]':
                            try:
                                chunk = json.loads(data)
                                if 'choices' in chunk and len(chunk['choices']) > 0:
                                    delta = chunk['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        yield delta['content']
                            except json.JSONDecodeError:
                                continue
        except requests.exceptions.RequestException as e:
            yield f"Error: {e}"

# Convenience function for quick usage
def create_client() -> LMStudioClient:
    """Create and return an LM Studio client instance"""
    return LMStudioClient()