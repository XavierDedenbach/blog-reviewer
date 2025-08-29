#!/usr/bin/env python3
"""
Claude-powered code generator for GitHub PR automation.

This script uses the Anthropic Claude API to generate code based on PR requirements
following a Test-Driven Development approach.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests


class ClaudeCodeGenerator:
    def __init__(self, api_key: str, github_token: str, repo: str):
        self.api_key = api_key
        self.github_token = github_token
        self.repo = repo
        self.anthropic_url = "https://api.anthropic.com/v1/messages"
        
    def read_project_structure(self) -> str:
        """Read and analyze the project structure."""
        structure = []
        
        # Get main directories and files
        for item in Path('.').iterdir():
            if item.name.startswith('.') and item.name not in ['.github', '.gitignore']:
                continue
            if item.is_dir():
                structure.append(f"📁 {item.name}/")
                # Add some key files from subdirectories
                if item.name in ['api', 'core', 'cli', 'tests']:
                    for subitem in item.iterdir():
                        if subitem.suffix == '.py':
                            structure.append(f"  📄 {subitem.name}")
            elif item.suffix in ['.py', '.md', '.yml', '.yaml', '.json', '.txt']:
                structure.append(f"📄 {item.name}")
        
        return "\n".join(structure)
    
    def read_existing_tests(self) -> str:
        """Read existing test files to understand testing patterns."""
        tests_content = []
        tests_dir = Path('tests')
        
        if tests_dir.exists():
            for test_file in tests_dir.rglob('*.py'):
                try:
                    content = test_file.read_text()[:1000]  # First 1000 chars
                    tests_content.append(f"## {test_file}\n```python\n{content}\n```")
                except:
                    continue
        
        return "\n\n".join(tests_content) if tests_content else "No existing tests found."
    
    def generate_code_with_claude(self, requirements: Dict[str, Any]) -> str:
        """Generate code using Claude API."""
        project_structure = self.read_project_structure()
        existing_tests = self.read_existing_tests()
        
        # Read package files for context
        requirements_txt = ""
        if Path('requirements.txt').exists():
            requirements_txt = Path('requirements.txt').read_text()
        
        pyproject_toml = ""
        if Path('pyproject.toml').exists():
            pyproject_toml = Path('pyproject.toml').read_text()
        
        
        # Create comprehensive prompt
        prompt = f"""You are a senior Python developer working on a blog reviewer application. 

IMPORTANT: Before implementing, please read and understand the full project context from these files:
- project_plan.md (contains detailed technical architecture and implementation plan)
- prd.md (contains product requirements and business logic)

These files provide critical context for the overall system design and requirements.

## Project Context
This is a blog content analysis and review system with the following structure:
```
{project_structure}
```

## Current Dependencies
### requirements.txt
```
{requirements_txt}
```

### pyproject.toml
```
{pyproject_toml}
```

## Existing Test Patterns
{existing_tests}

## Task Requirements
PR Title: {requirements['pr_title']}
Claude Command: {requirements['claude_command']['command']} - {requirements['claude_command']['details']}

Requirements to implement:
{chr(10).join([f"- {req['requirement']} (from {req['source']})" for req in requirements['requirements']])}

Test Required: {requirements['test_required']}
Documentation Required: {requirements['documentation_required']}

## Instructions
Please follow Test-Driven Development (TDD) approach:

1. **First, write comprehensive tests** that define the expected behavior
2. **Then implement the code** that makes the tests pass
3. **Ensure code quality** with proper error handling, type hints, and docstrings
4. **Follow project patterns** based on existing code structure
5. **Use existing dependencies** where possible

## Output Format
Provide your response in the following format:

### FILES_TO_CREATE_OR_MODIFY
List all files that need to be created or modified with brief descriptions.

### TEST_FILES
For each test file, provide:
```python
# File: path/to/test_file.py
[complete test file content]
```

### IMPLEMENTATION_FILES  
For each implementation file, provide:
```python
# File: path/to/implementation_file.py
[complete implementation file content]
```

### ADDITIONAL_FILES
Any configuration, documentation, or other files needed.

Generate production-ready code that follows Python best practices, includes proper error handling, and integrates well with the existing codebase.
"""

        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01'
        }
        
        data = {
            'model': 'claude-3-5-sonnet-20241022',
            'max_tokens': 4000,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        }
        
        try:
            response = requests.post(self.anthropic_url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            return result['content'][0]['text']
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling Claude API: {e}")
            return f"Error generating code: {e}"
    
    def parse_and_write_files(self, claude_response: str) -> List[str]:
        """Parse Claude's response and write files to disk."""
        created_files = []
        
        # Split response into sections
        sections = claude_response.split('###')
        
        for section in sections:
            if 'TEST_FILES' in section or 'IMPLEMENTATION_FILES' in section or 'ADDITIONAL_FILES' in section:
                # Extract code blocks
                import re
                code_blocks = re.findall(r'```(?:python)?\n# File: (.+?)\n(.*?)\n```', section, re.DOTALL)
                
                for file_path, content in code_blocks:
                    file_path = file_path.strip()
                    content = content.strip()
                    
                    # Create directory if needed
                    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
                    
                    # Write file
                    Path(file_path).write_text(content)
                    created_files.append(file_path)
                    print(f"Created/updated: {file_path}")
        
        return created_files


def main():
    parser = argparse.ArgumentParser(description='Generate code using Claude API')
    parser.add_argument('--pr-number', required=True, help='PR number')
    parser.add_argument('--requirements-file', required=True, help='Requirements JSON file')
    
    args = parser.parse_args()
    
    # Get environment variables
    api_key = os.getenv('ANTHROPIC_API_KEY')
    github_token = os.getenv('GITHUB_TOKEN')
    repo = os.getenv('GITHUB_REPOSITORY')
    
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable not set")
        return 1
    
    if not github_token:
        print("Error: GITHUB_TOKEN environment variable not set")
        return 1
    
    # Load requirements
    try:
        with open(args.requirements_file, 'r') as f:
            requirements = json.load(f)
    except FileNotFoundError:
        print(f"Error: Requirements file {args.requirements_file} not found")
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in requirements file: {e}")
        return 1
    
    # Generate code
    generator = ClaudeCodeGenerator(api_key, github_token, repo)
    
    print(f"Generating code for PR #{args.pr_number}...")
    print(f"Requirements: {len(requirements['requirements'])} items")
    
    # Get Claude's response
    claude_response = generator.generate_code_with_claude(requirements)
    
    # Parse and write files
    created_files = generator.parse_and_write_files(claude_response)
    
    print(f"\nCode generation complete!")
    print(f"Created/modified {len(created_files)} files:")
    for file_path in created_files:
        print(f"  - {file_path}")
    
    # Save Claude's full response for debugging
    with open('claude_response.md', 'w') as f:
        f.write(f"# Claude Response for PR #{args.pr_number}\n\n")
        f.write(f"## Requirements\n```json\n{json.dumps(requirements, indent=2)}\n```\n\n")
        f.write(f"## Claude Response\n{claude_response}\n")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())