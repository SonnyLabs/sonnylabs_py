#!/usr/bin/env python3
"""
Script to check MCP tool instructions for prompt injection vulnerabilities.
Uses SonnyLabs API to analyze docstrings and instructions in MCP tools.
"""

import os
import sys
import json
import re
from dotenv import load_dotenv
import requests

def load_sonnylabs_credentials():
    """Load SonnyLabs API credentials from environment variables."""
    load_dotenv()  # Load environment variables from .env file
    api_key = os.getenv("SONNYLABS_API_KEY")
    analysis_id = os.getenv("SONNYLABS_ANALYSIS_ID")
    
    if not api_key or not analysis_id:
        print("Error: SonnyLabs credentials not found in .env file")
        print("Please ensure SONNYLABS_API_KEY and SONNYLABS_ANALYSIS_ID are set")
        sys.exit(1)
    
    return api_key, analysis_id

def extract_mcp_tool_instructions(module_path):
    """Extract docstrings and instructions from MCP tools in the given module using regex."""
    print(f"Loading MCP tools from {module_path}")
    
    try:
        with open(module_path, 'r') as file:
            content = file.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    # Find functions decorated with @mcp.tool()
    # Pattern looks for @mcp.tool() followed by def function_name, then captures docstrings
    tool_pattern = r'@mcp\.tool\(\)\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\([^)]*\).*?"""(.*?)"""'
    
    # Find all matches with re.DOTALL to match across multiple lines
    matches = re.finditer(tool_pattern, content, re.DOTALL)
    
    tool_instructions = []
    for match in matches:
        function_name = match.group(1)
        docstring = match.group(2).strip()
        
        tool_info = {
            "name": function_name,
            "docstring": docstring,
        }
        
        tool_instructions.append(tool_info)
        print(f"Found tool: {function_name}")
    
    return tool_instructions

def check_prompt_injection(text, api_key, analysis_id):
    """
    Check text for potential prompt injections using SonnyLabs API.
    
    This is a simplified version that directly uses requests instead of the SonnyLabs client
    since we haven't installed the package.
    """
    print(f"Checking for prompt injections in: {text[:50]}...")
    
    # SonnyLabs API endpoint
    url = "https://sonnylabs-service.onrender.com/api/v1/text/analyze"
    
    # Prepare headers and payload
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "analysis_id": analysis_id,
        "scan_type": "input",  # We're checking inputs for potential prompt injections
        "text": text
    }
    
    # Make the API request
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Raise exception for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling SonnyLabs API: {e}")
        return {"error": str(e)}

def main():
    """Main function to run the script."""
    api_key, analysis_id = load_sonnylabs_credentials()
    
    # Path to the MCP module
    mcp_module_path = "main.py"
    
    # Extract tool instructions
    tool_instructions = extract_mcp_tool_instructions(mcp_module_path)
    print(f"Found {len(tool_instructions)} MCP tools")
    
    # Check each tool's docstring for potential prompt injections
    results = []
    for tool in tool_instructions:
        print(f"\nAnalyzing tool: {tool['name']}")
        
        # Check the docstring
        result = check_prompt_injection(tool['docstring'], api_key, analysis_id)
        
        result_info = {
            "tool_name": tool['name'],
            "instruction": tool['docstring'],
            "analysis_result": result
        }
        results.append(result_info)
    
    # Save the results to a file
    with open("prompt_injection_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nAnalysis complete! Results saved to prompt_injection_results.json")

if __name__ == "__main__":
    print("Starting prompt injection analysis for MCP tools...")
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
