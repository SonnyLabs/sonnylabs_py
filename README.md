# AI Security Scanner: Test Your AI Applications for Prompt Injection Vulnerabilities

Test your AI chatbots and agents for prompt injection vulnerabilities using the SonnyLabs scanning service. Receive a comprehensive vulnerability report by email within 24 hours.

## Table of Contents

- [About](#about)
- [Security Risks in AI Applications](#security-risks-in-ai-applications)
- [Installation](#installation)
- [Pre-requisites](#pre-requisites)
- [Quick 3-Step Integration](#quick-3-step-integration)
- [Prompt to Integrate SonnyLabs to your AI application](#prompt-to-integrate-sonnylabs-to-your-ai-application)
- [Example](#example)
- [API Reference](#api-reference)
- [License](#license)

## About

SonnyLabs.ai is a cybersecurity testing service that scans AI applications for prompt injection vulnerabilities. Our scanner analyzes both user inputs and AI outputs to identify security weaknesses in your AI chatbots and agents. After testing, you'll receive a comprehensive vulnerability report by email within 24 hours.

This package is a simple Python client for the SonnyLabs vulnerability scanning service. There are 10,000 free scanning requests per month for testing your AI applications.

## When to Use SonnyLabs

SonnyLabs is designed specifically for the **testing phase** of your AI development lifecycle, not for production deployment with real users. Implement this tool:

- During pre-deployment security testing
- In dedicated QA/testing environments
- As part of your CI/CD pipeline for automated security testing
- When conducting penetration testing of your AI application
- Before releasing new AI features or models

The goal is to identify and address prompt injection vulnerabilities before your AI application goes live, enhancing your security posture proactively rather than monitoring production traffic.

## Security Risks in AI Applications 

### Prompt Injection
Prompt injections are malicious inputs to AI applications that were designed by the user to manipulate an LLM into ignoring its original instructions or safety controls.

Risks associated with prompt injections:
- Bypassing content filters and safety mechanisms
- Extracting confidential system instructions
- Causing the LLM to perform unauthorized actions
- Compromising application security

The SonnyLabs vulnerability scanner provides a way to test your AI applications for prompt injection vulnerabilities without disrupting user interactions. You'll receive a comprehensive vulnerability report by email within 24 hours, detailing any security weaknesses found in both user inputs and AI responses.

## REST API output example on the input prompt

```json 
{
  "analysis": [
    {
      "type": "score",
      "name": "prompt_injection",
      "result": 0.99
    }
  ],
  "tag": "unique-request-identifier"
}
```

## Installation

The package is available on PyPI and can be installed using pip:

```bash
pip install sonnylabs
```

Alternatively, you can install directly from GitHub for the latest development version:

```bash
pip install git+https://github.com/SonnyLabs/sonnylabs_py
```

Or clone the repository and install locally:

```bash
git clone https://github.com/SonnyLabs/sonnylabs_py
cd sonnylabs_py
pip install -e .
```

## Pre-requisites 
These are the pre-requisites for this package and to use the SonnyLabs REST API.

- Python 3.7 or higher
- An AI application/AI agent to integrate SonnyLabs with
- [A Sonnylabs account](https://sonnylabs-service.onrender.com)
- [A SonnyLabs API key](https://sonnylabs-service.onrender.com/analysis/api-keys)
- [A SonnyLabs analysis ID](https://sonnylabs-service.onrender.com/analysis)   
- Securely store your API key and analysis ID (we recommend using a secure method like environment variables or a secrets manager)

### To register to SonnyLabs

1. Go to https://sonnylabs-service.onrender.com and register. 
2. Confirm your email address, and login to your new SonnyLabs account.

### To get a SonnyLabs API key:
1. Go to [API Keys](https://sonnylabs-service.onrender.com/analysis/api-keys).
2. Select + Generate New API Key.
3. Copy the generated API key.
4. Store this API key securely for use in your application.

### To get a SonnyLabs analysis ID:
1. Go to [Analysis](https://sonnylabs-service.onrender.com/analysis).
2. Create a new analysis and name it after the AI application/AI agent you will be auditing.
3. After you press Submit, you will be brought to the empty analysis page.
4. The analysis ID is the last part of the URL, like https://sonnylabs-service.onrender.com/analysis/{analysis_id}. Note that the analysis ID can also be found in the [SonnyLabs analysis dashboard](https://sonnylabs-service.onrender.com/analysis).
5. Store this analysis ID securely for use in your application.

> **Note:** We recommend storing your API key and analysis ID securely using environment variables or a secrets manager, not hardcoded in your application code.

> **Performance:** The SonnyLabs service operates with sub-200ms latency (one fifth of a second) per prompt input or AI output, ensuring minimal impact on your application's performance while collecting data for vulnerability analysis.

## Quick 3-Step Integration

Getting started with SonnyLabs is simple. The most important function to know is `analyze_text()`, which is the core method for analyzing content for security risks.

### 1. Install and initialize the client

```python
# Install the SDK
pip install sonnylabs

# In your application
from sonnylabs_py import SonnyLabsClient

# Initialize the client with your securely stored credentials
client = SonnyLabsClient(
    api_key="YOUR_API_KEY",  # Replace with your actual API key or use a secure method to retrieve it
    analysis_id="YOUR_ANALYSIS_ID",  # Replace with your actual ID or use a secure method to retrieve it
    base_url="https://sonnylabs-service.onrender.com"  # Optional, this is the default value
)
```

### 2. Analyze input/output with a single function call

```python
# Send user input to the SonnyLabs API without showing results to users
input_result = client.analyze_text("User message here", scan_type="input")

# Process the message normally (no blocking)
ai_response = "AI response here"

# Link AI response with the input using the same tag
output_result = client.analyze_text(ai_response, scan_type="output", tag=input_result["tag"])

# All analysis happens on the backend and results are available in your SonnyLabs dashboard
```

For more advanced usage and complete examples, see the sections below.

## API Reference

This section documents all functions available in the SonnyLabsClient, their parameters, return values, and usage.

### Initialization

```python
SonnyLabsClient(api_key, base_url, analysis_id, timeout=5)
```

**Parameters:**
- `api_key` (str, **required**): Your SonnyLabs API key (previously called api_token, both are supported for backward compatibility).
- `base_url` (str, **required**): Base URL for the SonnyLabs API (e.g., "https://sonnylabs-service.onrender.com").
- `analysis_id` (str, **required**): The analysis ID associated with your application.
- `timeout` (int, optional): Request timeout in seconds. Default is 5 seconds.

### Core Analysis Methods

#### `analyze_text(text, scan_type="input", tag=None)`

**Description:** The primary method for analyzing text content for security risks.

**Parameters:**
- `text` (str, **required**): The text content to analyze.
- `scan_type` (str, optional): Either "input" (user message) or "output" (AI response). Default is "input".
- `tag` (str, optional): A unique identifier for linking related analyses. If not provided, one will be generated.

**Returns:** Dictionary with analysis results:
```python
{
    "success": True,  # Whether the API call was successful
    "tag": "unique_tag",  # The tag used for this analysis
    "analysis": [  # Array of analysis results
        {"type": "score", "name": "prompt_injection", "result": 0.8}
    ]
}
```

### Analysis

All prompt injection analysis is performed on the SonnyLabs backend. You only need to submit your data using the `analyze_text` function. Results will be available in your SonnyLabs dashboard after analysis is complete.



## Prompt to Integrate SonnyLabs to your AI application
Here is an example prompt to give to your IDE's LLM (Cursor, VSCode, Windsurf etc) to integrate the Sonnylabs REST API to your AI application.

```
As an expert AI developer, help me integrate SonnyLabs security auditing into my existing AI application.

I need to implement vulnerability scanning for my AI application:
1. Send test user inputs to SonnyLabs for vulnerability analysis
2. Send my AI's responses to SonnyLabs for security testing
3. Link user prompts with AI responses to identify potential vulnerabilities

I've already installed the SonnyLabs Python SDK using pip and have my API key and analysis ID from the SonnyLabs dashboard.

Please provide a step-by-step implementation guide including:
- How to initialize the SonnyLabs vulnerability scanner client
- How to send test inputs to SonnyLabs for security analysis
- How to send AI outputs to SonnyLabs for vulnerability detection
- How to properly use the 'tag' parameter to link prompts with their responses
- How to integrate this testing process with minimal code changes

Note: I understand that all vulnerability reports will be sent by email within 24 hours and I don't need to process any results directly in my application.
```

### Quick Start
```python
from sonnylabs_py import SonnyLabsClient
import os
from dotenv import load_dotenv

# Load API key from environment (recommended)
load_dotenv()
api_key = os.getenv("SONNYLABS_API_KEY")
analysis_id = os.getenv("SONNYLABS_ANALYSIS_ID")

# Initialize the client with your securely stored credentials
client = SonnyLabsClient(
    api_key=api_key,
    analysis_id=analysis_id,
    base_url="https://sonnylabs-service.onrender.com"  
)

# Analyze text for prompt injection risk (input)
result = client.analyze_text("Hello, how can I help you today?", scan_type="input")
print(f"Prompt injection score: {result['analysis'][0]['result']}")

# If you want to link an input with its corresponding output, change the scan_type from "input" to "output" but reuse the tag:
tag = result["tag"]
response = "I'm an AI assistant, I'd be happy to help!"
output_result = client.analyze_text(response, scan_type="output", tag=tag)
```

## Integrating with a Chatbot
Here's how to integrate the SDK into a Python chatbot to audit all security risks without blocking any messages:

### Set up the client
```python 
from sonnylabs_py import SonnyLabsClient
import os
from dotenv import load_dotenv

# Load environment variables (recommended)
load_dotenv()

# Initialize the SonnyLabs client with your securely stored credentials
sonnylabs_client = SonnyLabsClient(
    api_token=os.getenv("SONNYLABS_API_TOKEN"),
    analysis_id=os.getenv("SONNYLABS_ANALYSIS_ID"),
    base_url="https://sonnylabs-service.onrender.com"
)
```

### Implement message handling with audit-only logging

```python 
def handle_user_message(user_message):
    # Step 1: Send the user message to SonnyLabs (silently, no user-facing results)
    analysis_result = sonnylabs_client.analyze_text(user_message, scan_type="input")
    
    # Step 2: Process the message normally
    bot_response = generate_bot_response(user_message)
    
    # Step 3: Send the AI response using the same tag to link it with the input
    tag = analysis_result["tag"]  # Reuse the tag from the input analysis
    sonnylabs_client.analyze_text(bot_response, scan_type="output", tag=tag)
    
    # No need to process any results as everything is analyzed on the backend
    
    # Always return the response (audit-only mode)
    return bot_response

def generate_bot_response(user_message):
    # Your existing chatbot logic here
    # This could be a call to an LLM API or other response generation logic
    return "This is the chatbot's response"
```

### License
This project is licensed under the MIT License - see the LICENSE file for details.
