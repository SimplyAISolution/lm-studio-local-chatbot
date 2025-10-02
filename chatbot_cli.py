#!/usr/bin/env python3
"""
Simple CLI chatbot interface for LM Studio
"""

import os
import sys
from typing import List, Dict
from lm_studio_client import create_client

class ChatBot:
    def __init__(self):
        self.client = create_client()
        self.conversation_history: List[Dict[str, str]] = []
        
    def check_lm_studio_connection(self) -> bool:
        """Check if LM Studio is running and accessible"""
        if not self.client.check_connection():
            print("❌ Cannot connect to LM Studio!")
            print("Please make sure:")
            print("1. LM Studio is running")
            print("2. A model is loaded")
            print("3. Local server is started (default: http://localhost:1234)")
            return False
        return True
    
    def display_available_models(self):
        """Display available models"""
        models = self.client.get_models()
        if models:
            print("📋 Available models:")
            for i, model in enumerate(models, 1):
                print(f"  {i}. {model.get('id', 'Unknown')}")
        else:
            print("⚠️  No models found or unable to fetch models")
    
    def chat(self):
        """Main chat loop"""
        print("🤖 LM Studio Local Chatbot")
        print("=" * 40)
        
        if not self.check_lm_studio_connection():
            return
        
        self.display_available_models()
        print("\nType 'quit', 'exit', or press Ctrl+C to end the conversation")
        print("Type 'clear' to clear conversation history")
        print("Type 'models' to see available models again")
        print("-" * 40)
        
        try:
            while True:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    print("\n👋 Goodbye!")
                    break
                
                if user_input.lower() == 'clear':
                    self.conversation_history.clear()
                    print("🧹 Conversation history cleared!")
                    continue
                
                if user_input.lower() == 'models':
                    self.display_available_models()
                    continue
                
                if not user_input:
                    continue
                
                # Add user message to history
                self.conversation_history.append({"role": "user", "content": user_input})
                
                # Get response from LM Studio
                print("\n🤖 Assistant: ", end="", flush=True)
                
                try:
                    # Use streaming for real-time response
                    response_generator = self.client.chat_completion(
                        messages=self.conversation_history,
                        stream=True,
                        temperature=float(os.getenv('TEMPERATURE', 0.7)),
                        max_tokens=int(os.getenv('MAX_TOKENS', 1000))
                    )
                    
                    assistant_response = ""
                    for chunk in response_generator:
                        if isinstance(chunk, str):
                            print(chunk, end="", flush=True)
                            assistant_response += chunk
                    
                    print()  # New line after response
                    
                    # Add assistant response to history
                    if assistant_response:
                        self.conversation_history.append({
                            "role": "assistant", 
                            "content": assistant_response
                        })
                    
                except Exception as e:
                    print(f"\n❌ Error getting response: {e}")
                    # Remove the user message if we couldn't get a response
                    if self.conversation_history and self.conversation_history[-1]["role"] == "user":
                        self.conversation_history.pop()
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")

def main():
    """Main entry point"""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    chatbot = ChatBot()
    chatbot.chat()

if __name__ == "__main__":
    main()