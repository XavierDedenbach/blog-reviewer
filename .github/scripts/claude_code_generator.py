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
import time
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
                    # Handle the conditional content separately to avoid quote conflicts
                    ellipsis = "..." if len(doc_path.read_text()) > 2000 else ""
                    content_sections.append(f"### {doc_file}\n```\n{content}{ellipsis}\n```")
                except Exception as e:
                    content_sections.append(f"### {doc_file}\n*Could not read file: {e}*")
        
        docs['file_list'] = '\n'.join(docs['file_list']) if docs['file_list'] else '- No documentation files found'
        docs['content'] = '\n\n'.join(content_sections)
        
        return docs
    
    def generate_code_with_claude(self, requirements: Dict[str, Any], iteration: int = 1, test_failures: str = '') -> str:
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
{chr(10).join([f"- {req['requirement']} (from {req.get('source', 'unknown')})" for req in requirements['requirements']])}

Test Required: {requirements['test_required']}
Documentation Required: {requirements['documentation_required']}

## Previous Work Context
{self._format_previous_work_context()}

## TDD Iteration Context
Current Iteration: {iteration}
{f"Previous Test Failures:" if test_failures else "First iteration - writing initial tests and implementation"}
{f"```" if test_failures else ""}
{f"{test_failures}" if test_failures else ""}
{f"```" if test_failures else ""}

## YOUR APPROACH - THINK STEP BY STEP
{f"**ITERATION {iteration} - FIXING FAILING TESTS**" if test_failures else "**ITERATION {iteration} - INITIAL IMPLEMENTATION**"}

1. **ANALYZE**: Break down requirements into specific, measurable tasks
2. **PLAN**: Design solution architecture considering existing patterns  
3. **DESIGN**: Create detailed implementation plan with dependencies
4. **IMPLEMENT**: Write tests first, then code following TDD
5. **VALIDATE**: Verify each requirement is met with specific checks
6. **INTEGRATE**: Ensure seamless integration with existing codebase

{f"**SPECIAL INSTRUCTIONS FOR ITERATION {iteration}:**" if iteration > 1 else ""}
{f"**FOCUS ON FIXING THESE TEST FAILURES:**" if test_failures else ""}
{f"```" if test_failures else ""}
{f"{test_failures}" if test_failures else ""}
{f"```" if test_failures else ""}
{f"**DO NOT REPEAT WORK:** Build upon existing implementation, fix what's broken" if iteration > 1 else ""}

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
2. **CRITICAL: Implement the ACTUAL CODE that makes tests pass**
3. **DO NOT just write tests - you MUST create implementation files**
4. Validate against all requirements
5. Ensure seamless integration
6. Provide detailed explanations for every decision

**IMPORTANT: You must generate BOTH test files AND implementation files.**
**Tests alone are not enough - you need working code that passes those tests.**

