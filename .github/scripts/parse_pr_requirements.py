#!/usr/bin/env python3
"""
Parse PR requirements from title, body, and comment to extract development tasks.

This script analyzes PR information and comments to generate structured requirements
for Claude code generation.
"""

import argparse
import json
import re
import sys
from typing import Dict, List, Any


def extract_requirements_from_text(text: str) -> List[str]:
    """Extract requirements from text using various patterns."""
    requirements = []
    
    # Look for numbered lists
    numbered_pattern = r'^\s*\d+\.\s*(.+)$'
    numbered_matches = re.findall(numbered_pattern, text, re.MULTILINE)
    requirements.extend(numbered_matches)
    
    # Look for bullet points
    bullet_pattern = r'^\s*[-*]\s*(.+)$'
    bullet_matches = re.findall(bullet_pattern, text, re.MULTILINE)
    requirements.extend(bullet_matches)
    
    # Look for "implement", "add", "create" statements
    action_pattern = r'\b(implement|add|create|build|develop|write)\s+(.+?)(?:\.|$)'
    action_matches = re.findall(action_pattern, text, re.IGNORECASE)
    for match in action_matches:
        requirements.append(f"{match[0].capitalize()} {match[1]}")
    
    # Look for "need to" statements
    need_pattern = r'\bneed to\s+(.+?)(?:\.|$)'
    need_matches = re.findall(need_pattern, text, re.IGNORECASE)
    for match in need_matches:
        requirements.append(f"Need to {match}")
    
    return [req.strip() for req in requirements if req.strip()]


def parse_claude_command(comment_body: str) -> Dict[str, Any]:
    """Parse @claude command from comment body."""
    claude_pattern = r'@claude\s+(.+)'
    match = re.search(claude_pattern, comment_body, re.IGNORECASE | re.DOTALL)
    
    if not match:
        return {"command": "implement", "details": ""}
    
    command_text = match.group(1).strip()
    
    # Detect command type
    if any(word in command_text.lower() for word in ['implement', 'code', 'write', 'create']):
        command_type = "implement"
    elif any(word in command_text.lower() for word in ['test', 'tests']):
        command_type = "test"
    elif any(word in command_text.lower() for word in ['review', 'check']):
        command_type = "review"
    elif any(word in command_text.lower() for word in ['fix', 'bug', 'error']):
        command_type = "fix"
    else:
        command_type = "implement"
    
    return {
        "command": command_type,
        "details": command_text
    }


def main():
    parser = argparse.ArgumentParser(description='Parse PR requirements for Claude automation')
    parser.add_argument('--pr-title', required=True, help='PR title')
    parser.add_argument('--pr-body', required=True, help='PR body')
    parser.add_argument('--comment-body', required=True, help='Comment body')
    
    args = parser.parse_args()
    
    # Extract requirements from all sources
    all_requirements = []
    
    # From PR title
    title_reqs = extract_requirements_from_text(args.pr_title)
    all_requirements.extend([{"source": "title", "requirement": req} for req in title_reqs])
    
    # From PR body
    if args.pr_body:
        body_reqs = extract_requirements_from_text(args.pr_body)
        all_requirements.extend([{"source": "body", "requirement": req} for req in body_reqs])
    
    # Parse Claude command
    claude_command = parse_claude_command(args.comment_body)
    
    # Generate structured requirements
    requirements_data = {
        "pr_title": args.pr_title,
        "claude_command": claude_command,
        "requirements": all_requirements,
        "priority": "high" if "urgent" in args.comment_body.lower() else "normal",
        "test_required": "test" in args.comment_body.lower() or "tests" in args.comment_body.lower(),
        "documentation_required": "docs" in args.comment_body.lower() or "documentation" in args.comment_body.lower()
    }
    
    # Write to file
    with open('pr_requirements.json', 'w') as f:
        json.dump(requirements_data, f, indent=2)
    
    print(f"Parsed {len(all_requirements)} requirements")
    print(f"Claude command: {claude_command['command']}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())