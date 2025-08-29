#!/usr/bin/env python3
"""
Simplified PR requirements parser for GitHub Actions automation.

Parses simplified PR templates with a single Requirements section.
"""

import argparse
import json
import re
import sys
from typing import Dict, List, Any


def extract_requirements(text: str) -> List[Dict[str, Any]]:
    """Extract all checkbox requirements from the PR template."""
    requirements = []
    
    # Extract all checkbox items (- [ ] format)
    checkbox_pattern = r'^\s*-\s*\[\s*\]\s*(.+)$'
    matches = re.findall(checkbox_pattern, text, re.MULTILINE)
    
    for match in matches:
        requirement_text = match.strip()
        
        # Categorize based on keywords
        if any(word in requirement_text.lower() for word in ['test', 'verify', 'check']):
            req_type = "test"
            priority = "high"
        elif any(word in requirement_text.lower() for word in ['create', 'set up', 'configure', 'add']):
            req_type = "task"
            priority = "high"
        else:
            req_type = "requirement"
            priority = "normal"
        
        requirements.append({
            "type": req_type,
            "requirement": requirement_text,
            "priority": priority,
            "source": "body"
        })
    
    return requirements


def extract_description(text: str) -> str:
    """Extract the description section."""
    desc_pattern = r'## Description\s*\n(.*?)(?=\n##|\Z)'
    match = re.search(desc_pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""


def parse_claude_command(comment_body: str) -> Dict[str, str]:
    """Parse @claude command from comment body."""
    claude_pattern = r'@claude\s+(.+)'
    match = re.search(claude_pattern, comment_body, re.IGNORECASE | re.DOTALL)
    
    if not match:
        return {"command": "implement", "details": "implement the requirements"}
    
    command_text = match.group(1).strip()
    
    # Simple command detection
    if "test" in command_text.lower():
        command_type = "test"
    elif "fix" in command_text.lower():
        command_type = "fix"
    else:
        command_type = "implement"
    
    return {
        "command": command_type,
        "details": command_text
    }


def main():
    parser = argparse.ArgumentParser(description='Parse simplified PR requirements')
    parser.add_argument('--pr-title', required=True, help='PR title')
    parser.add_argument('--pr-body', required=True, help='PR body')
    parser.add_argument('--comment-body', required=True, help='Comment body')
    
    args = parser.parse_args()
    
    # Extract requirements and description
    requirements = extract_requirements(args.pr_body) if args.pr_body else []
    description = extract_description(args.pr_body) if args.pr_body else ""
    claude_command = parse_claude_command(args.comment_body)
    
    # Categorize requirements
    tasks = [r for r in requirements if r["type"] == "task"]
    tests = [r for r in requirements if r["type"] == "test"]
    other = [r for r in requirements if r["type"] == "requirement"]
    
    # Generate output
    requirements_data = {
        "pr_title": args.pr_title,
        "description": description,
        "claude_command": claude_command,
        "requirements": requirements,
        "summary": {
            "total": len(requirements),
            "tasks": len(tasks),
            "tests": len(tests),
            "other": len(other)
        },
        "test_required": len(tests) > 0,
        "priority": "high" if "urgent" in args.comment_body.lower() else "normal"
    }
    
    # Write to file
    with open('pr_requirements.json', 'w') as f:
        json.dump(requirements_data, f, indent=2)
    
    print(f"✅ Parsed {len(requirements)} requirements:")
    print(f"   📋 Tasks: {len(tasks)}")
    print(f"   🧪 Tests: {len(tests)}")
    print(f"   📝 Other: {len(other)}")
    print(f"🤖 Command: {claude_command['command']}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())