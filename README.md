# SonnyLabs Python Client

Detect prompt injections and PII in real-time in your AI applications using the SonnyLabs REST API.

## Table of Contents

- [About](#about)  
- [Security Risks in AI Applications](#security-risks-in-ai-applications)
- [Installation](#installation)
- [Pre-requisites](#pre-requisites)
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
- A `.env` file, or secrets manager, to store your API token and analysis ID

### To register to SonnyLabs

1. Go to https://sonnylabs-service.onrender.com and register. 
2. Confirm your email address, and login to your new SonnyLabs account.

### To get a SonnyLabs API token:
1. Go to [API Keys](https://sonnylabs-service.onrender.com/analysis/api-keys).
2. Select + Generate New API Key.
3. Copy the generated API key.
4. Paste the API key into your .env file (or secrets manager), and name it SONNYLABS_API_TOKEN.

### To get a SonnyLabs analysis ID:
1. Go to [Analysis](https://sonnylabs-service.onrender.com/analysis).
2. Create a new analysis and name it after the AI application/AI agent you will be protecting.
3. After you press Submit, you will be brought to the empty analysis page.
4. The analysis ID is the last part of the URL, like https://sonnylabs-service.onrender.com/analysis/{analysis_id}. Note that the analysis ID can also be found in the [SonnyLabs analysis dashboard](https://sonnylabs-service.onrender.com/analysis).
5. Copy the analysis ID and paste it into your AI application's .env file (or secrets manager), and name it SONNYLABS_ANALYSIS_ID.

### Setting up your .env file
Create a `.env` file in your project root directory with the following content:
```
SONNYLABS_API_TOKEN=your_api_token_here
SONNYLABS_ANALYSIS_ID=your_analysis_id_here
```

To load these environment variables in your Python application, you can use the `python-dotenv` package:
```bash
pip install python-dotenv
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

# Load environment variables from .env file
load_dotenv()

# Initialize the client
client = SonnyLabsClient(
    api_token=os.environ.get("SONNYLABS_API_TOKEN"),
    base_url="https://sonnylabs-service.onrender.com",
    analysis_id=os.environ.get("SONNYLABS_ANALYSIS_ID")
)

# Analyze text for security issues (input)
result = client.analyze_text("Hello, my name is John Doe", scan_type="input")
print(result)

# If you want to link an input with its corresponding output, reuse the tag:
tag = result["tag"]
response = "I'm an AI assistant, nice to meet you John!"
output_result = client.analyze_text(response, scan_type="output", tag=tag)
```

Integrating with a Chatbot
Here's how to integrate the SDK into a Python chatbot to detect prompt injections and PII:

### Set up the client
```python 
from sonnylabs_py import SonnyLabsClient
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the SonnyLabs client
sonnylabs_client = SonnyLabsClient(
    api_token=os.environ.get("SONNYLABS_API_TOKEN"),  # Your API token from .env
    base_url="https://sonnylabs-service.onrender.com",              # SonnyLabs API endpoint
    analysis_id=os.environ.get("SONNYLABS_ANALYSIS_ID") # Your analysis ID from .env
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

### Integrate with a web framework (e.g., Flask)

```python 
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    response = handle_user_message(user_message)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
```

### API Reference
SonnyLabsClient

```python
SonnyLabsClient(api_token, base_url, analysis_id, timeout=5)
```

Parameters:

api_token (str): Your SonnyLabs API token
base_url (str): Base URL for the SonnyLabs API
analysis_id (str): The analysis ID associated with your application
timeout (int, optional): Request timeout in seconds (default: 5)

### Methods
#### analyze_text

```python
analyze_text(text, scan_type="input", tag=None)
```

Parameters:

    text (str): Text to analyze
    scan_type (str, optional): "input" or "output" (default: "input")
    tag (str, optional): Custom tag for linking prompts with their responses (default: None)

Returns:

    dict: Analysis results, including the tag used

### Linking Prompts and Responses

To properly link prompts with their corresponding responses in the SonnyLabs dashboard, use the same tag for both analyses, but ensure to update the scan_type to be either input (by the user) or output (by the LLM):

```python
# Analyze the user input (prompt)
input_result = sonnylabs_client.analyze_text(user_message, scan_type="input")

# Extract the tag from the input analysis
tag = input_result["tag"]

# Generate your response
bot_response = generate_bot_response(user_message)

# Analyze the output using the same tag
output_result = sonnylabs_client.analyze_text(bot_response, scan_type="output", tag=tag)
```

This ensures that prompts and their responses are linked in the SonnyLabs dashboard and analytics.

#### get_prompt_injections

```python
get_prompt_injections(analysis_result)
```

Parameters:

    analysis_result (dict): Analysis results from analyze_text

Returns:

    dict: Prompt injection information including detection status, or None if no issue

#### is_prompt_injection

```python
is_prompt_injection(analysis_result)
```

Parameters:

    analysis_result (dict): Analysis results from analyze_text

Returns:

    bool: True if prompt injection was detected, False otherwise

#### get_pii

```python
get_pii(analysis_result)
```

Parameters:

    analysis_result (dict): Analysis results from analyze_text

Returns:

    list: List of PII items found or empty list if none

### License
This project is licensed under the MIT License - see the LICENSE file for details.