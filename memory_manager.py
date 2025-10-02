import os
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import hashlib
import shutil

class MemoryManager:
    """
    Memory management system for LM Studio
    Provides persistent storage for conversations, context, facts, and learning
    """
    
    def __init__(self, memory_dir: Optional[str] = None):
        self.memory_dir = Path(memory_dir) if memory_dir else Path(__file__).parent / "memory"
        self.memory_dir.mkdir(exist_ok=True)
        
        # Initialize subdirectories
        self.conversations_dir = self.memory_dir / "conversations"
        self.context_dir = self.memory_dir / "context"
        self.learning_dir = self.memory_dir / "learning"
        self.facts_dir = self.memory_dir / "facts"
        
        for dir_path in [self.conversations_dir, self.context_dir, self.learning_dir, self.facts_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Load or create memory index
        self.index_file = self.memory_dir / "memory_index.json"
        self.index = self._load_index()
    
    def _load_index(self) -> Dict[str, Any]:
        """Load the memory index or create a new one"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "conversations": {},
            "context_items": {},
            "facts": {},
            "learning_sessions": {},
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_index(self):
        """Save the memory index"""
        self.index["last_updated"] = datetime.now().isoformat()
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)
    
    def _generate_id(self, prefix: str = "") -> str:
        """Generate a unique ID"""
        return f"{prefix}{uuid.uuid4().hex[:8]}"
    
    def _hash_content(self, content: str) -> str:
        """Generate hash for content deduplication"""
        return hashlib.md5(content.encode()).hexdigest()
    
    # ==================== CONVERSATION MEMORY ====================
    
    def save_conversation(self, 
                         messages: List[Dict[str, str]], 
                         title: Optional[str] = None,
                         tags: Optional[List[str]] = None,
                         conversation_id: Optional[str] = None) -> str:
        """Save a conversation to memory"""
        
        if not conversation_id:
            conversation_id = self._generate_id("conv_")
        
        timestamp = datetime.now().isoformat()
        
        # Auto-generate title if not provided
        if not title:
            if messages and len(messages) > 0:
                first_user_msg = next((msg for msg in messages if msg.get('role') == 'user'), None)
                if first_user_msg:
                    title = first_user_msg['content'][:50] + "..." if len(first_user_msg['content']) > 50 else first_user_msg['content']
                else:
                    title = f"Conversation {conversation_id}"
            else:
                title = f"Conversation {conversation_id}"
        
        conversation_data = {
            "id": conversation_id,
            "title": title,
            "messages": messages,
            "tags": tags or [],
            "created": timestamp,
            "updated": timestamp,
            "message_count": len(messages)
        }
        
        # Save conversation file
        conv_file = self.conversations_dir / f"{conversation_id}.json"
        with open(conv_file, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, indent=2, ensure_ascii=False)
        
        # Update index
        self.index["conversations"][conversation_id] = {
            "title": title,
            "created": timestamp,
            "updated": timestamp,
            "tags": tags or [],
            "message_count": len(messages),
            "file": str(conv_file)
        }
        
        self._save_index()
        return conversation_id
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a conversation from memory"""
        conv_file = self.conversations_dir / f"{conversation_id}.json"
        
        if conv_file.exists():
            try:
                with open(conv_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return None
    
    def search_conversations(self, 
                           query: Optional[str] = None,
                           tags: Optional[List[str]] = None,
                           days_back: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search conversations by query, tags, or date"""
        results = []
        
        cutoff_date = None
        if days_back:
            cutoff_date = datetime.now() - timedelta(days=days_back)
        
        for conv_id, conv_info in self.index["conversations"].items():
            match = True
            
            # Date filter
            if cutoff_date:
                conv_date = datetime.fromisoformat(conv_info["created"])
                if conv_date < cutoff_date:
                    match = False
            
            # Tags filter
            if tags and match:
                if not any(tag in conv_info.get("tags", []) for tag in tags):
                    match = False
            
            # Text search
            if query and match:
                conv = self.get_conversation(conv_id)
                if conv:
                    search_text = conv["title"].lower()
                    for msg in conv["messages"]:
                        search_text += " " + msg.get("content", "").lower()
                    
                    if query.lower() not in search_text:
                        match = False
            
            if match:
                results.append({
                    "id": conv_id,
                    **conv_info
                })
        
        # Sort by creation date (newest first)
        results.sort(key=lambda x: x["created"], reverse=True)
        return results
    
    # ==================== CONTEXT MEMORY ====================
    
    def save_context(self, 
                    context_type: str,
                    content: Dict[str, Any],
                    key: Optional[str] = None,
                    expiry_days: Optional[int] = None) -> str:
        """Save context information (user preferences, project details, etc.)"""
        
        if not key:
            key = self._generate_id("ctx_")
        
        timestamp = datetime.now().isoformat()
        expiry = None
        if expiry_days:
            expiry = (datetime.now() + timedelta(days=expiry_days)).isoformat()
        
        context_data = {
            "key": key,
            "type": context_type,
            "content": content,
            "created": timestamp,
            "updated": timestamp,
            "expiry": expiry
        }
        
        # Save context file
        ctx_file = self.context_dir / f"{key}.json"
        with open(ctx_file, 'w', encoding='utf-8') as f:
            json.dump(context_data, f, indent=2, ensure_ascii=False)
        
        # Update index
        self.index["context_items"][key] = {
            "type": context_type,
            "created": timestamp,
            "updated": timestamp,
            "expiry": expiry,
            "file": str(ctx_file)
        }
        
        self._save_index()
        return key
    
    def get_context(self, key: Optional[str] = None, context_type: Optional[str] = None) -> Optional[Union[Dict[str, Any], List[Dict[str, Any]]]]:
        """Get context by key or type"""
        if key:
            ctx_file = self.context_dir / f"{key}.json"
            if ctx_file.exists():
                try:
                    with open(ctx_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Check expiry
                        if data.get("expiry"):
                            if datetime.fromisoformat(data["expiry"]) < datetime.now():
                                self.delete_context(key)
                                return None
                        return data
                except Exception:
                    pass
            return None
        
        elif context_type:
            results = []
            for ctx_key, ctx_info in self.index["context_items"].items():
                if ctx_info["type"] == context_type:
                    ctx_data = self.get_context(ctx_key)
                    if ctx_data:
                        results.append(ctx_data)
            return results
        
        return []
    
    def delete_context(self, key: str):
        """Delete context item"""
        ctx_file = self.context_dir / f"{key}.json"
        if ctx_file.exists():
            ctx_file.unlink()
        
        if key in self.index["context_items"]:
            del self.index["context_items"][key]
            self._save_index()
    
    # ==================== FACTS MEMORY ====================
    
    def save_fact(self, 
                  fact: str,
                  category: str = "general",
                  source: Optional[str] = None,
                  confidence: float = 1.0) -> str:
        """Save a fact to memory"""
        
        fact_id = self._generate_id("fact_")
        fact_hash = self._hash_content(fact)
        
        # Check for duplicates
        for existing_id, existing_info in self.index["facts"].items():
            if existing_info.get("hash") == fact_hash:
                return existing_id  # Return existing fact ID
        
        timestamp = datetime.now().isoformat()
        
        fact_data = {
            "id": fact_id,
            "fact": fact,
            "category": category,
            "source": source,
            "confidence": confidence,
            "hash": fact_hash,
            "created": timestamp,
            "accessed_count": 0,
            "last_accessed": timestamp
        }
        
        # Save fact file
        fact_file = self.facts_dir / f"{fact_id}.json"
        with open(fact_file, 'w', encoding='utf-8') as f:
            json.dump(fact_data, f, indent=2, ensure_ascii=False)
        
        # Update index
        self.index["facts"][fact_id] = {
            "category": category,
            "source": source,
            "confidence": confidence,
            "hash": fact_hash,
            "created": timestamp,
            "file": str(fact_file)
        }
        
        self._save_index()
        return fact_id
    
    def search_facts(self, 
                    query: Optional[str] = None,
                    category: Optional[str] = None,
                    min_confidence: float = 0.0) -> List[Dict[str, Any]]:
        """Search facts"""
        results = []
        
        for fact_id, fact_info in self.index["facts"].items():
            match = True
            
            # Category filter
            if category and fact_info["category"] != category:
                match = False
            
            # Confidence filter
            if fact_info["confidence"] < min_confidence:
                match = False
            
            if match:
                fact_file = self.facts_dir / f"{fact_id}.json"
                if fact_file.exists():
                    try:
                        with open(fact_file, 'r', encoding='utf-8') as f:
                            fact_data = json.load(f)
                            
                            # Text search
                            if query:
                                if query.lower() not in fact_data["fact"].lower():
                                    continue
                            
                            # Update access count
                            fact_data["accessed_count"] = fact_data.get("accessed_count", 0) + 1
                            fact_data["last_accessed"] = datetime.now().isoformat()
                            
                            with open(fact_file, 'w', encoding='utf-8') as f:
                                json.dump(fact_data, f, indent=2, ensure_ascii=False)
                            
                            results.append(fact_data)
                    except Exception:
                        continue
        
        # Sort by confidence and access count
        results.sort(key=lambda x: (x["confidence"], x["accessed_count"]), reverse=True)
        return results
    
    # ==================== LEARNING MEMORY ====================
    
    def save_learning(self, 
                     topic: str,
                     content: str,
                     learning_type: str = "general",
                     importance: int = 5) -> str:
        """Save learning/insights"""
        
        learning_id = self._generate_id("learn_")
        timestamp = datetime.now().isoformat()
        
        learning_data = {
            "id": learning_id,
            "topic": topic,
            "content": content,
            "type": learning_type,
            "importance": importance,
            "created": timestamp,
            "reinforcement_count": 1,
            "last_reinforced": timestamp
        }
        
        # Save learning file
        learning_file = self.learning_dir / f"{learning_id}.json"
        with open(learning_file, 'w', encoding='utf-8') as f:
            json.dump(learning_data, f, indent=2, ensure_ascii=False)
        
        # Update index
        self.index["learning_sessions"][learning_id] = {
            "topic": topic,
            "type": learning_type,
            "importance": importance,
            "created": timestamp,
            "file": str(learning_file)
        }
        
        self._save_index()
        return learning_id
    
    def reinforce_learning(self, learning_id: str):
        """Reinforce a learning item (increases importance)"""
        learning_file = self.learning_dir / f"{learning_id}.json"
        
        if learning_file.exists():
            try:
                with open(learning_file, 'r', encoding='utf-8') as f:
                    learning_data = json.load(f)
                
                learning_data["reinforcement_count"] = learning_data.get("reinforcement_count", 0) + 1
                learning_data["last_reinforced"] = datetime.now().isoformat()
                learning_data["importance"] = min(10, learning_data.get("importance", 5) + 1)
                
                with open(learning_file, 'w', encoding='utf-8') as f:
                    json.dump(learning_data, f, indent=2, ensure_ascii=False)
                
                # Update index
                if learning_id in self.index["learning_sessions"]:
                    self.index["learning_sessions"][learning_id]["importance"] = learning_data["importance"]
                    self._save_index()
                
            except Exception:
                pass
    
    def get_relevant_learning(self, topic: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get learning relevant to a topic"""
        results = []
        
        for learning_id, learning_info in self.index["learning_sessions"].items():
            learning_file = self.learning_dir / f"{learning_id}.json"
            
            if learning_file.exists():
                try:
                    with open(learning_file, 'r', encoding='utf-8') as f:
                        learning_data = json.load(f)
                        
                        # Simple relevance check
                        if (topic.lower() in learning_data["topic"].lower() or 
                            topic.lower() in learning_data["content"].lower()):
                            results.append(learning_data)
                except Exception:
                    continue
        
        # Sort by importance and reinforcement
        results.sort(key=lambda x: (x["importance"], x["reinforcement_count"]), reverse=True)
        return results[:max_results]
    
    # ==================== UTILITY METHODS ====================
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        stats = {
            "conversations": len(self.index["conversations"]),
            "context_items": len(self.index["context_items"]),
            "facts": len(self.index["facts"]),
            "learning_sessions": len(self.index["learning_sessions"]),
            "total_size_mb": 0,
            "created": self.index.get("created"),
            "last_updated": self.index.get("last_updated")
        }
        
        # Calculate total size
        total_size = 0
        for root, dirs, files in os.walk(self.memory_dir):
            for file in files:
                total_size += os.path.getsize(os.path.join(root, file))
        
        stats["total_size_mb"] = round(total_size / (1024 * 1024), 2)
        return stats
    
    def cleanup_expired(self):
        """Clean up expired context items"""
        now = datetime.now()
        expired_keys = []
        
        for key, info in self.index["context_items"].items():
            if info.get("expiry"):
                if datetime.fromisoformat(info["expiry"]) < now:
                    expired_keys.append(key)
        
        for key in expired_keys:
            self.delete_context(key)
        
        return len(expired_keys)
    
    def backup_memory(self, backup_path: str):
        """Create a backup of the entire memory system"""
        backup_dir = Path(backup_path)
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Create timestamped backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"memory_backup_{timestamp}"
        final_backup_path = backup_dir / backup_name
        
        shutil.copytree(self.memory_dir, final_backup_path)
        return str(final_backup_path)
    
    def export_memory(self, export_path: str, format: str = "json"):
        """Export memory to a single file"""
        export_data = {
            "conversations": {},
            "context": {},
            "facts": {},
            "learning": {},
            "metadata": self.get_memory_stats()
        }
        
        # Export conversations
        for conv_id in self.index["conversations"]:
            conv_data = self.get_conversation(conv_id)
            if conv_data:
                export_data["conversations"][conv_id] = conv_data
        
        # Export context
        for ctx_key in self.index["context_items"]:
            ctx_data = self.get_context(ctx_key)
            if ctx_data:
                export_data["context"][ctx_key] = ctx_data
        
        # Export facts
        for fact_id in self.index["facts"]:
            fact_file = self.facts_dir / f"{fact_id}.json"
            if fact_file.exists():
                with open(fact_file, 'r', encoding='utf-8') as f:
                    export_data["facts"][fact_id] = json.load(f)
        
        # Export learning
        for learning_id in self.index["learning_sessions"]:
            learning_file = self.learning_dir / f"{learning_id}.json"
            if learning_file.exists():
                with open(learning_file, 'r', encoding='utf-8') as f:
                    export_data["learning"][learning_id] = json.load(f)
        
        # Save export file
        export_file = Path(export_path)
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return str(export_file)

# Convenience function
def create_memory_manager(memory_dir: Optional[str] = None) -> MemoryManager:
    """Create and return a memory manager instance"""
    return MemoryManager(memory_dir)