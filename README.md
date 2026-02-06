# Continuous Feedback Automation System

An automated workflow for processing annual appraisal data using web scraping and LLM-powered comment generation. This system extracts appraisal information from Ultimatix SPEED platform and generates contextually appropriate comments.

## About

The Continuous Feedback Automation System is designed to streamline the annual appraisal process by automating the most time-consuming aspects: data extraction and comment generation. Built for employees working with the Ultimatix SPEED platform, this tool leverages modern web automation and AI technologies to reduce manual effort while maintaining the personal touch required for meaningful performance feedback.

This project addresses a common pain point in corporate environments where employees need to:
- Manually extract appraisal data from multiple web pages
- Draft thoughtful comments for goals and performance attributes
- Ensure consistency in feedback language while maintaining authenticity
- Spend valuable time on administrative tasks rather than meaningful reflection

By combining Playwright for robust web automation with local LLM capabilities for intelligent comment generation, the system creates a seamless pipeline that preserves employee voice while dramatically reducing the time investment required for annual appraisals.

## Features

- **Web Automation**: Automated login and data extraction from Ultimatix SPEED appraisal system
- **LLM Integration**: AI-powered comment generation based on previous conversations and requirements
- **Data Pipeline**: Structured flow using pocketflow for data processing
- **YAML Storage**: Persistent storage of appraisal data in structured YAML format
- **Cookie Management**: Session persistence for repeated access

## Project Structure

```
ContinousFeedback/
├── speed_appraisal.py      # Main web automation script
├── speed_nodes.py           # Data processing pipeline nodes
├── user_flow.py             # Flow creation utilities
├── utils.py                 # LLM integration utilities
├── pages/                   # Page object models
│   ├── ultimatix_login.py   # Login page automation
│   └── speed_page.py        # SPEED page interactions
└── details/                 # Data storage
    ├── Goals.yaml           # Appraisal goals data
    ├── Attributes.yaml      # Performance attributes
    ├── Settings.yaml        # Appraisal settings
    ├── feed_forward.yaml    # User context data
    ├── users_dict.yaml      # Stakeholder information
    └── final_comments.yaml  # Generated comments
```

## Prerequisites

- Python 3.8+
- Playwright browser automation
- Local LLM server (Ollama with qwen3:4b-instruct-2507-q4_K_M model)
- OpenAI Python library

## Installation

```bash
pip install playwright openai pocketflow pyyaml
playwright install
```

## Setup

1. Start your local LLM server:
```bash
ollama serve
```

2. Configure the LLM endpoint in `utils.py` (default: `http://localhost:11434/v1`)

3. Place your Ultimatix credentials in the script or modify as needed

## Usage

### Web Data Extraction
```bash
python speed_appraisal.py
```
This will:
- Login to Ultimatix SPEED platform
- Extract appraisal goals, attributes, and settings
- Save data to YAML files in the `details/` directory
- Generate comments using LLM
- Fill comments back into the web interface

### Comment Generation Pipeline
```bash
python speed_nodes.py
```
This runs the data processing pipeline:
- Load YAML appraisal data
- Generate contextual comments for each goal/attribute
- Save final comments to `final_comments.yaml`

## Data Flow

1. **Data Extraction**: Web scraping collects appraisal data from SPEED platform
2. **Context Processing**: Previous conversations and requirements are analyzed
3. **Comment Generation**: LLM generates appropriate comments for each appraisal item
4. **Final Review**: Comments are validated and formatted
5. **Output**: Results saved to YAML files and optionally submitted to web interface

## Configuration

Modify the following files as needed:
- `utils.py`: LLM endpoint and model configuration
- `speed_appraisal.py`: Employee ID and browser settings
- `details/`: Template YAML files for data structure

## Key Components

- **DataGatherer**: Collects and categorizes appraisal YAML files
- **CommentsGenerator**: Uses LLM to generate contextual comments
- **CommentFinalizer**: Proofreads and validates generated comments
- **OutputFileWriter**: Persists final results to disk

## Notes

- The system uses a local LLM instance for privacy and cost efficiency
- Cookies are stored for session persistence
- All generated comments follow the employee's voice and conversation context
- The pipeline handles both goals and performance attributes

## Dependencies

- `playwright`: Web browser automation
- `openai`: LLM API interface
- `pocketflow`: Pipeline orchestration
- `pyyaml`: YAML file handling
- `yaml`: YAML data processing