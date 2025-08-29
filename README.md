# Blog Reviewer
Some tooling to increase the quality and diversity of feedback to a blog post

## Project Overview

The blog reviewer provides multiple vectors of review, for purose, for style when compared to writers of your choice, and grammar.
1. **Purpose**: It analyzes the author's stated intent of the blog. Then it evaluates the effectiveness of the blog in articulating the argument
2. **Style**: The author can select up to five authors to provide feedback on your blog in the realm of tone, effectiveness, alignment with their own stated position.
3. **Grammar/tone**: The blog is reviewed for punctuation, confidence and word seletion to improve the clarity of communication.

## Getting Started

### Prerequisites

- Python 3.8+
- MongoDB
- OpenRouter API key
- Brave Search API key (Premium tier)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/blog-accelerator-agent.git
   cd blog-accelerator-agent
   ```

2. Set up the research environment:
   ```
   python setup_research.py
   ```

3. Install dependencies:
   ```
   python setup_research.py --install-deps
   ```

4. Configure your API keys in the `.env` file.

## Project Structure

```
blog-accelerator-agent/
├── tests/
├── agents/
│   ├── reviewer/
│   │   └── __init__.py
│   ├── utilities/
│   │   ├── db.py
│   │   ├── file_ops.py
│   │   ├── source_validator.py
│   │   ├── firecrawl_client.py
│   │   └── yaml_guard.py
│   └── reviewer_agent.py
├── api/
│   ├── main.py
│   └── endpoints/
│       └── review.py
├── data/
│   ├── tracker_yaml/
│   ├── uploads/
│   └── visual_assets/
├── project_requirements/
│   ├── kickoff.md
│   ├── setup_research.py
│   └── tasks.md
│   ├── userflow.md
│   ├── prd.md
│   ├── frontend_requirements.md
│   └── backend_requirements.md
├── storage/
├── docker-compose.yml
├── .env
└── README.md
```

## Running Tests

```bash
pytest tests/
```

## Running the API

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8080
```

Visit http://localhost:8080/docs for the OpenAPI documentation.

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
MONGODB_URI=mongodb://localhost:27017
OPENROUTER_API_KEY=your_openrouter_key
BRAVE_API_KEY=your_brave_key
FIRECRAWL_SERVER=http://localhost:4000
OPIK_SERVER=http://localhost:7000
```