Think through this systematically and deliver a complete, working solution that a senior developer would be proud of.
"""

        # Always start fresh with full context for better results
        print("🔄 Starting fresh with full project context...")
        
        # Load previous work from DEVELOPMENT_LOG.md if it exists
        previous_work = self._load_previous_work()
        if previous_work:
            print(f"📚 Found previous work: {len(previous_work['completed_items'])} items completed")
            print(f"📋 Remaining work: {len(previous_work['missing_items'])} items to complete")
        else:
            print("🆕 No previous work found, starting from scratch")
        
        # Use retry logic for initial API calls
        print("📡 Making initial API request to Claude with retry logic...")
        initial_response = self._make_claude_request_with_retry(prompt)
        
        # Check if API call failed
        if initial_response is None:
            print("❌ Claude API call failed after all retry attempts")
            print("💾 Progress saved for manual resume")
            return None
        
        # Validate response format and continue if incomplete
        if not self._validate_response_format(initial_response):
            print("⚠️ Response format incomplete, continuing in chunks...")
            
            # Save current progress
            self._save_progress(initial_response, requirements, attempt=1)
            
            # Continue with continuation prompt
            continuation_prompt = self._create_continuation_prompt(initial_response, requirements)
            continued_response = self._make_claude_request_with_retry(continuation_prompt)
            
            if continued_response is None:
                print("❌ Continuation failed, progress saved for manual resume")
                return None
            
            # Combine responses
            full_response = initial_response + "\n\n" + continued_response
            
            # Check if we need more chunks
            if not self._validate_response_format(full_response):
                print("⚠️ Still incomplete, saving progress for manual resume...")
                self._save_progress(full_response, requirements, attempt=2)
                return full_response  # Return what we have so far
            
            # Additional validation: Check if implementation is actually complete
            validation_result = self._validate_implementation_completeness(full_response, requirements)
            if not validation_result['complete']:
                print(f"⚠️ Response format complete but implementation incomplete ({validation_result['overall_score']:.1f}%)")
                print("💾 Saving progress for manual resume...")
                self._save_progress(full_response, requirements, attempt=2)
                return full_response  # Return what we have so far
            
            print(f"✅ Successfully completed response in chunks with full implementation")
            return full_response
        
        return initial_response
    
    def _make_claude_request_with_retry(self, prompt: str, max_retries: int = 3) -> str:
        """Make a request to Claude API with retry logic and intelligent error handling."""
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01'
        }
        
        data = {
            'model': 'claude-sonnet-4-20250514',
            'max_tokens': 8000,  # Stay within 8K output tokens/minute limit
            'messages': [
                {
                    'role': 'user',
                    'content': prompt  # Full prompt allowed (within 30K input tokens/minute)
                }
            ]
        }
        
        for attempt in range(max_retries):
            try:
                print(f"Making API request to: {self.anthropic_url} (attempt {attempt + 1}/{max_retries})")
                print(f"Using model: {data['model']}")
                print(f"API version: {headers['anthropic-version']}")
                print(f"Max tokens: {data['max_tokens']}")
                
                # Exponential backoff: 300s, 600s, 900s
                timeout = 300 + (attempt * 300)
                print(f"Timeout set to: {timeout} seconds")
                
                response = requests.post(self.anthropic_url, headers=headers, json=data, timeout=timeout)
                
                print(f"Response status: {response.status_code}")
                if response.status_code != 200:
                    print(f"Response headers: {response.headers}")
                    print(f"Response text: {response.text[:500]}...")  # Truncate long responses
                
                # Handle specific HTTP status codes
                if response.status_code == 429:  # Rate limit
                    print(f"⚠️ Rate limit hit on attempt {attempt + 1}")
                    
                    # Show current rate limit status
                    if 'anthropic-ratelimit-output-tokens-remaining' in response.headers:
                        remaining = response.headers['anthropic-ratelimit-output-tokens-remaining']
                        limit = response.headers.get('anthropic-ratelimit-output-tokens-limit', 'unknown')
                        reset = response.headers.get('anthropic-ratelimit-output-tokens-reset', 'unknown')
                        print(f"   - Output tokens remaining: {remaining}/{limit}")
                        print(f"   - Reset time: {reset}")
                    
                    if 'retry-after' in response.headers:
                        retry_after = int(response.headers['retry-after'])
                        print(f"   - API suggests waiting {retry_after} seconds")
                        if attempt < max_retries - 1:
                            # For rate limits, always respect the API's retry-after suggestion
                            wait_time = retry_after + 5  # Add 5 seconds buffer
                            print(f"   - Waiting {wait_time} seconds (API suggestion + buffer) before retry...")
                            import time
                            time.sleep(wait_time)
                            continue
                        else:
                            print(f"❌ All retry attempts failed due to rate limiting")
                            print(f"   - Last API suggestion was to wait {retry_after} seconds")
                            return None
                    else:
                        if attempt < max_retries - 1:
                            wait_time = (2 ** attempt) * 30  # Longer wait for rate limits
                            print(f"   - Waiting {wait_time} seconds before retry...")
                            import time
                            time.sleep(wait_time)
                            continue
                        else:
                            print(f"❌ All retry attempts failed due to rate limiting")
                            return None
                
                elif response.status_code == 503:  # Service unavailable
                    print(f"⚠️ Service unavailable on attempt {attempt + 1}")
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) * 15  # Moderate wait for server issues
                        print(f"Waiting {wait_time} seconds before retry...")
                        import time
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"❌ All retry attempts failed due to service unavailability")
                        return None
                
                response.raise_for_status()
                
                result = response.json()
                initial_response = result['content'][0]['text']
                
                # Log token usage if available
                if 'usage' in result:
                    usage = result['usage']
                    input_tokens = usage.get('input_tokens', 'unknown')
                    output_tokens = usage.get('output_tokens', 'unknown')
                    print(f"   - Input tokens used: {input_tokens}")
                    print(f"   - Output tokens used: {output_tokens}")
                
                print(f"✅ API request successful on attempt {attempt + 1}")
                return initial_response
                
            except requests.exceptions.Timeout as e:
                print(f"⚠️ Timeout error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 10  # Longer wait for timeouts
                    print(f"Waiting {wait_time} seconds before retry...")
                    import time
                    time.sleep(wait_time)
                else:
                    print(f"❌ All retry attempts failed due to timeout")
                    return None
                    
            except requests.exceptions.RequestException as e:
                print(f"❌ Request error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 10
                    print(f"Waiting {wait_time} seconds before retry...")
                    import time
                    time.sleep(wait_time)
                else:
                    print(f"❌ All retry attempts failed")
                    return None
        
        return None  # Return None to indicate failure
    
    def _save_progress(self, response: str, requirements: Dict[str, Any], attempt: int = 1) -> None:
        """Save partial response progress for resuming later."""
        progress = {
            'timestamp': time.time(),
            'pr_title': requirements.get('pr_title', 'Unknown'),
            'response': response,
            'attempt': attempt,
            'status': 'partial'
        }
        
        with open('claude_progress.json', 'w') as f:
            json.dump(progress, f, indent=2)
        
        print(f"💾 Progress saved to claude_progress.json")
    
    def _load_progress(self) -> Optional[Dict[str, Any]]:
        """Load saved progress if available."""
        if 'claude_progress.json' in os.listdir('.'):
            try:
                with open('claude_progress.json', 'r') as f:
                    progress = json.load(f)
                print(f"📂 Loaded progress from claude_progress.json")
                return progress
            except Exception as e:
                print(f"⚠️ Could not load progress: {e}")
        return None
    
    def _create_continuation_prompt(self, partial_response: str, requirements: Dict[str, Any]) -> str:
        """Create a prompt to continue from where we left off."""
        return f"""Please continue your response from where you left off. 

