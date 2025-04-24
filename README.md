# Detect Prompt Injections & PII in AI agents using SonnyLabs Python Client

Detect prompt injections and PII in real-time in your AI applications using the SonnyLabs REST API.

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

SonnyLabs.ai is a cybersecurity REST API that provides security protection for AI applications. It can be used to detect the risk of prompt injection and PII in prompts and LLM responses, especially useful for securing AI applications and AI agents.

This package is a simple Python client for the SonnyLabs REST API. There are 10,000 free requests to the REST API per month.

## Security Risks in AI Applications 

### Prompt Injection
Prompt injections are malicious inputs to AI applications that were designed by the user to manipulate an LLM into ignoring its original instructions or safety controls.

Risks associated with prompt injections:
- Bypassing content filters and safety mechanisms
- Extracting confidential system instructions
- Causing the LLM to perform unauthorized actions
- Compromising application security

### PII
PII (Personally Identifiable Information) refers to any information that can be used to identify an individual, such as their name, email address, phone number, or social security number.

Risks associated with PII:
- Unauthorized access to personal information
- Data breaches and identity theft
- Unauthorized disclosure of sensitive information
- Unauthorized modification of personal data

The SonnyLabs REST API provides a way to detect prompt injections and PII in real-time in your AI applications. 

## REST API output example

```json 
{
  "analysis": [
    {
      "type": "score",
      "name": "prompt_injection",
      "result": 0.99
    },    {
      "type": "PII",
      "result": [
        {"label": "EMAIL", "text": "example@email.com"},
        {"label": "PHONE", "text": "123-456-7890"}
      ]
    }
  ],
  "tag": "unique-request-identifier"
}
```

## Installation

The package will soon be available on PyPI, but you can now install it on your system directly from GitHub:

```bash
pip install git+https://github.com/SonnyLabs/sonnylabs_py
```

