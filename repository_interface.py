import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
from memory_manager import create_memory_manager

load_dotenv()

class RepositoryInterface:
    """Interface for LM Studio to interact with the repository"""
    
    def __init__(self, repo_path: Optional[str] = None):
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.allowed_extensions = {'.py', '.md', '.txt', '.json', '.yaml', '.yml', '.toml', '.cfg', '.ini'}
        self.excluded_dirs = {'.git', '__pycache__', '.venv', 'venv', 'node_modules', '.pytest_cache'}
    
    def get_repo_structure(self, max_depth: int = 3) -> Dict[str, Any]:
        """Get repository structure for LM Studio to understand the codebase"""
        def scan_directory(path: Path, current_depth: int = 0) -> Dict[str, Any]:
            if current_depth > max_depth:
                return {"type": "directory", "truncated": True}
            
            items = {}
            try:
                for item in path.iterdir():
                    if item.name.startswith('.') and item.name not in {'.env.example', '.gitignore'}:
                        continue
                    if item.name in self.excluded_dirs:
                        continue
                    
                    if item.is_file():
                        if item.suffix in self.allowed_extensions:
                            items[item.name] = {
                                "type": "file",
                                "size": item.stat().st_size,
                                "extension": item.suffix
                            }
                    elif item.is_dir():
                        items[item.name] = {
                            "type": "directory",
                            "contents": scan_directory(item, current_depth + 1)
                        }
            except PermissionError:
                pass
            
            return items
        
        return {
            "repository_path": str(self.repo_path),
            "structure": scan_directory(self.repo_path)
        }
    
    def read_file(self, file_path: str, lines: Optional[tuple] = None) -> Dict[str, Any]:
        """Read file content safely"""
        try:
            full_path = self.repo_path / file_path
            
            # Security check - ensure path is within repo
            if not str(full_path.resolve()).startswith(str(self.repo_path.resolve())):
                return {"error": "Access denied: Path outside repository"}
            
            if not full_path.exists():
                return {"error": f"File not found: {file_path}"}
            
            if full_path.suffix not in self.allowed_extensions:
                return {"error": f"File type not allowed: {full_path.suffix}"}
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # If specific lines requested
            if lines:
                start_line, end_line = lines
                lines_list = content.split('\n')
                if start_line < 1 or end_line > len(lines_list):
                    return {"error": "Line range out of bounds"}
                content = '\n'.join(lines_list[start_line-1:end_line])
            
            return {
                "file_path": file_path,
                "content": content,
                "lines_total": len(content.split('\n')),
                "size": len(content)
            }
        
        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}
    
    def write_file(self, file_path: str, content: str, backup: bool = True) -> Dict[str, Any]:
        """Write file content safely with backup"""
        try:
            full_path = self.repo_path / file_path
            
            # Security check
            if not str(full_path.resolve()).startswith(str(self.repo_path.resolve())):
                return {"error": "Access denied: Path outside repository"}
            
            if full_path.suffix not in self.allowed_extensions:
                return {"error": f"File type not allowed: {full_path.suffix}"}
            
            # Create directories if needed
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Backup existing file
            backup_path = None
            if backup and full_path.exists():
                backup_path = full_path.with_suffix(full_path.suffix + '.backup')
                full_path.rename(backup_path)
            
            # Write new content
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "file_path": file_path,
                "status": "success",
                "backup_created": str(backup_path) if backup_path else None,
                "lines_written": len(content.split('\n'))
            }
        
        except Exception as e:
            return {"error": f"Failed to write file: {str(e)}"}
    
    def search_files(self, query: str, file_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Search for text in files"""
        try:
            results = []
            file_types = file_types or ['.py', '.md', '.txt']
            
            for file_path in self.repo_path.rglob('*'):
                if file_path.is_file() and file_path.suffix in file_types:
                    if any(excluded in str(file_path) for excluded in self.excluded_dirs):
                        continue
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if query.lower() in content.lower():
                                # Find line numbers with matches
                                lines = content.split('\n')
                                matching_lines = []
                                for i, line in enumerate(lines, 1):
                                    if query.lower() in line.lower():
                                        matching_lines.append({
                                            "line_number": i,
                                            "content": line.strip()
                                        })
                                
                                results.append({
                                    "file_path": str(file_path.relative_to(self.repo_path)),
                                    "matches": len(matching_lines),
                                    "matching_lines": matching_lines[:10]  # Limit to first 10 matches
                                })
                    except Exception:
                        continue
            
            return {
                "query": query,
                "total_files_searched": len(list(self.repo_path.rglob('*'))),
                "files_with_matches": len(results),
                "results": results[:20]  # Limit to top 20 files
            }
        
        except Exception as e:
            return {"error": f"Search failed: {str(e)}"}
    
    def run_tests(self) -> Dict[str, Any]:
        """Run tests and return results"""
        try:
            # Look for test files
            test_files = list(self.repo_path.rglob('test_*.py')) + list(self.repo_path.rglob('*_test.py'))
            
            if not test_files:
                return {"message": "No test files found"}
            
            # Run pytest if available
            result = subprocess.run(
                ['python', '-m', 'pytest', '--tb=short', '-v'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "test_files_found": len(test_files),
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "status": "passed" if result.returncode == 0 else "failed"
            }
        
        except subprocess.TimeoutExpired:
            return {"error": "Test execution timed out"}
        except Exception as e:
            return {"error": f"Failed to run tests: {str(e)}"}
    
    def get_git_status(self) -> Dict[str, Any]:
        """Get git status information"""
        try:
            # Check if it's a git repository
            git_dir = self.repo_path / '.git'
            if not git_dir.exists():
                return {"error": "Not a git repository"}
            
            # Get git status
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {"error": f"Git command failed: {result.stderr}"}
            
            # Parse status
            changes = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    status = line[:2]
                    file_path = line[3:]
                    changes.append({
                        "status": status,
                        "file": file_path,
                        "description": self._parse_git_status(status)
                    })
            
            # Get current branch
            branch_result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            
            return {
                "current_branch": branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown",
                "changes": changes,
                "total_changes": len(changes)
            }
        
        except Exception as e:
            return {"error": f"Failed to get git status: {str(e)}"}
    
    def _parse_git_status(self, status: str) -> str:
        """Parse git status codes"""
        status_map = {
            'M ': 'Modified (staged)',
            ' M': 'Modified (not staged)',
            'A ': 'Added (staged)',
            ' A': 'Added (not staged)',
            'D ': 'Deleted (staged)',
            ' D': 'Deleted (not staged)',
            '??': 'Untracked',
            'R ': 'Renamed',
            'C ': 'Copied'
        }
        return status_map.get(status, f'Unknown status: {status}')

# Flask application
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Initialize repository interface
repo_interface = RepositoryInterface()

# Initialize memory manager
memory_manager = create_memory_manager()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "LM Studio Repository Interface"})

@app.route('/api/repository/structure', methods=['GET'])
def get_structure():
    """Get repository structure"""
    max_depth = request.args.get('max_depth', 3, type=int)
    return jsonify(repo_interface.get_repo_structure(max_depth))

@app.route('/api/repository/file', methods=['GET'])
def read_file():
    """Read file content"""
    file_path = request.args.get('path')
    if not file_path:
        return jsonify({"error": "Missing 'path' parameter"}), 400
    
    # Optional line range
    start_line = request.args.get('start_line', type=int)
    end_line = request.args.get('end_line', type=int)
    lines = (start_line, end_line) if start_line and end_line else None
    
    result = repo_interface.read_file(file_path, lines)
    return jsonify(result)

@app.route('/api/repository/file', methods=['POST'])
def write_file():
    """Write file content"""
    data = request.get_json()
    if not data or 'path' not in data or 'content' not in data:
        return jsonify({"error": "Missing 'path' or 'content' in request body"}), 400
    
    backup = data.get('backup', True)
    result = repo_interface.write_file(data['path'], data['content'], backup)
    return jsonify(result)

@app.route('/api/repository/search', methods=['GET'])
def search_files():
    """Search files for text"""
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400
    
    file_types = request.args.getlist('file_types')
    result = repo_interface.search_files(query, file_types if file_types else None)
    return jsonify(result)

@app.route('/api/repository/tests', methods=['POST'])
def run_tests():
    """Run repository tests"""
    result = repo_interface.run_tests()
    return jsonify(result)

@app.route('/api/repository/git/status', methods=['GET'])
def git_status():
    """Get git status"""
    result = repo_interface.get_git_status()
    return jsonify(result)

# ==================== MEMORY ENDPOINTS ====================

@app.route('/api/memory/conversations', methods=['POST'])
def save_conversation():
    """Save a conversation to memory"""
    data = request.get_json()
    if not data or 'messages' not in data:
        return jsonify({"error": "Missing 'messages' in request body"}), 400
    
    conversation_id = memory_manager.save_conversation(
        messages=data['messages'],
        title=data.get('title'),
        tags=data.get('tags'),
        conversation_id=data.get('conversation_id')
    )
    
    return jsonify({"conversation_id": conversation_id, "status": "saved"})

@app.route('/api/memory/conversations/<conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get a specific conversation"""
    conversation = memory_manager.get_conversation(conversation_id)
    if conversation:
        return jsonify(conversation)
    else:
        return jsonify({"error": "Conversation not found"}), 404

@app.route('/api/memory/conversations/search', methods=['GET'])
def search_conversations():
    """Search conversations"""
    query = request.args.get('query')
    tags = request.args.getlist('tags')
    days_back = request.args.get('days_back', type=int)
    
    results = memory_manager.search_conversations(
        query=query,
        tags=tags if tags else None,
        days_back=days_back
    )
    
    return jsonify({"results": results, "count": len(results)})

@app.route('/api/memory/context', methods=['POST'])
def save_context():
    """Save context information"""
    data = request.get_json()
    if not data or 'type' not in data or 'content' not in data:
        return jsonify({"error": "Missing 'type' or 'content' in request body"}), 400
    
    key = memory_manager.save_context(
        context_type=data['type'],
        content=data['content'],
        key=data.get('key'),
        expiry_days=data.get('expiry_days')
    )
    
    return jsonify({"key": key, "status": "saved"})

@app.route('/api/memory/context', methods=['GET'])
def get_context():
    """Get context information"""
    key = request.args.get('key')
    context_type = request.args.get('type')
    
    if not key and not context_type:
        return jsonify({"error": "Must provide either 'key' or 'type' parameter"}), 400
    
    result = memory_manager.get_context(key=key, context_type=context_type)
    
    if result is None:
        return jsonify({"error": "Context not found"}), 404
    
    return jsonify(result)

@app.route('/api/memory/context/<key>', methods=['DELETE'])
def delete_context(key):
    """Delete context item"""
    memory_manager.delete_context(key)
    return jsonify({"status": "deleted"})

@app.route('/api/memory/facts', methods=['POST'])
def save_fact():
    """Save a fact to memory"""
    data = request.get_json()
    if not data or 'fact' not in data:
        return jsonify({"error": "Missing 'fact' in request body"}), 400
    
    fact_id = memory_manager.save_fact(
        fact=data['fact'],
        category=data.get('category', 'general'),
        source=data.get('source'),
        confidence=data.get('confidence', 1.0)
    )
    
    return jsonify({"fact_id": fact_id, "status": "saved"})

@app.route('/api/memory/facts/search', methods=['GET'])
def search_facts():
    """Search facts"""
    query = request.args.get('query')
    category = request.args.get('category')
    min_confidence = request.args.get('min_confidence', 0.0, type=float)
    
    results = memory_manager.search_facts(
        query=query,
        category=category,
        min_confidence=min_confidence
    )
    
    return jsonify({"results": results, "count": len(results)})

@app.route('/api/memory/learning', methods=['POST'])
def save_learning():
    """Save learning/insights"""
    data = request.get_json()
    if not data or 'topic' not in data or 'content' not in data:
        return jsonify({"error": "Missing 'topic' or 'content' in request body"}), 400
    
    learning_id = memory_manager.save_learning(
        topic=data['topic'],
        content=data['content'],
        learning_type=data.get('type', 'general'),
        importance=data.get('importance', 5)
    )
    
    return jsonify({"learning_id": learning_id, "status": "saved"})

@app.route('/api/memory/learning/<learning_id>/reinforce', methods=['POST'])
def reinforce_learning(learning_id):
    """Reinforce a learning item"""
    memory_manager.reinforce_learning(learning_id)
    return jsonify({"status": "reinforced"})

@app.route('/api/memory/learning/search', methods=['GET'])
def search_learning():
    """Get learning relevant to a topic"""
    topic = request.args.get('topic')
    if not topic:
        return jsonify({"error": "Missing 'topic' parameter"}), 400
    
    max_results = request.args.get('max_results', 10, type=int)
    results = memory_manager.get_relevant_learning(topic, max_results)
    
    return jsonify({"results": results, "count": len(results)})

@app.route('/api/memory/stats', methods=['GET'])
def memory_stats():
    """Get memory usage statistics"""
    stats = memory_manager.get_memory_stats()
    return jsonify(stats)

@app.route('/api/memory/cleanup', methods=['POST'])
def cleanup_memory():
    """Clean up expired memory items"""
    expired_count = memory_manager.cleanup_expired()
    return jsonify({"expired_items_removed": expired_count, "status": "cleanup_complete"})

@app.route('/api/memory/export', methods=['POST'])
def export_memory():
    """Export memory to file"""
    data = request.get_json() or {}
    export_path = data.get('path', 'memory_export.json')
    
    try:
        exported_file = memory_manager.export_memory(export_path)
        return jsonify({"exported_file": exported_file, "status": "exported"})
    except Exception as e:
        return jsonify({"error": f"Export failed: {str(e)}"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

def main():
    """Main function to run the repository interface server"""
    port = int(os.getenv('REPO_INTERFACE_PORT', 8080))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    print(f"🔧 Starting LM Studio Repository Interface on port {port}")
    print(f"📁 Repository path: {repo_interface.repo_path}")
    print(f"🌐 API will be available at: http://localhost:{port}/api/")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )

if __name__ == "__main__":
    main()