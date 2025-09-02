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
    
    def read_project_documentation(self) -> Dict[str, str]:
        """Read all project documentation files and return relevant content."""
        project_req_dir = Path('project_requirements')
        docs = {
            'file_list': [],
            'content': ''
        }
        
        if not project_req_dir.exists():
            return {'file_list': '- No project_requirements directory found', 'content': ''}
        
        # Define which docs are most important (include summaries, not full content to save tokens)
        important_docs = {
            'project_plan.md': 'Technical architecture and implementation plan',
            'prd.md': 'Product requirements and business logic',
            'api_specification.md': 'API endpoints and interface contracts',
            'database_schema.md': 'Database design and data models',
            'testing_strategy.md': 'Testing approach and standards',
            'backend_requirements.md': 'Backend system requirements'
        }
        
        content_sections = []
        
        for doc_file, description in important_docs.items():
            doc_path = project_req_dir / doc_file
            if doc_path.exists():
                docs['file_list'].append(f"- {doc_file} ({description})")
                try:
                    # Read first 2000 chars of each doc for better context (increased from 1500)
                    content = doc_path.read_text()[:2000]
                    content_sections.append(f"### {doc_file}\n```\n{content}{'...' if len(doc_path.read_text()) > 2000 else ''}\n```")
                except Exception as e:
                    content_sections.append(f"### {doc_file}\n*Could not read file: {e}*")
        
        docs['file_list'] = '\n'.join(docs['file_list']) if docs['file_list'] else '- No documentation files found'
        docs['content'] = '\n\n'.join(content_sections)
        
        return docs
    
    def generate_code_with_claude(self, requirements: Dict[str, Any]) -> str:
        """Generate code using Claude API with iterative refinement."""
        project_structure = self.read_project_structure()
        existing_tests = self.read_existing_tests()
        
        # Read package files for context
        requirements_txt = ""
        if Path('requirements.txt').exists():
            requirements_txt = Path('requirements.txt').read_text()
        
        pyproject_toml = ""
        if Path('pyproject.toml').exists():
            pyproject_toml = Path('pyproject.toml').read_text()
        
        
        # Read all project documentation for context
        project_docs = self.read_project_documentation()
        
        # Create comprehensive prompt
        prompt = f"""You are an EXPERT Python developer and system architect working on the AI Blog Reviewer project. 

## CRITICAL INSTRUCTIONS
You MUST act as an INDEPENDENT AI AGENT that thinks systematically:

1. **ANALYZES requirements thoroughly** - Break down each requirement into specific, measurable components
2. **BREAKS DOWN complex tasks** - Create a step-by-step implementation plan with clear dependencies
3. **FOLLOWS existing project patterns** - Study the existing code structure and replicate patterns exactly
4. **DELIVERS COMPLETE SOLUTIONS** - Ensure every requirement is fully addressed with working code
5. **EXPLAINS your reasoning** - Provide clear rationale for every architectural and implementation decision
6. **VALIDATES your approach** - Self-check that your solution actually solves the stated problem

## THINKING METHODOLOGY
Use this systematic approach:
- **Step 1**: Read and understand ALL context files completely
- **Step 2**: Analyze each requirement individually - what does it mean, what does it need?
- **Step 3**: Identify dependencies between requirements and existing code
- **Step 4**: Design the solution architecture step by step
- **Step 5**: Plan the implementation order considering dependencies
- **Step 6**: Write comprehensive tests that define expected behavior
- **Step 7**: Implement code that makes tests pass
- **Step 8**: Validate integration with existing codebase

IMPORTANT: Before implementing, please read and understand the full project context from these files:
{project_docs['file_list']}

These files provide critical context for the overall system design, requirements, and technical specifications.

## Key Documentation Context
{project_docs['content']}

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

## YOUR APPROACH - THINK STEP BY STEP
1. **ANALYZE**: Break down requirements into specific, measurable tasks
2. **PLAN**: Design solution architecture considering existing patterns  
3. **DESIGN**: Create detailed implementation plan with dependencies
4. **IMPLEMENT**: Write tests first, then code following TDD
5. **VALIDATE**: Verify each requirement is met with specific checks
6. **INTEGRATE**: Ensure seamless integration with existing codebase

## THINKING PROCESS
Before writing any code, you MUST:
- List each requirement and what it means
- Identify potential challenges and dependencies
- Plan the implementation order
- Consider edge cases and error scenarios
- Design for maintainability and testing

## Output Format
Provide your response in this EXACT format:

### REQUIREMENT_ANALYSIS
Break down each requirement into specific, implementable tasks. For each requirement:
- What does it mean exactly?
- What components does it need?
- What are the dependencies?
- What are potential challenges?

### SOLUTION_ARCHITECTURE
Explain your design decisions and how they integrate with existing code:
- Why did you choose this approach?
- How does it follow existing patterns?
- What alternatives did you consider?
- How does it handle edge cases?

### IMPLEMENTATION_STEPS
List the exact steps you will take to implement the solution:
- Step-by-step breakdown with clear dependencies
- What needs to be built first?
- How do components interact?
- What testing is needed at each step?

### FILES_TO_CREATE_OR_MODIFY
List all files that need to be created or modified with brief descriptions.

### TEST_FILES
```python
# File: path/to/test_file.py
[complete test file content]
```

### IMPLEMENTATION_FILES  
```python
# File: path/to/implementation_file.py
[complete implementation file content]
```

### VALIDATION_CHECKLIST
For each requirement, provide specific validation criteria:
- [ ] Requirement 1: [specific validation - how will you verify this works?]
- [ ] Requirement 2: [specific validation - what test proves this works?]
- [ ] Integration: [how will you verify it works with existing code?]
- [ ] Testing: [what test coverage is needed and why?]
- [ ] Error Handling: [how do you handle failure scenarios?]
- [ ] Performance: [are there any performance considerations?]
- [ ] Security: [are there any security implications?]

### EXPLANATION
Explain your reasoning for each design decision and how this solution addresses the requirements.

### SELF-VALIDATION
After completing your solution, verify each point with specific evidence:
- [ ] Does this solve ALL stated requirements? [List each requirement and how your solution addresses it]
- [ ] Are there any edge cases I missed? [Identify potential edge cases and how you handle them]
- [ ] Does this integrate well with existing code? [Explain how it follows existing patterns and integrates seamlessly]
- [ ] Are my tests comprehensive? [Detail what scenarios your tests cover and why they're sufficient]
- [ ] Is my error handling robust? [Describe error scenarios and how you handle them gracefully]
- [ ] Have I explained my design decisions clearly? [Summarize key decisions and rationale]
- [ ] Is this solution maintainable? [Explain how future developers can understand and modify this code]
- [ ] Are there any performance implications? [Consider scalability and efficiency]

## FINAL INSTRUCTIONS
Remember: You are an independent AI agent. 

**DO NOT START CODING UNTIL YOU HAVE:**
1. ✅ Analyzed ALL requirements thoroughly
2. ✅ Designed the complete solution architecture
3. ✅ Planned the implementation steps
4. ✅ Identified all dependencies and challenges

**THEN:**
1. Write comprehensive tests first (TDD approach)
2. Implement code that makes tests pass
3. Validate against all requirements
4. Ensure seamless integration
5. Provide detailed explanations for every decision

Think through this systematically and deliver a complete, working solution that a senior developer would be proud of.
"""

        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01'
        }
        
        data = {
            'model': 'claude-sonnet-4-20250514',
            'max_tokens': 16000,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        }
        
        try:
            print(f"Making API request to: {self.anthropic_url}")
            print(f"Using model: {data['model']}")
            print(f"API version: {headers['anthropic-version']}")
            
            response = requests.post(self.anthropic_url, headers=headers, json=data, timeout=120)
            
            print(f"Response status: {response.status_code}")
            if response.status_code != 200:
                print(f"Response headers: {response.headers}")
                print(f"Response text: {response.text}")
            
            response.raise_for_status()
            
            result = response.json()
            initial_response = result['content'][0]['text']
            
            # Validate response format and refine if needed
            if not self._validate_response_format(initial_response):
                print("⚠️ Response format incomplete, requesting refinement...")
                refinement_prompt = self._create_refinement_prompt(initial_response, requirements)
                refined_response = self._call_claude_api(refinement_prompt)
                if refined_response and "Error" not in refined_response:
                    return refined_response
            
            return initial_response
            
        except requests.exceptions.RequestException as e:
            print(f"Error calling Claude API: {e}")
            print(f"Full error details: {response.text if 'response' in locals() else 'No response available'}")
            return f"Error generating code: {e}"
    
    def _validate_response_format(self, response: str) -> bool:
        """Validate that response has required sections."""
        required_sections = [
            'REQUIREMENT_ANALYSIS',
            'SOLUTION_ARCHITECTURE', 
            'IMPLEMENTATION_STEPS',
            'TEST_FILES',
            'IMPLEMENTATION_FILES',
            'VALIDATION_CHECKLIST',
            'SELF_VALIDATION'
        ]
        
        for section in required_sections:
            if section not in response:
                return False
        return True
    
    def _create_refinement_prompt(self, incomplete_response: str, requirements: Dict[str, Any]) -> str:
        """Create a prompt to refine incomplete responses."""
        return f"""Your previous response was incomplete. Please provide a COMPLETE response with ALL required sections:

## MISSING SECTIONS
Your response must include these exact sections:
- REQUIREMENT_ANALYSIS
- SOLUTION_ARCHITECTURE  
- IMPLEMENTATION_STEPS
- TEST_FILES
- IMPLEMENTATION_FILES
- VALIDATION_CHECKLIST
- EXPLANATION
- SELF_VALIDATION

## ORIGINAL REQUIREMENTS
{requirements['pr_title']}
{chr(10).join([f"- {req['requirement']}" for req in requirements['requirements']])}

## YOUR INCOMPLETE RESPONSE
{incomplete_response[:1000]}...

Please provide a COMPLETE response with all sections properly formatted.
"""
    
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