Alternatively, you can clone the repository and install locally:

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
- [A SonnyLabs API token](https://sonnylabs-service.onrender.com/analysis/api-keys)
- [A SonnyLabs analysis ID](https://sonnylabs-service.onrender.com/analysis)   
- Securely store your API token and analysis ID (we recommend using a secure method like environment variables or a secrets manager)

### To register to SonnyLabs

1. Go to https://sonnylabs-service.onrender.com and register. 
2. Confirm your email address, and login to your new SonnyLabs account.

### To get a SonnyLabs API token:
1. Go to [API Keys](https://sonnylabs-service.onrender.com/analysis/api-keys).
2. Select + Generate New API Key.
3. Copy the generated API key.
4. Store this API token securely for use in your application.

### To get a SonnyLabs analysis ID:
1. Go to [Analysis](https://sonnylabs-service.onrender.com/analysis).
2. Create a new analysis and name it after the AI application/AI agent you will be protecting.
3. After you press Submit, you will be brought to the empty analysis page.
4. The analysis ID is the last part of the URL, like https://sonnylabs-service.onrender.com/analysis/{analysis_id}. Note that the analysis ID can also be found in the [SonnyLabs analysis dashboard](https://sonnylabs-service.onrender.com/analysis).
5. Store this analysis ID securely for use in your application.

> **Note:** We recommend storing your API token and analysis ID securely using environment variables or a secrets manager, not hardcoded in your application code.

## Easy 3-Step Integration

Getting started with SonnyLabs is simple. The most important function to know is `analyze_text()`, which is the core method for analyzing content for security risks.

### 1. Install and initialize the client

```python
# Install the SDK
pip install git+https://github.com/SonnyLabs/sonnylabs_py

# In your application
from sonnylabs_py import SonnyLabsClient

# Initialize the client with your securely stored credentials
client = SonnyLabsClient(
    api_key="YOUR_API_TOKEN",  # Replace with your actual token or use a secure method to retrieve it
    analysis_id="YOUR_ANALYSIS_ID",  # Replace with your actual ID or use a secure method to retrieve it
    base_url="https://sonnylabs-service.onrender.com"  # Optional, this is the default value
)
```

### 2. Analyze input/output with a single function call

```python
# Analyze user input
input_result = client.analyze_text("User message here", scan_type="input")

# Check for risks using helper methods
if client.has_risks(input_result) or client.is_toxic(input_result):
    # Handle risky input
    print("Security risk detected in input")

# Later, analyze AI response
output_result = client.analyze_text("AI response here", scan_type="output", tag=input_result["tag"])
```

### 3. Use specialized helper methods for specific checks

```python
# Check for specific types of risks
if client.has_pii(input_result):
    print("PII detected!")
    # Process PII information: input_result["analysis"][1]["result"]

if client.is_prompt_relevant(output_result):
    print("Response is relevant to the prompt")
else:
    print("Response might be off-topic")
```

For more advanced usage and complete examples, see the sections below.

## API Reference

This section documents all functions available in the SonnyLabsClient, their parameters, return values, and usage.

### Initialization

```python
SonnyLabsClient(api_token, base_url, analysis_id, timeout=5)
```

**Parameters:**
- `api_token` (str, **required**): Your SonnyLabs API token.
- `base_url` (str, **required**): Base URL for the SonnyLabs API (e.g., "https://sonnylabs-service.onrender.com").
- `analysis_id` (str, **required**): The analysis ID associated with your application.
- `timeout` (int, optional): Request timeout in seconds. Default is 5 seconds.

### Core Analysis Method

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
        {"type": "score", "name": "prompt_injection", "result": 0.8},
        {"type": "PII", "result": [{"label": "EMAIL", "text": "example@email.com"}, ...]}
        # Potentially other analysis types
    ]
}
```

### Helper Methods

#### `get_prompt_injections(analysis_result, threshold=0.65)`

**Description:** Extracts prompt injection details from analysis results.

**Parameters:**
- `analysis_result` (dict, **required**): The result dictionary from analyze_text.
- `threshold` (float, optional): The confidence threshold above which to consider a prompt injection detected. Default is 0.65.

**Returns:** Dictionary with prompt injection information or None if no issue:
```python
{
    "score": 0.8,  # Confidence score between 0 and 1
    "tag": "unique_tag",  # The tag from the analysis
    "detected": True,  # Whether the score exceeds the threshold
    "threshold": 0.65  # The threshold used
}
```

#### `is_prompt_injection(analysis_result, threshold=0.65)`

**Description:** Directly checks if prompt injection was detected above the threshold.

**Parameters:** Same as `get_prompt_injections()`.

**Returns:** Boolean indicating whether prompt injection was detected.

#### `get_pii(analysis_result)`

**Description:** Extracts PII (Personally Identifiable Information) details from analysis results.

**Parameters:**
- `analysis_result` (dict, **required**): The result dictionary from analyze_text.

**Returns:** List of PII items found or empty list if none:
```python
[
    {"label": "EMAIL", "text": "example@email.com", "tag": "unique_tag"},
    {"label": "PHONE", "text": "123-456-7890", "tag": "unique_tag"}
    # Additional PII items...
]
```

## Prompt to Integrate SonnyLabs to your AI application
Here is an example prompt to give to your IDE's LLM (Cursor, VSCode, Windsurf etc) to integrate the Sonnylabs REST API to your AI application.

```
As an expert AI developer, help me integrate SonnyLabs security features into my existing AI application.

I need to implement the following security measures:
1. Block prompt injections in both user inputs and AI outputs
2. Detect (but not block) PII in both user inputs and AI outputs
3. Link user prompts with AI responses in the SonnyLabs dashboard for monitoring

I've already installed the SonnyLabs Python SDK using pip and have my API token and analysis ID from the SonnyLabs dashboard.

Please provide a step-by-step implementation guide including:
- How to initialize the SonnyLabs client
- How to analyze user inputs before passing them to my LLM
- How to block requests if prompt injections are detected
- How to detect and log PII in user inputs (without blocking)
- How to analyze AI outputs before sending them to users
- How to block AI responses if they contain prompt injections
- How to detect and log PII in AI outputs (without blocking)
- How to properly use the 'tag' parameter to link prompts with their responses in the SonnyLabs dashboard
```

### Quick Start
```python
from sonnylabs_py import SonnyLabsClient
import os
from dotenv import load_dotenv

# Initialize the client with your securely stored credentials
client = SonnyLabsClient(
    api_token="YOUR_API_TOKEN",  # Replace with your actual token or use a secure method to retrieve it
    analysis_id="YOUR_ANALYSIS_ID",  # Replace with your actual ID or use a secure method to retrieve it
    base_url="https://sonnylabs-service.onrender.com"  
)

# Analyze text for security issues (input)
result = client.analyze_text("Hello, my name is John Doe", scan_type="input")
print(result)

# If you want to link an input with its corresponding output, change the scan_type from "input" to "output" but reuse the tag:
tag = result["tag"]
response = "I'm an AI assistant, nice to meet you John!"
output_result = client.analyze_text(response, scan_type="output", tag=tag)
```

## Integrating with a Chatbot
Here's how to integrate the SDK into a Python chatbot to detect prompt injections and PII:

### Set up the client
```python 
from sonnylabs_py import SonnyLabsClient
import os
from dotenv import load_dotenv

# Initialize the SonnyLabs client with your securely stored credentials
sonnylabs_client = SonnyLabsClient(
    api_token="YOUR_API_TOKEN",  # Replace with your actual token or use a secure method to retrieve it
    base_url="https://sonnylabs-service.onrender.com",  # SonnyLabs API endpoint
    analysis_id="YOUR_ANALYSIS_ID"  # Replace with your actual ID or use a secure method to retrieve it
)
```

### Implement message handling with security checks

```python 
def handle_user_message(user_message):
    # Step 1: Analyze the incoming message for security issues
    analysis_result = sonnylabs_client.analyze_text(user_message, scan_type="input")
    
    # Step 2: Check for prompt injections
    if sonnylabs_client.is_prompt_injection(analysis_result):
        return "I detected potential prompt injection in your message. Please try again."
    
    # Step 3: Check for PII
    pii_items = sonnylabs_client.get_pii(analysis_result)
    if pii_items:
        pii_types = [item["label"] for item in pii_items]
        return f"I detected personal information ({', '.join(pii_types)}) in your message. Please don't share sensitive data."
    
    # Step 4: If no security issues are found, process the message normally
    bot_response = generate_bot_response(user_message)
    
    # Step 5: Scan the outgoing message using the same tag to link it with the input
    tag = analysis_result["tag"]  # Reuse the tag from the input analysis
    output_analysis = sonnylabs_client.analyze_text(bot_response, scan_type="output", tag=tag)
    # Apply additional checks to bot_response if needed
    
    return bot_response

def generate_bot_response(user_message):
    # Your existing chatbot logic here
    # This could be a call to an LLM API or other response generation logic
    return "This is the chatbot's response"
```



### License
This project is licensed under the MIT License - see the LICENSE file for details.
