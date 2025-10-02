#!/usr/bin/env python3
"""
Memory Management CLI for LM Studio
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from memory_manager import create_memory_manager

def print_stats(memory_manager):
    """Print memory statistics"""
    stats = memory_manager.get_memory_stats()
    
    print("📊 Memory Statistics")
    print("=" * 40)
    print(f"Conversations: {stats['conversations']}")
    print(f"Context Items: {stats['context_items']}")
    print(f"Facts: {stats['facts']}")
    print(f"Learning Sessions: {stats['learning_sessions']}")
    print(f"Total Size: {stats['total_size_mb']} MB")
    print(f"Created: {stats['created']}")
    print(f"Last Updated: {stats['last_updated']}")

def search_conversations(memory_manager, query=None, tags=None, days_back=None):
    """Search and display conversations"""
    print(f"🔍 Searching conversations...")
    
    conversations = memory_manager.search_conversations(
        query=query,
        tags=tags.split(',') if tags else None,
        days_back=days_back
    )
    
    if not conversations:
        print("No conversations found.")
        return
    
    print(f"Found {len(conversations)} conversation(s):")
    print("-" * 40)
    
    for conv in conversations[:10]:  # Show first 10
        print(f"ID: {conv['id']}")
        print(f"Title: {conv['title']}")
        print(f"Created: {conv['created']}")
        print(f"Messages: {conv['message_count']}")
        print(f"Tags: {', '.join(conv.get('tags', []))}")
        print("-" * 40)

def search_facts(memory_manager, query=None, category=None):
    """Search and display facts"""
    print(f"🔍 Searching facts...")
    
    facts = memory_manager.search_facts(
        query=query,
        category=category
    )
    
    if not facts:
        print("No facts found.")
        return
    
    print(f"Found {len(facts)} fact(s):")
    print("-" * 40)
    
    for fact in facts[:10]:  # Show first 10
        print(f"ID: {fact['id']}")
        print(f"Fact: {fact['fact']}")
        print(f"Category: {fact['category']}")
        print(f"Confidence: {fact['confidence']}")
        print(f"Created: {fact['created']}")
        print("-" * 40)

def search_learning(memory_manager, topic):
    """Search and display learning"""
    print(f"🔍 Searching learning for topic: {topic}")
    
    learning = memory_manager.get_relevant_learning(topic)
    
    if not learning:
        print("No learning found.")
        return
    
    print(f"Found {len(learning)} learning item(s):")
    print("-" * 40)
    
    for item in learning:
        print(f"ID: {item['id']}")
        print(f"Topic: {item['topic']}")
        print(f"Content: {item['content']}")
        print(f"Importance: {item['importance']}/10")
        print(f"Reinforcements: {item['reinforcement_count']}")
        print(f"Created: {item['created']}")
        print("-" * 40)

def export_memory(memory_manager, output_file):
    """Export memory to file"""
    print(f"📤 Exporting memory to {output_file}...")
    
    try:
        exported_file = memory_manager.export_memory(output_file)
        print(f"✅ Memory exported successfully to: {exported_file}")
    except Exception as e:
        print(f"❌ Export failed: {e}")

def cleanup_memory(memory_manager):
    """Clean up expired memory items"""
    print("🧹 Cleaning up expired memory items...")
    
    expired_count = memory_manager.cleanup_expired()
    print(f"✅ Removed {expired_count} expired items")

def interactive_mode(memory_manager):
    """Interactive memory exploration"""
    print("🧠 LM Studio Memory Explorer")
    print("=" * 40)
    
    while True:
        print("\nCommands:")
        print("1. stats - Show memory statistics")
        print("2. conversations [query] - Search conversations")
        print("3. facts [query] - Search facts")
        print("4. learning <topic> - Search learning")
        print("5. cleanup - Clean expired items")
        print("6. export <file> - Export memory")
        print("7. quit - Exit")
        
        try:
            command = input("\n> ").strip().split()
            
            if not command:
                continue
            
            cmd = command[0].lower()
            
            if cmd == 'quit':
                break
            elif cmd == 'stats':
                print_stats(memory_manager)
            elif cmd == 'conversations':
                query = command[1] if len(command) > 1 else None
                search_conversations(memory_manager, query=query)
            elif cmd == 'facts':
                query = command[1] if len(command) > 1 else None
                search_facts(memory_manager, query=query)
            elif cmd == 'learning':
                if len(command) < 2:
                    print("Please provide a topic: learning <topic>")
                    continue
                topic = ' '.join(command[1:])
                search_learning(memory_manager, topic)
            elif cmd == 'cleanup':
                cleanup_memory(memory_manager)
            elif cmd == 'export':
                if len(command) < 2:
                    print("Please provide a filename: export <file>")
                    continue
                export_memory(memory_manager, command[1])
            else:
                print("Unknown command. Type 'quit' to exit.")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n👋 Goodbye!")

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(description="LM Studio Memory Management CLI")
    parser.add_argument('--memory-dir', help='Memory directory path')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Stats command
    subparsers.add_parser('stats', help='Show memory statistics')
    
    # Search conversations
    conv_parser = subparsers.add_parser('conversations', help='Search conversations')
    conv_parser.add_argument('--query', help='Search query')
    conv_parser.add_argument('--tags', help='Comma-separated tags')
    conv_parser.add_argument('--days-back', type=int, help='Days back to search')
    
    # Search facts
    fact_parser = subparsers.add_parser('facts', help='Search facts')
    fact_parser.add_argument('--query', help='Search query')
    fact_parser.add_argument('--category', help='Fact category')
    
    # Search learning
    learn_parser = subparsers.add_parser('learning', help='Search learning')
    learn_parser.add_argument('topic', help='Topic to search for')
    
    # Export memory
    export_parser = subparsers.add_parser('export', help='Export memory')
    export_parser.add_argument('output_file', help='Output file path')
    
    # Cleanup
    subparsers.add_parser('cleanup', help='Clean up expired items')
    
    # Interactive mode
    subparsers.add_parser('interactive', help='Interactive memory exploration')
    
    args = parser.parse_args()
    
    # Create memory manager
    memory_manager = create_memory_manager(args.memory_dir)
    
    if not args.command:
        # Default to interactive mode
        interactive_mode(memory_manager)
        return
    
    # Handle commands
    if args.command == 'stats':
        print_stats(memory_manager)
    
    elif args.command == 'conversations':
        search_conversations(
            memory_manager,
            query=args.query,
            tags=args.tags,
            days_back=args.days_back
        )
    
    elif args.command == 'facts':
        search_facts(
            memory_manager,
            query=args.query,
            category=args.category
        )
    
    elif args.command == 'learning':
        search_learning(memory_manager, args.topic)
    
    elif args.command == 'export':
        export_memory(memory_manager, args.output_file)
    
    elif args.command == 'cleanup':
        cleanup_memory(memory_manager)
    
    elif args.command == 'interactive':
        interactive_mode(memory_manager)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()