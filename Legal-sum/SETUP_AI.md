# AI Analysis Setup Guide

This guide will help you set up GPT-4o-mini integration for legal case analysis.

## Prerequisites

1. Get an OpenAI API key from: https://platform.openai.com/api-keys
2. Ensure you have credits in your OpenAI account

## Setup Instructions

### Windows

1. Open Command Prompt or PowerShell
2. Set the environment variable:
```cmd
set OPENAI_API_KEY=sk-your-api-key-here
```

### Linux/Mac

```bash
export OPENAI_API_KEY=sk-your-api-key-here
```

### Permanent Setup (Windows)

1. Search for "Environment Variables" in Windows Search
2. Click "Edit the system environment variables"
3. Click "Environment Variables"
4. Under "User variables", click "New"
5. Variable name: `OPENAI_API_KEY`
6. Variable value: `sk-your-api-key-here`
7. Click OK and restart your terminal/IDE

### Permanent Setup (Linux/Mac)

Add to your `~/.bashrc` or `~/.zshrc`:
```bash
export OPENAI_API_KEY=sk-your-api-key-here
```

Then reload:
```bash
source ~/.bashrc
```

## Running the Application

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the application:
```bash
python app.py
```

3. Check console output:
   - If you see "✓ AI Analyzer initialized with GPT-4o-mini" - AI analysis is enabled
   - If you see "⚠ AI Analyzer not available" - check your API key setup

## Features

When AI analysis is enabled:
- Automatic case analysis using GPT-4o-mini
- Verdict prediction (Win/Loss/Draw)
- Win probability percentages for both parties
- Identification of legal issues
- Applicable laws and acts
- Strengths and weaknesses analysis
- Detailed reasoning
- Recommended legal strategy

## Cost Estimation

- GPT-4o-mini is OpenAI's most cost-effective model
- Approximately $0.15 per $1M input tokens
- A typical analysis costs around $0.002-0.005 per query
- Very affordable for college projects

## Troubleshooting

### "AI Analyzer not available"
- Check if OPENAI_API_KEY is set
- Verify the API key is valid
- Check console for error messages

### API Errors
- Ensure you have credits in your OpenAI account
- Check API rate limits
- Verify internet connection

## Alternative: Without AI Analysis

The application works perfectly without AI analysis:
- Case summarization still works
- Similarity matching still works
- PDF viewing still works
- Only the AI verdict prediction will be disabled

This is a completely optional feature that enhances the application but is not required for core functionality.