## ORIGINAL REQUIREMENTS
{requirements.get('pr_title', 'Unknown PR')}

## YOUR PARTIAL RESPONSE (CONTINUE FROM HERE)
{partial_response[-2000:]}...

## INSTRUCTIONS
- Continue exactly where you left off
- Complete any incomplete sections
- Maintain the same format and style
- Focus on completing the remaining requirements
- Do not repeat what you've already written

Please continue with the next section or complete the current one."""
    
    def resume_from_progress(self, requirements: Dict[str, Any]) -> str:
        """Resume generation from saved progress."""
        progress = self._load_progress()
        if not progress:
            print("❌ No saved progress found")
            return None
        
        print(f"🔄 Resuming from progress saved at {time.ctime(progress['timestamp'])}")
        
        # Continue with continuation prompt
        continuation_prompt = self._create_continuation_prompt(progress['response'], requirements)
        continued_response = self._make_claude_request_with_retry(continuation_prompt)
        
        if continued_response is None:
            print("❌ Continuation failed, progress updated for next attempt")
            return None
        
        # Combine responses
        full_response = progress['response'] + "\n\n" + continued_response
        
        # Check if complete
        if self._validate_response_format(full_response):
            print("✅ Successfully completed response from progress")
            # Clean up progress file
            if 'claude_progress.json' in os.listdir('.'):
                os.remove('claude_progress.json')
                print("🧹 Progress file cleaned up")
            return full_response
        else:
            print("⚠️ Still incomplete, progress updated for next attempt")
            self._save_progress(full_response, requirements, progress['attempt'] + 1)
            return full_response
    
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
    
    def _validate_implementation_completeness(self, response: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that all requirements have been implemented."""
        validation_result = {
            'complete': False,
            'missing_items': [],
            'completed_items': [],
            'overall_score': 0
        }
        
        # Extract requirements list
        req_list = requirements.get('requirements', [])
        if not req_list:
            validation_result['missing_items'].append('No requirements found to validate')
            return validation_result
        
        total_requirements = len(req_list)
        completed_count = 0
        
        for req in req_list:
            req_text = req.get('requirement', '').lower()
            req_id = req.get('id', 'Unknown')
            
            # Check if this requirement is addressed in the response
            if self._requirement_implemented(req_text, response):
                validation_result['completed_items'].append(f"✅ {req_id}: {req_text}")
                completed_count += 1
            else:
                validation_result['missing_items'].append(f"❌ {req_id}: {req_text}")
        
        # Calculate completion score
        validation_result['overall_score'] = (completed_count / total_requirements) * 100
        validation_result['complete'] = validation_result['overall_score'] >= 90  # 90% threshold
        
        return validation_result
    
    def _requirement_implemented(self, requirement: str, response: str) -> bool:
        """Check if a specific requirement is implemented in the response."""
        # Convert to lowercase for comparison
        req_lower = requirement.lower()
        resp_lower = response.lower()
        
        # Check for key indicators of implementation
        implementation_indicators = [
            'class', 'def ', 'import ', 'from ', 'async def', 'async with',
            'def test_', 'class Test', 'pytest', 'unittest',
            'def main', 'if __name__', 'return ', 'raise ',
            'try:', 'except:', 'finally:', 'with open'
        ]
        
        # Check if requirement keywords are present
        req_keywords = [word for word in req_lower.split() if len(word) > 3]
        keywords_found = sum(1 for keyword in req_keywords if keyword in resp_lower)
        
        # Check if implementation code is present (not just tests)
        has_implementation = any(indicator in resp_lower for indicator in implementation_indicators)
        
        # CRITICAL: Check for actual implementation files, not just tests
        has_impl_files = (
            'implementation_files' in resp_lower or
            'models.py' in resp_lower or
            'state_manager.py' in resp_lower or
            'task_queue.py' in resp_lower or
            'orchestrator.py' in resp_lower
        )
        
        # Requirement is implemented if:
        # 1. Most keywords are found AND
        # 2. Implementation code is present AND
        # 3. We have actual implementation files (not just tests)
        keyword_threshold = max(1, len(req_keywords) * 0.6)  # 60% of keywords
        
        return (keywords_found >= keyword_threshold and 
                has_implementation and 
                has_impl_files)
    
    def _create_development_log(self, response: str, requirements: Dict[str, Any], validation_result: Dict[str, Any]) -> str:
        """Create a development log tracking all changes and completion status."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S UTC')
        
        log_content = f"""# Development Log - {requirements.get('pr_title', 'Unknown PR')}

