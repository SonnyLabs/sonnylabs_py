# SonnyLabs Python Client

A simple Python client for the SonnyLabs Security API.

## Installation

```bash
pip install sonnylabs-py
```

## Example

Authentication
You'll need:

An API token from SonnyLabs
Your analysis ID (available in the SonnyLabs dashboard)

### Quick Start
```python
from sonnylabs_py import SonnyLabsClient

# Initialize the client
client = SonnyLabsClient(
    api_token="your_api_token",
    base_url="https://api.sonnylabs.ai",
    analysis_id="your_analysis_id"
)

# Analyze text for security issues
result = client.analyze_text("Hello, my name is John Doe", scan_type="input")
print(result)
```

Integrating with a Chatbot
Here's how to integrate the SDK into a Python chatbot to detect prompt injections and PII:

### Set up the client
```python 
from sonnylabs_py import SonnyLabsClient
import os

# Initialize the SonnyLabs client
sonnylabs_client = SonnyLabsClient(
    api_token=os.environ.get("SONNYLABS_API_TOKEN"),  # Your API token
    base_url="https://api.sonnylabs.ai",              # SonnyLabs API endpoint
    analysis_id="your_analysis_id"                    # From SonnyLabs dashboard
)
```

### Implement message handling with security checks

```python 
def handle_user_message(user_message):
    # Step 1: Analyze the incoming message for security issues
    analysis_result = sonnylabs_client.analyze_text(user_message, scan_type="input")
    
    # Step 2: Check for prompt injections
    prompt_injection = sonnylabs_client.get_prompt_injections(analysis_result)
    if prompt_injection and prompt_injection["score"] > 0.65:  # Threshold can be adjusted, recommended of over 0.65
        return "I detected potential prompt injection in your message. Please try again."
    
    # Step 3: Check for PII
    pii_items = sonnylabs_client.get_pii(analysis_result)
    if pii_items:
        pii_types = [item["label"] for item in pii_items]
        return f"I detected personal information ({', '.join(pii_types)}) in your message. Please don't share sensitive data."
    
    # Step 4: If no security issues are found, process the message normally
    bot_response = generate_bot_response(user_message)
    
    # Step 5: Optionally scan the outgoing message too
    output_analysis = sonnylabs_client.analyze_text(bot_response, scan_type="output")
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
analyze_text(text, scan_type="input")
```

Parameters:

    text (str): Text to analyze
    scan_type (str, optional): "input" or "output" (default: "input")

Returns:

    dict: Analysis results

#### get_prompt_injections

```python
get_prompt_injections(analysis_result)
```

Parameters:

    analysis_result (dict): Analysis results from analyze_text

Returns:

    dict: Prompt injection score and tag or None if no issue

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