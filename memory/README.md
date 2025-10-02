# LM Studio Memory System

This directory provides persistent memory capabilities for LM Studio, allowing the AI to remember conversations, learn from interactions, and maintain context across sessions.

## 📁 Memory Structure

```
memory/
├── conversations/     # Saved conversations with full message history
├── context/          # Contextual information (user preferences, project details)
├── facts/           # Important facts and information to remember
├── learning/        # Learning insights and patterns discovered
└── memory_index.json # Index file for fast searches and metadata
```

## 🧠 Memory Types

### 1. Conversations
- **Purpose**: Store complete conversation histories
- **Usage**: Reference previous discussions, maintain context
- **Features**: Searchable by content, tags, date ranges
- **Auto-cleanup**: Configurable retention periods

### 2. Context
- **Purpose**: Store user preferences, project information, settings
- **Usage**: Personalize responses, remember user needs
- **Features**: Categorized storage, expiration dates
- **Examples**: Coding style preferences, project requirements, user goals

### 3. Facts
- **Purpose**: Store important factual information
- **Usage**: Build knowledge base, avoid repetition
- **Features**: Confidence scoring, categorization, deduplication
- **Examples**: API documentation facts, project specifications, user requirements

### 4. Learning
- **Purpose**: Store insights and patterns learned during interactions
- **Usage**: Improve future responses, adapt to user patterns
- **Features**: Importance scoring, reinforcement learning, topic-based retrieval
- **Examples**: Code patterns user prefers, common issues and solutions

## 🔧 Memory Operations

### Saving Information
```python
# Save conversation
memory_manager.save_conversation(
    messages=[{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi!"}],
    title="Greeting conversation",
    tags=["greeting", "casual"]
)

# Save context
memory_manager.save_context(
    context_type="user_preference",
    content={"coding_style": "PEP8", "preferred_language": "Python"},
    key="user_coding_prefs"
)

# Save fact
memory_manager.save_fact(
    fact="User prefers async/await over traditional callbacks",
    category="coding_preferences",
    confidence=0.9
)

# Save learning
memory_manager.save_learning(
    topic="error_handling",
    content="User consistently asks for try-catch blocks in Python code",
    importance=8
)
```

### Retrieving Information
```python
# Search conversations
conversations = memory_manager.search_conversations(
    query="authentication",
    tags=["security"],
    days_back=30
)

# Get context
user_prefs = memory_manager.get_context(context_type="user_preference")

# Search facts
facts = memory_manager.search_facts(
    query="API rate limits",
    category="technical_specs"
)

# Get relevant learning
insights = memory_manager.get_relevant_learning("error_handling")
```

## 🌐 API Endpoints

### Conversations
- `POST /api/memory/conversations` - Save conversation
- `GET /api/memory/conversations/<id>` - Get specific conversation
- `GET /api/memory/conversations/search` - Search conversations

### Context
- `POST /api/memory/context` - Save context
- `GET /api/memory/context` - Get context by key or type
- `DELETE /api/memory/context/<key>` - Delete context

### Facts
- `POST /api/memory/facts` - Save fact
- `GET /api/memory/facts/search` - Search facts

### Learning
- `POST /api/memory/learning` - Save learning
- `GET /api/memory/learning/search` - Search learning
- `POST /api/memory/learning/<id>/reinforce` - Reinforce learning

### Utilities
- `GET /api/memory/stats` - Get memory statistics
- `POST /api/memory/cleanup` - Clean expired items
- `POST /api/memory/export` - Export memory data

## 🎯 Usage Examples

### 1. Learning User Preferences
```json
// LM Studio saves user coding preferences
POST /api/memory/context
{
  "type": "coding_preference",
  "content": {
    "language": "Python",
    "style": "PEP8",
    "prefers_type_hints": true,
    "testing_framework": "pytest"
  }
}
```

### 2. Remembering Project Details
```json
// Save project-specific information
POST /api/memory/context
{
  "type": "project_info",
  "content": {
    "name": "E-commerce API",
    "framework": "Flask",
    "database": "PostgreSQL",
    "main_features": ["user_auth", "payment_processing", "inventory"]
  },
  "key": "current_project"
}
```

### 3. Building Knowledge Base
```json
// Save important facts discovered during development
POST /api/memory/facts
{
  "fact": "The payment API has a rate limit of 100 requests per minute",
  "category": "api_limitations",
  "source": "payment_provider_docs",
  "confidence": 1.0
}
```

### 4. Learning from Patterns
```json
// Save insights about user behavior
POST /api/memory/learning
{
  "topic": "debugging_approach",
  "content": "User prefers step-by-step debugging with print statements before using debugger",
  "type": "user_behavior",
  "importance": 7
}
```

## 🔄 Memory Workflow

### Automatic Memory Usage
1. **Conversation End**: Automatically save important conversations
2. **Context Discovery**: Save user preferences as they're revealed
3. **Fact Recording**: Store important information discovered during sessions
4. **Pattern Learning**: Identify and save patterns in user interactions

### Manual Memory Operations
1. **Explicit Saves**: User requests to remember specific information
2. **Knowledge Queries**: User asks "What do you remember about X?"
3. **Context Retrieval**: Load relevant context for current conversation
4. **Learning Reinforcement**: Strengthen important memories

## 📊 Memory Statistics

Track memory usage and effectiveness:
- Total conversations stored
- Context items by type
- Facts by category and confidence
- Learning items by importance
- Storage size and cleanup stats

## 🧹 Memory Maintenance

### Automatic Cleanup
- Expired context items removed automatically
- Low-confidence facts archived after time
- Unused learning items may be demoted

### Manual Maintenance
- Export memory for backup
- Clean up old conversations
- Merge duplicate facts
- Review and update learning importance

## 🔒 Privacy and Security

### Data Protection
- All memory stored locally
- No external transmission unless explicitly requested
- User controls what information is saved
- Easy deletion and cleanup options

### Access Control
- Memory access restricted to repository scope
- No system file access through memory
- Configurable retention policies
- User can inspect all stored data

## ⚡ Performance Features

### Optimization
- Indexed searches for fast retrieval
- Content deduplication to save space
- Lazy loading of large memory items
- Configurable memory limits

### Scalability
- Hierarchical storage for large datasets
- Compression for old/unused items
- Pagination for large result sets
- Background cleanup processes

This memory system transforms LM Studio from a stateless assistant into a persistent, learning AI that grows more helpful over time by remembering what matters to you and your projects.