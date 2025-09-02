#!/usr/bin/env python3
"""
Enhanced PR requirements parser for GitHub Actions automation.

Parses PR templates with comprehensive analysis including complexity assessment,
effort estimation, and implementation context for the AI agent.
"""

import argparse
import json
import re
import sys
from typing import Dict, List, Any


def extract_requirements(text: str) -> List[Dict[str, Any]]:
    """Extract all checkbox requirements from the PR template with enhanced analysis."""
    requirements = []
    
    # Extract all checkbox items (- [ ] format)
    checkbox_pattern = r'^\s*-\s*\[\s*\]\s*(.+)$'
    matches = re.findall(checkbox_pattern, text, re.MULTILINE)
    
    for match in matches:
        requirement_text = match.strip()
        
        # Enhanced categorization based on keywords
        if any(word in requirement_text.lower() for word in ['test', 'verify', 'check', 'validate']):
            req_type = "test"
            priority = "high"
        elif any(word in requirement_text.lower() for word in ['create', 'set up', 'configure', 'add', 'implement', 'build']):
            req_type = "task"
            priority = "high"
        elif any(word in requirement_text.lower() for word in ['fix', 'bug', 'error', 'issue']):
            req_type = "bugfix"
            priority = "high"
        elif any(word in requirement_text.lower() for word in ['refactor', 'optimize', 'improve']):
            req_type = "improvement"
            priority = "normal"
        elif any(word in requirement_text.lower() for word in ['document', 'docs', 'comment']):
            req_type = "documentation"
            priority = "normal"
        else:
            req_type = "requirement"
            priority = "normal"
        
        # Assess complexity
        complexity = assess_requirement_complexity(requirement_text)
        
        # Determine priority with more granular analysis
        priority = determine_requirement_priority(requirement_text, req_type, priority)
        
        requirements.append({
            "type": req_type,
            "requirement": requirement_text,
            "priority": priority,
            "complexity": complexity,
            "source": "body"
        })
    
    return requirements


def assess_requirement_complexity(requirement_text: str) -> str:
    """Assess complexity of a requirement based on content analysis."""
    text_lower = requirement_text.lower()
    
    # High complexity indicators
    if any(word in text_lower for word in ['complex', 'major', 'significant', 'advanced', 'integration', 'system', 'architecture']):
        return "high"
    elif any(word in text_lower for word in ['database', 'api', 'service', 'authentication', 'security']):
        return "high"
    elif any(word in text_lower for word in ['simple', 'basic', 'minor', 'small', 'update']):
        return "low"
    else:
        return "medium"


def determine_requirement_priority(requirement_text: str, req_type: str, base_priority: str) -> str:
    """Determine priority for a specific requirement with enhanced analysis."""
    text_lower = requirement_text.lower()
    
    # Critical priority indicators
    if any(word in text_lower for word in ['critical', 'urgent', 'security', 'bug', 'fix', 'error', 'broken']):
        return "critical"
    elif any(word in text_lower for word in ['important', 'core', 'essential', 'required', 'blocking']):
        return "high"
    elif req_type in ['test', 'bugfix']:
        return "high"
    elif any(word in text_lower for word in ['nice to have', 'optional', 'enhancement']):
        return "low"
    else:
        return base_priority


def extract_description(text: str) -> str:
    """Extract the description section."""
    desc_pattern = r'## Description\s*\n(.*?)(?=\n##|\Z)'
    match = re.search(desc_pattern, text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""


def parse_claude_command(comment_body: str) -> Dict[str, Any]:
    """Parse @claude command from comment body with enhanced analysis."""
    claude_pattern = r'@claude\s+(.+)'
    match = re.search(claude_pattern, comment_body, re.IGNORECASE | re.DOTALL)
    
    if not match:
        return {
            "command": "implement", 
            "details": "implement the requirements",
            "urgency": "normal",
            "scope": "full"
        }
    
    command_text = match.group(1).strip()
    
    # Enhanced command detection
    command_type = detect_command_type(command_text)
    urgency = detect_urgency(command_text)
    scope = detect_scope(command_text)
    
    return {
        "command": command_type,
        "details": command_text,
        "urgency": urgency,
        "scope": scope
    }


def detect_command_type(command_text: str) -> str:
    """Detect the type of command with enhanced analysis."""
    command_lower = command_text.lower()
    
    if any(word in command_lower for word in ['implement', 'code', 'write', 'create', 'build', 'develop']):
        return "implement"
    elif any(word in command_lower for word in ['test', 'tests', 'verify', 'validate', 'check']):
        return "test"
    elif any(word in command_lower for word in ['review', 'check', 'analyze', 'audit', 'inspect']):
        return "review"
    elif any(word in command_lower for word in ['fix', 'bug', 'error', 'issue', 'resolve']):
        return "fix"
    elif any(word in command_lower for word in ['refactor', 'optimize', 'improve', 'enhance']):
        return "refactor"
    elif any(word in command_lower for word in ['document', 'docs', 'comment', 'explain']):
        return "document"
    else:
        return "implement"


def detect_urgency(command_text: str) -> str:
    """Detect urgency level from command."""
    command_lower = command_text.lower()
    
    if any(word in command_lower for word in ['urgent', 'asap', 'immediately', 'critical', 'emergency']):
        return "critical"
    elif any(word in command_lower for word in ['soon', 'quickly', 'fast', 'priority']):
        return "high"
    else:
        return "normal"


def detect_scope(command_text: str) -> str:
    """Detect scope of work from command."""
    command_lower = command_text.lower()
    
    if any(word in command_lower for word in ['minimal', 'basic', 'simple', 'quick']):
        return "minimal"
    elif any(word in command_lower for word in ['comprehensive', 'full', 'complete', 'thorough', 'detailed']):
        return "comprehensive"
    else:
        return "full"


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
        "documentation_required": "docs" in args.comment_body.lower() or "documentation" in args.pr_body.lower() if args.pr_body else False,
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