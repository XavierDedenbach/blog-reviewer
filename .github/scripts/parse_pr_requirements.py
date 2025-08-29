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
from typing import Dict, List, Any, Optional


def extract_requirements_from_text(text: str) -> List[Dict[str, Any]]:
    """Extract requirements from structured PR text."""
    requirements = []
    
    # Extract Tasks section
    tasks_section = extract_section(text, "## Tasks")
    if tasks_section:
        task_items = extract_checkbox_items(tasks_section)
        requirements.extend([
            {"type": "task", "requirement": item, "priority": "high", "section": "tasks"}
            for item in task_items
        ])
    
    # Extract Testing Requirements (including nested subsections)
    testing_section = extract_section(text, "## Testing Requirements")
    if testing_section:
        test_items = extract_checkbox_items(testing_section)
        requirements.extend([
            {"type": "test", "requirement": item, "priority": "high", "section": "testing"}
            for item in test_items
        ])
        
        # Also extract from nested testing subsections
        for subsection in ["### Unit Tests", "### Integration Tests", "### Infrastructure Tests"]:
            sub_content = extract_section(testing_section, subsection)
            if sub_content:
                sub_items = extract_checkbox_items(sub_content)
                requirements.extend([
                    {"type": "test", "requirement": item, "priority": "high", "section": subsection.lower().replace("### ", "").replace(" ", "_")}
                    for item in sub_items
                ])
    
    # Extract Acceptance Criteria
    acceptance_section = extract_section(text, "## Acceptance Criteria")
    if acceptance_section:
        acceptance_items = extract_checkbox_items(acceptance_section)
        requirements.extend([
            {"type": "acceptance", "requirement": item, "priority": "critical", "section": "acceptance"}
            for item in acceptance_items
        ])
    
    # Extract from Overview/Description if no structured sections found
    if not requirements:
        overview = extract_section(text, "## Overview") or extract_section(text, "## Description")
        if overview:
            general_items = extract_general_requirements(overview)
            requirements.extend([
                {"type": "general", "requirement": item, "priority": "normal", "section": "general"}
                for item in general_items
            ])
    
    return requirements


def extract_section(text: str, section_header: str) -> Optional[str]:
    """Extract content of a specific section from markdown text."""
    # For main sections (##), stop at next ## followed by space or end
    if section_header.startswith('## '):
        pattern = rf'{re.escape(section_header)}\s*\n(.*?)(?=\n## |\Z)'
    # For subsections (###), stop at next ### or ## or end  
    elif section_header.startswith('### '):
        pattern = rf'{re.escape(section_header)}\s*\n(.*?)(?=\n###|\n## |\Z)'
    else:
        pattern = rf'{re.escape(section_header)}\s*\n(.*?)(?=\n## |\Z)'
    
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else None


def extract_checkbox_items(text: str) -> List[str]:
    """Extract items from checkbox lists (- [ ] format)."""
    checkbox_pattern = r'^\s*-\s*\[\s*\]\s*(.+)$'
    matches = re.findall(checkbox_pattern, text, re.MULTILINE)
    return [match.strip() for match in matches if match.strip()]


def extract_general_requirements(text: str) -> List[str]:
    """Extract general requirements from description text."""
    requirements = []
    
    # Look for action verbs
    action_patterns = [
        r'\b(implement|add|create|build|develop|write|set up|configure|establish)\s+(.+?)(?:\.|\n|$)',
        r'\b(need to|must|should|will)\s+(.+?)(?:\.|\n|$)'
    ]
    
    for pattern in action_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            requirements.append(f"{match[0].capitalize()} {match[1].strip()}")
    
    return [req for req in requirements if req.strip()]


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
    
    # From PR title (simple extraction)
    if args.pr_title:
        title_reqs = extract_general_requirements(args.pr_title)
        all_requirements.extend([
            {"source": "title", "type": "general", "requirement": req, "priority": "high", "section": "title"}
            for req in title_reqs
        ])
    
    # From PR body (structured extraction)
    if args.pr_body:
        body_reqs = extract_requirements_from_text(args.pr_body)
        for req in body_reqs:
            req["source"] = "body"
            all_requirements.append(req)
    
    # Parse Claude command
    claude_command = parse_claude_command(args.comment_body)
    
    # Analyze requirements for better categorization
    task_count = len([r for r in all_requirements if r.get("type") == "task"])
    test_count = len([r for r in all_requirements if r.get("type") == "test"])
    acceptance_count = len([r for r in all_requirements if r.get("type") == "acceptance"])
    
    # Generate structured requirements
    requirements_data = {
        "pr_title": args.pr_title,
        "claude_command": claude_command,
        "requirements": all_requirements,
        "summary": {
            "total_requirements": len(all_requirements),
            "tasks": task_count,
            "tests": test_count,
            "acceptance_criteria": acceptance_count
        },
        "priority": "high" if "urgent" in args.comment_body.lower() else "normal",
        "test_required": test_count > 0 or "test" in args.comment_body.lower(),
        "documentation_required": "docs" in args.comment_body.lower() or "documentation" in args.pr_body.lower() if args.pr_body else False
    }
    
    # Write to file
    with open('pr_requirements.json', 'w') as f:
        json.dump(requirements_data, f, indent=2)
    
    print(f"Parsed {len(all_requirements)} requirements:")
    print(f"  - Tasks: {requirements_data['summary']['tasks']}")
    print(f"  - Tests: {requirements_data['summary']['tests']}")
    print(f"  - Acceptance Criteria: {requirements_data['summary']['acceptance_criteria']}")
    print(f"Claude command: {claude_command['command']} - {claude_command['details'][:50]}...")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())