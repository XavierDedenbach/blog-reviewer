# GitHub Actions Claude PR Automation Setup

This repository includes automated code generation using Claude AI for pull requests. Here's how to set it up:

## Required GitHub Secrets

You need to configure the following secrets in your GitHub repository settings:

### 1. ANTHROPIC_API_KEY

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create or log into your account
3. Navigate to "API Keys"
4. Create a new API key
5. Copy the key

**Add to GitHub:**
1. Go to your repository on GitHub
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `ANTHROPIC_API_KEY`
5. Value: Paste your Claude API key
6. Click "Add secret"

### 2. GITHUB_TOKEN (Automatic)

The `GITHUB_TOKEN` is automatically provided by GitHub Actions and doesn't need manual configuration.

## How It Works

The automation triggers when:

1. **PR Comments**: Someone comments `@claude` on a pull request
2. **PR Events**: New PRs are opened or updated

### Workflow Steps

1. **Parse Requirements**: Extracts tasks from PR title, description, and comments
2. **Generate Code**: Uses Claude API to generate code following TDD approach
3. **Run Tests**: Executes pytest if available
4. **Commit Changes**: Automatically commits generated code
5. **Update PR**: Comments with results and marks PR ready for review

### Usage Examples

Comment on a PR with:

```
@claude implement the user authentication system with JWT tokens
```

```
@claude add unit tests for the database models
```

```
@claude fix the async endpoint handling bug
```

## File Structure

```
.github/
├── workflows/
│   └── claude-pr-automation.yml  # Main workflow
├── scripts/
│   ├── parse_pr_requirements.py  # Requirement parser
│   └── claude_code_generator.py  # Code generator
└── SETUP.md                      # This file
```

## Testing the Setup

1. Create a test PR
2. Comment `@claude implement a simple hello world function`
3. Check the Actions tab for workflow execution
4. Review generated code and test results

## Troubleshooting

### Common Issues

1. **API Key Not Set**: Ensure `ANTHROPIC_API_KEY` is correctly configured
2. **Permission Errors**: Check that the workflow has necessary permissions
3. **Script Errors**: Review the Actions logs for detailed error messages

### Debug Information

The workflow saves Claude's full response in `claude_response.md` for debugging purposes.

## Customization

### Modifying the Workflow

Edit `.github/workflows/claude-pr-automation.yml` to:
- Change trigger conditions
- Modify test commands
- Adjust commit messages
- Add custom steps

### Updating Scripts

The Python scripts in `.github/scripts/` can be customized:
- `parse_pr_requirements.py`: Modify requirement extraction logic
- `claude_code_generator.py`: Adjust code generation prompts and patterns

## Best Practices

1. **Clear Requirements**: Write detailed PR descriptions and comments
2. **Review Generated Code**: Always review and test Claude's output
3. **Iterative Development**: Use multiple small requests rather than large ones
4. **Test Coverage**: Request tests alongside implementation
5. **Code Standards**: Specify coding standards in comments when needed

## Security Notes

- API keys are stored securely as GitHub secrets
- Generated code is committed with clear attribution
- All API calls are logged in Actions for audit purposes
- No sensitive data is exposed in logs or generated code