## 📅 Generated: {timestamp}
## 🎯 PR: {requirements.get('pr_title', 'Unknown PR')}
## 📋 Requirements: {len(requirements.get('requirements', []))} total

## ✅ Completion Status
**Overall Score: {validation_result['overall_score']:.1f}%**
**Status: {'🟢 COMPLETE' if validation_result['complete'] else '🟡 INCOMPLETE'}**

### ✅ Completed Requirements ({len(validation_result['completed_items'])})
{chr(10).join(validation_result['completed_items'])}

### ❌ Missing Requirements ({len(validation_result['missing_items'])})
{chr(10).join(validation_result['missing_items'])}

## 📁 Generated Files
{self._extract_generated_files(response)}

## 🔍 Implementation Details
{self._extract_implementation_summary(response)}

## 📝 Notes
- Generated by Enhanced Claude AI Agent
- Validation threshold: 90% completion required
- This log must show 90%+ completion for commit approval

---
*Last updated: {timestamp}*
"""
        return log_content
    
    def _extract_generated_files(self, response: str) -> str:
        """Extract list of generated files from Claude's response."""
        files_section = ""
        
        # Look for TEST_FILES section
        if 'TEST_FILES' in response:
            test_start = response.find('TEST_FILES')
            test_end = response.find('###', test_start + 1) if '###' in response[test_start:] else len(response)
            test_section = response[test_start:test_end]
            files_section += f"### Test Files\n{test_section}\n\n"
        
        # Look for IMPLEMENTATION_FILES section
        if 'IMPLEMENTATION_FILES' in response:
            impl_start = response.find('IMPLEMENTATION_FILES')
            impl_end = response.find('###', impl_start + 1) if '###' in response[impl_start:] else len(response)
            impl_section = response[impl_start:impl_end]
            files_section += f"### Implementation Files\n{impl_section}\n\n"
        
        return files_section if files_section else "No file sections found in response"
    
    def _extract_implementation_summary(self, response: str) -> str:
        """Extract implementation summary from Claude's response."""
        summary = ""
        
        # Look for key sections
        sections = ['REQUIREMENT_ANALYSIS', 'SOLUTION_ARCHITECTURE', 'IMPLEMENTATION_STEPS']
        
        for section in sections:
            if section in response:
                section_start = response.find(section)
                section_end = response.find('###', section_start + 1) if '###' in response[section_start:] else len(response)
                section_content = response[section_start:section_end]
                summary += f"### {section}\n{section_content[:500]}...\n\n"
        
        return summary if summary else "No implementation details found"
    
    def _load_previous_work(self) -> Optional[Dict[str, Any]]:
        """Load previous work from DEVELOPMENT_LOG.md if it exists."""
        import os
        
        if not os.path.exists('DEVELOPMENT_LOG.md'):
            return None
        
        try:
            with open('DEVELOPMENT_LOG.md', 'r') as f:
                content = f.read()
            
            # Parse the development log to extract completion status
            previous_work = {
                'completed_items': [],
                'missing_items': [],
                'overall_score': 0,
                'generated_files': '',
                'implementation_details': ''
            }
            
            # Extract completed items
            if '### ✅ Completed Requirements' in content:
                completed_start = content.find('### ✅ Completed Requirements')
                completed_end = content.find('### ❌ Missing Requirements')
                if completed_end == -1:
                    completed_end = content.find('## 📁 Generated Files')
                
                if completed_end != -1:
                    completed_section = content[completed_start:completed_end]
                    # Extract individual completed items
                    lines = completed_section.split('\n')
                    for line in lines:
                        if line.strip().startswith('✅'):
                            previous_work['completed_items'].append(line.strip())
            
            # Extract missing items
            if '### ❌ Missing Requirements' in content:
                missing_start = content.find('### ❌ Missing Requirements')
                missing_end = content.find('## 📁 Generated Files')
                
                if missing_end != -1:
                    missing_section = content[missing_start:missing_end]
                    # Extract individual missing items
                    lines = missing_section.split('\n')
                    for line in lines:
                        if line.strip().startswith('❌'):
                            previous_work['missing_items'].append(line.strip())
            
            # Extract generated files
            if '## 📁 Generated Files' in content:
                files_start = content.find('## 📁 Generated Files')
                files_end = content.find('## 🔍 Implementation Details')
                if files_end == -1:
                    files_end = content.find('## 📝 Notes')
                
                if files_end != -1:
                    previous_work['generated_files'] = content[files_start:files_end].strip()
            
            # Extract implementation details
            if '## 🔍 Implementation Details' in content:
                impl_start = content.find('## 🔍 Implementation Details')
                impl_end = content.find('## 📝 Notes')
                
                if impl_end != -1:
                    previous_work['implementation_details'] = content[impl_start:impl_end].strip()
            
            return previous_work
            
        except Exception as e:
            print(f"⚠️ Warning: Could not parse DEVELOPMENT_LOG.md: {e}")
            return None
    
    def _format_previous_work_context(self) -> str:
        """Format previous work context for inclusion in the prompt."""
        previous_work = self._load_previous_work()
        
        if not previous_work:
            return "No previous work found - starting fresh implementation."
        
        context = f"""Previous development session found with the following progress:

### ✅ Previously Completed ({len(previous_work['completed_items'])} items)
{chr(10).join(previous_work['completed_items'][:10])}  # Show first 10 items

### ❌ Still Need to Implement ({len(previous_work['missing_items'])} items)
{chr(10).join(previous_work['missing_items'][:10])}  # Show first 10 items

### 📁 Previously Generated Files
{previous_work['generated_files'][:1000]}...

### 🔍 Previous Implementation Details
{previous_work['implementation_details'][:1000]}...

**IMPORTANT**: Build upon this existing work. Do not recreate what's already done.
Focus on implementing the missing requirements and improving existing code if needed."""
        
        return context
    
    def run_tdd_iterations(self, initial_response: str, requirements: Dict[str, Any], created_files: List[str]) -> str:
        """Run TDD iterations: tests → fail → fix → tests → pass."""
        print("🔄 Starting TDD Iteration Process...")
        
        max_iterations = 10
        current_response = initial_response
        
        for iteration in range(1, max_iterations + 1):
            print(f"\n🔄 TDD Iteration {iteration}/{max_iterations}")
            
            # Check if we have tests to run
            if not any(f.endswith('.py') and 'test' in f.lower() for f in created_files):
                print("📝 No test files found, skipping TDD iterations")
                break
            
            # Run tests
            print("📋 Running tests...")
            try:
                import subprocess
                
                # Use unittest (always available, no installation needed)
                print("🧪 Using Python's built-in unittest framework")
                
                result = subprocess.run(['python', '-m', 'unittest', 'discover', '-v'], 
                                      capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print("✅ All tests passed!")
                    print("🎉 TDD Process Complete - Implementation successful!")
                    return current_response
                else:
                    print(f"❌ Tests failed on iteration {iteration}")
                    print("Test output:")
                    print("STDOUT:")
                    print(result.stdout[-2000:] if result.stdout else "No stdout")
                    print("\nSTDERR:")
                    print(result.stderr[-1000:] if result.stderr else "No stderr")
                    
                    # Show test failure summary (unittest format)
                    if result.stdout:
                        # Count tests run and failed
                        lines = result.stdout.split('\n')
                        tests_run = 0
                        tests_failed = 0
                        tests_errors = 0
                        
                        for line in lines:
                            if 'test' in line.lower() and ('ok' in line.lower() or 'passed' in line.lower()):
                                tests_run += 1
                            elif 'fail' in line.lower():
                                tests_failed += 1
                            elif 'error' in line.lower():
                                tests_errors += 1
                        
                        print(f"\n📊 Test Summary: {tests_run} tests run, {tests_failed} failed, {tests_errors} errors")
                        
                        # Extract specific test failures
                        failed_tests = []
                        for line in lines:
                            if any(keyword in line.lower() for keyword in ['fail', 'error', 'exception']):
                                failed_tests.append(line.strip())
                        
                        if failed_tests:
                            print("🔍 Specific Test Failures:")
                            for test in failed_tests[:5]:  # Show first 5 failures
                                print(f"  - {test}")
                    
                    if iteration < max_iterations:
                        print("🔄 Tests failed, triggering next iteration...")
                        
                        # Create continuation prompt with test failures
                        test_failures = f"STDOUT:\n{result.stdout[-2000:] if result.stdout else 'No stdout'}\n\nSTDERR:\n{result.stderr[-1000:] if result.stderr else 'No stderr'}"
                        continuation_prompt = self._create_tdd_continuation_prompt(current_response, requirements, test_failures, iteration)
                        
                        # Get Claude to fix the failing tests
                        fixed_response = self._make_claude_request_with_retry(continuation_prompt)
                        
                        if fixed_response:
                            # Combine responses
                            current_response = current_response + "\n\n" + fixed_response
                            
                            # Re-parse and write files
                            new_files = self.parse_and_write_files(fixed_response)
                            created_files.extend(new_files)
                            
                            print(f"📝 Claude made fixes, continuing to iteration {iteration + 1}")
                        else:
                            print("❌ Claude failed to provide fixes, stopping TDD iterations")
                            break
                    else:
                        print("⚠️ Maximum iterations reached, stopping TDD iterations")
                        break
                        
            except subprocess.TimeoutExpired:
                print("⏰ Test execution timed out, stopping TDD iterations")
                break
            except Exception as e:
                print(f"❌ Error running tests: {e}")
                break
        
        print("🏁 TDD Iteration Process Complete")
        return current_response
    
    def _create_tdd_continuation_prompt(self, current_response: str, requirements: Dict[str, Any], test_failures: str, iteration: int) -> str:
        """Create a prompt for Claude to fix failing tests in TDD iterations."""
        return f"""You are continuing TDD iteration {iteration}. The tests are failing and need to be fixed.

## CRITICAL: YOU MUST GENERATE IMPLEMENTATION CODE

The tests are failing because you haven't implemented the actual classes and functions. 
You need to create the IMPLEMENTATION files, not just fix tests.

## ORIGINAL REQUIREMENTS
{requirements.get('pr_title', 'Unknown PR')}
{requirements.get('requirements', [])}

## PREVIOUS WORK CONTEXT
{self._format_previous_work_context()}

## TEST FAILURES (Fix These)
{test_failures}

## WHAT YOU MUST DO
1. **ANALYZE** the test failures to understand what's missing
2. **IMPLEMENT** the actual classes and functions that the tests are expecting
3. **CREATE** implementation files (not just test files)
4. **ENSURE** the implementation matches the test expectations

## IMPLEMENTATION PRIORITY
Focus on creating these core implementation files:
- `review_orchestrator/__init__.py` - Main package
- `review_orchestrator/models.py` - Data models
- `review_orchestrator/state_manager.py` - State management
- `review_orchestrator/task_queue.py` - Task queuing
- `review_orchestrator/orchestrator.py` - Main orchestrator

## OUTPUT FORMAT
Provide ONLY the implementation code in this format:

### IMPLEMENTATION_FILES

#### `review_orchestrator/models.py`
```python
# Your implementation here
```

#### `review_orchestrator/state_manager.py`
```python
# Your implementation here
```

Continue with all required implementation files. DO NOT just fix tests - IMPLEMENT THE ACTUAL CODE.

## INSTRUCTIONS
1. **ANALYZE** the test failures carefully
2. **IDENTIFY** what's wrong with the current implementation
3. **FIX** the implementation to make tests pass
4. **ONLY** provide the fixed/updated code sections
5. **DO NOT** repeat the entire response
6. **FOCUS** on making the failing tests pass

## OUTPUT FORMAT
Provide ONLY the corrected implementation sections:

### IMPLEMENTATION_FILES (Updated)
```python
# File: path/to/fixed_file.py
[fixed implementation code]
```

### ADDITIONAL_FILES (If needed)
```python
# File: path/to/new_file.py
[new implementation code]
```

Make the tests pass with minimal, targeted changes."""
    
    def _create_refinement_prompt(self, incomplete_response: str, requirements: Dict[str, Any]) -> str:
        """Create a prompt to refine incomplete responses."""
        # Safely extract requirements with fallbacks
        pr_title = requirements.get('pr_title', 'Unknown PR')
        requirements_list = requirements.get('requirements', [])
        
        # Build requirements text safely
        if isinstance(requirements_list, list) and len(requirements_list) > 0:
            req_text = chr(10).join([f"- {req.get('requirement', 'Unknown requirement')}" for req in requirements_list])
        else:
            req_text = "- No specific requirements found"
        
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
{pr_title}
{req_text}

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
    parser.add_argument('--resume', action='store_true', help='Resume from saved progress')
    parser.add_argument('--iteration', type=int, default=1, help='Current TDD iteration number')
    parser.add_argument('--test-failures', type=str, default='', help='Test failure output for iteration')
    
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
        
        # Validate requirements structure
        print(f"📋 Requirements loaded successfully")
        print(f"   - Type: {type(requirements)}")
        print(f"   - Keys: {list(requirements.keys()) if isinstance(requirements, dict) else 'Not a dict'}")
        if isinstance(requirements, dict):
            print(f"   - PR Title: {requirements.get('pr_title', 'Missing')}")
            print(f"   - Requirements count: {len(requirements.get('requirements', []))}")
        
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
    
    # Check if we should resume from progress
    if args.resume:
        print("🔄 Resuming from saved progress...")
        claude_response = generator.resume_from_progress(requirements)
    else:
        # Get Claude's response
        print(f"🔄 Starting TDD Iteration {args.iteration}")
        if args.test_failures:
            print(f"📋 Previous test failures detected, fixing implementation...")
        claude_response = generator.generate_code_with_claude(requirements, args.iteration, args.test_failures)
    
    # Check if Claude API call failed
    if claude_response is None:
        print("❌ ERROR: Claude API call failed completely")
        print("💾 Progress has been saved to claude_progress.json")
        print("🔄 To resume later, run: python .github/scripts/claude_code_generator.py --resume --pr-number X --requirements-file Y")
        print("The workflow should fail to prevent false positive commits.")
        return 1
    
    # Parse and write files
    created_files = generator.parse_and_write_files(claude_response)
    
    print(f"\nCode generation complete!")
    print(f"Created/modified {len(created_files)} files:")
    for file_path in created_files:
        print(f"  - {file_path}")
    
    # TDD: Run tests and iterate if needed
    if args.iteration == 1:  # Only do TDD iterations on first run
        print("\n🧪 Starting TDD Iteration Process...")
        final_response = generator.run_tdd_iterations(claude_response, requirements, created_files)
        if final_response:
            claude_response = final_response
            # Re-parse files after TDD iterations
            created_files = generator.parse_and_write_files(claude_response)
            print(f"\n🔄 TDD Complete! Final files:")
            for file_path in created_files:
                print(f"  - {file_path}")
    
    # STRICT VALIDATION: Check implementation completeness
    print("\n🔍 Validating implementation completeness...")
    validation_result = generator._validate_implementation_completeness(claude_response, requirements)
    
    print(f"📊 Completion Score: {validation_result['overall_score']:.1f}%")
    print(f"✅ Completed: {len(validation_result['completed_items'])} requirements")
    print(f"❌ Missing: {len(validation_result['missing_items'])} requirements")
    
    # Create development log
    development_log = generator._create_development_log(claude_response, requirements, validation_result)
    with open('DEVELOPMENT_LOG.md', 'w') as f:
        f.write(development_log)
    
    print(f"📝 Development log saved to DEVELOPMENT_LOG.md")
    
    # STRICT COMPLETION CHECK: Must be 90%+ complete
    if not validation_result['complete']:
        print("❌ ERROR: Implementation is INCOMPLETE!")
        print(f"   - Required: 90% completion")
        print(f"   - Actual: {validation_result['overall_score']:.1f}% completion")
        print("   - Missing requirements:")
        for missing in validation_result['missing_items'][:5]:  # Show first 5
            print(f"     {missing}")
        if len(validation_result['missing_items']) > 5:
            print(f"     ... and {len(validation_result['missing_items']) - 5} more")
        
        print("\n💾 Progress saved to DEVELOPMENT_LOG.md")
        print("🔄 To resume and complete missing requirements, run with --resume flag")
        print("The workflow should fail to prevent incomplete commits.")
        return 1
    
    # Validate that actual implementation files were created
    if len(created_files) == 0:
        print("❌ ERROR: No implementation files were created!")
        print("This indicates the Claude script failed to generate actual code.")
        print("The workflow should fail to prevent false positive commits.")
        return 1
    
    # Check for actual Python files (not just markdown)
    python_files = [f for f in created_files if f.endswith('.py')]
    if len(python_files) == 0:
        print("❌ ERROR: No Python implementation files were created!")
        print("Only markdown files were generated, which indicates failure.")
        return 1
    
    print(f"✅ Successfully created {len(created_files)} files including {len(python_files)} Python files")
    print(f"🎉 IMPLEMENTATION COMPLETE: {validation_result['overall_score']:.1f}% requirements satisfied!")
    
    # Save Claude's full response for debugging
    with open('claude_response.md', 'w') as f:
        f.write(f"# Claude Response for PR #{args.pr_number}\\n\\n")
        f.write(f"## Requirements\\n```json\\n{json.dumps(requirements, indent=2)}\\n```\\n\\n")
        f.write(f"## Claude Response\\n{claude_response}\\n")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())