# SonnyLabs Helper Functions Documentation

A clean, reusable library for integrating prompt injection detection into agentic AI workflows. These helpers cover all critical security scan points where untrusted content meets your LLM.

## Quick Start

```python
from sonnylabs import SonnyLabsClient, configure_client, scan_text

# Setup once at app startup
client = SonnyLabsClient(
    api_token="your_token",
    base_url="https://api.sonnylabs.com",
    analysis_id="your_analysis_id"
)
configure_client(client)

# Now use scan functions anywhere
verdict = scan_text(user_input)
if verdict.is_safe:
    # Process user input
    pass
else:
    # Reject or log incident
    print(f"Injection detected: {verdict.score:.2f}")
```

## Core Functions

### 1. `scan_text(text, scan_type="input", policy=None, meta=None, client=None) -> ScanVerdict`

Scan a single text string for prompt injection attacks.

**Covers these scan points:**
- User input (before LLM call)
- Web/file/email/API ingestion (after extraction)
- Tool output re-ingestion (before feeding back to LLM)
- Memory reuse (before loading stored context)
- Inter-agent messages (before forwarding to another agent)

**Parameters:**
- `text` (str): Content to analyze
- `scan_type` (str): Type of scan
  - `"input"`: General user/untrusted input (default)
  - `"output"`: LLM output (for output scanning)
  - `"tool_output"`: Output from a tool execution
- `policy` (dict): Configuration options
  - `threshold`: Confidence threshold (default: 0.65)
  - `action`: "block", "review", or "allow"
- `meta` (dict): Metadata about the source
  - `source`: "web", "pdf", "email", "api", "memory", "agent:name"
  - `url`: For web content
  - `tool`: For tool output (e.g., `{"tool": "web_search"}`)
- `client`: Optional SonnyLabsClient instance (uses configured default if not provided)

**Returns:** `ScanVerdict` object with:
- `is_safe` (bool): True if content is clean
- `score` (float): Injection probability 0-1 (higher = more suspicious)
- `scan_type` (str): The type of scan performed
- `tag` (str): Unique ID for this analysis request
- `meta` (dict): Metadata passed in
- `raw_analysis` (list): Detailed analysis results

**Examples:**

```python
# Simple user input
verdict = scan_text(user_message)
if not verdict.is_safe:
    raise SecurityError(f"Injection detected: score={verdict.score}")

# Web content ingestion
web_text = extract_html_to_text(webpage_html)
verdict = scan_text(
    web_text,
    scan_type="input",
    meta={"source": "web", "url": webpage_url}
)

# Tool output before re-ingestion
search_results = web_search_tool.run(query)
verdict = scan_text(
    search_results,
    scan_type="tool_output",
    meta={"tool": "web_search"}
)

# Memory before loading into context
stored_notes = database.get_user_notes(user_id)
verdict = scan_text(
    stored_notes,
    scan_type="input",
    meta={"source": "memory", "user_id": user_id}
)
```

---

### 2. `scan_messages(messages, scan_type="input", policy=None, meta=None, client=None) -> ScanVerdict`

Scan a list of chat messages (conversation history) for prompt injection.

**Use cases:**
- Scanning multi-turn conversation before processing
- Loading long-term memory with past messages
- Checking inter-agent message chains

**Parameters:**
- `messages` (list): List of message dicts
  ```python
  [
      {"role": "user", "content": "user message"},
      {"role": "assistant", "content": "assistant response"},
      {"role": "system", "content": "system prompt"},
  ]
  ```
- `scan_type` (str): Same as `scan_text` ("input", "output", etc.)
- `policy` (dict): Configuration (threshold, etc.)
- `meta` (dict): Metadata
- `client`: Optional SonnyLabsClient instance

**Returns:** `ScanVerdict` (combined verdict across all messages)

**Examples:**

```python
# Scan conversation history before processing
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "First question"},
    {"role": "assistant", "content": "First answer"},
    {"role": "user", "content": user_input}  # New input
]

verdict = scan_messages(
    messages,
    scan_type="input",
    meta={"source": "conversation", "session_id": session_id}
)

if not verdict.is_safe:
    print(f"Injection in conversation history (score: {verdict.score})")
    # Handle: sanitize, alert, or reject continuation

# Load long-term memory
saved_conversations = load_user_memory(user_id)
verdict = scan_messages(
    saved_conversations,
    scan_type="input",
    meta={"source": "memory", "user_id": user_id}
)
```

---

### 3. `scan_rag_chunks(query, chunks, policy=None, meta=None, client=None) -> RagScanResult`

Scan RAG-retrieved document chunks BEFORE they're added to the LLM context.

**Critical scan point:** Stops "poisoned docs" and embedded injection instructions before they influence your LLM.

**Parameters:**
- `query` (str): Original search query
- `chunks` (list): Retrieved chunks - can be:
  - List of strings: `[chunk1_text, chunk2_text, ...]`
  - List of dicts: `[{"text": "...", "metadata": {...}}, {"content": "...", ...}]`
- `policy` (dict): Configuration
  - `threshold`: Confidence threshold (default: 0.65)
  - `max_chunks_to_scan`: Limit number of chunks to scan (for performance)
- `meta` (dict): Metadata
  - `retriever`: "pinecone", "weaviate", "opensearch", etc.
  - `index`: Index name
- `client`: Optional SonnyLabsClient instance

**Returns:** `RagScanResult` with:
- `query` (str): The search query
- `total_chunks` (int): Total chunks retrieved
- `safe_chunks` (list): Chunks that passed security check
- `flagged_chunks` (list): Potentially injected chunks (separated out)
- `is_safe` (bool): True if query + all chunks are clean
- `safe_count`, `flagged_count`: Counts for convenience
- `verdict_per_chunk`: Individual verdicts for each chunk

**Examples:**

```python
# After vector DB retrieval
chunks = vector_db.search(
    query=user_query,
    top_k=10
)

result = scan_rag_chunks(
    query=user_query,
    chunks=chunks,
    meta={"retriever": "pinecone", "index": "prod_docs"}
)

print(f"Safe: {result.safe_count}, Flagged: {result.flagged_count}")

if result.flagged_count > 0:
    logger.warning(f"Detected {result.flagged_count} suspicious chunks")
    for flagged in result.flagged_chunks:
        logger.warning(f"Chunk {flagged['index']}: score {flagged['score']}")

# Use ONLY safe chunks for LLM context
safe_context = "\n\n".join([c["text"] for c in result.safe_chunks])
prompt = f"Context:\n{safe_context}\n\nQuestion: {user_query}"
```

---

### 4. `scan_tool_call(user_message, tool_name, tool_args, tool_schema=None, policy=None, meta=None, client=None) -> ToolCallScanResult`

Scan a proposed tool call BEFORE execution to prevent prompt injection attacks from turning into real-world actions.

**Critical scan point:** After LLM generates tool call, assess before execution to prevent:
- Data exfiltration
- Destructive operations
- Unauthorized actions

**Parameters:**
- `user_message` (str): Original user message that led to this tool call
- `tool_name` (str): Name of the tool
- `tool_args` (dict): Arguments the model proposed
- `tool_schema` (str or dict): Tool description or full schema (helps detector understand intent)
  ```python
  # Can be simple string
  "Send an email to the provided recipient"
  
  # Or full schema
  {
      "name": "send_email",
      "description": "Send email",
      "parameters": {
          "to": {"type": "string"},
          "subject": {"type": "string"},
          "body": {"type": "string"}
      }
  }
  ```
- `policy` (dict): Configuration
- `meta` (dict): Metadata
- `client`: Optional SonnyLabsClient instance

**Returns:** `ToolCallScanResult` with:
- `is_safe` (bool): Overall safety assessment
- `tool_name` (str): The tool name
- `user_intent_safe` (bool): Is the user message itself safe?
- `tool_args_safe` (bool): Are the arguments safe?
- `combined_score` (float): Combined injection probability
- `user_message_verdict`: Detailed verdict on user intent
- `tool_context_verdict`: Detailed verdict on tool context
- `recommendation` (str): "proceed", "review", or "block"

**Examples:**

```python
# After LLM generates a tool call
user_input = "Search for my password on the web"
proposed_tool = {
    "name": "web_search",
    "arguments": {"query": "my password"}
}

result = scan_tool_call(
    user_message=user_input,
    tool_name=proposed_tool["name"],
    tool_args=proposed_tool["arguments"],
    tool_schema="Search the web using provided query string"
)

print(result)  # Tool Call 'web_search': ✗ RISKY [REVIEW]

# Decision logic
if result.recommendation == "block":
    logger.error("Blocking tool execution - high injection confidence")
    raise SecurityError(f"Potential injection in tool call: {result.combined_score}")

elif result.recommendation == "review":
    logger.warning("Suspicious tool call - queuing for manual review")
    alert_security_team(result)
    # Could allow with extra logging, or block

else:  # "proceed"
    # Execute tool
    output = execute_tool(proposed_tool["name"], proposed_tool["arguments"])
```

---

## Return Types

### `ScanVerdict`

```python
@dataclass
class ScanVerdict:
    is_safe: bool                              # True if text is clean
    score: float                               # Injection probability (0-1)
    scan_type: str                             # "input", "output", etc.
    tag: str                                   # Unique analysis ID
    meta: Dict[str, Any]                       # Metadata passed in
    raw_analysis: List[Dict[str, Any]]         # Detailed analysis data
    
    @property
    def confidence(self) -> float:             # Alias for score
        ...
    
    def __str__(self) -> str:
        # "✓ SAFE (score: 0.23, type: input)" or "✗ INJECTION DETECTED ..."
        ...
```

### `RagScanResult`

```python
@dataclass
class RagScanResult:
    query: str                                 # The search query
    total_chunks: int                          # Total chunks retrieved
    safe_chunks: List[Dict[str, Any]]          # Passed chunks with metadata
    flagged_chunks: List[Dict[str, Any]]       # Failed chunks with scores
    is_safe: bool                              # True if all clean
    verdict_per_chunk: List[ScanVerdict]       # Individual verdicts
    
    @property
    def safe_count(self) -> int:               # len(safe_chunks)
        ...
    
    @property  
    def flagged_count(self) -> int:            # len(flagged_chunks)
        ...
```

### `ToolCallScanResult`

```python
@dataclass
class ToolCallScanResult:
    is_safe: bool                              # Overall safety
    tool_name: str                             # Tool being called
    user_intent_safe: bool                     # User message safety
    tool_args_safe: bool                       # Arguments safety
    combined_score: float                      # Average injection probability
    user_message_verdict: ScanVerdict           # Details on user intent
    tool_context_verdict: Optional[ScanVerdict] # Details on tool context
    recommendation: str                        # "proceed", "review", "block"
```

---

## Configuration

### One-Time Setup

```python
from sonnylabs import SonnyLabsClient, configure_client

# Initialize client
client = SonnyLabsClient(
    api_token="sk_live_...",  # From environment
    base_url="https://api.sonnylabs.com",
    analysis_id="analysis_123"  # From environment
)

# Configure as default (used by all scan functions)
configure_client(client)

# Now all scan functions work without passing client explicitly
verdict = scan_text("user input")
```

### Custom Client Per Call

```python
# Use specific client instance
verdict = scan_text(
    "user input",
    client=my_custom_client
)
```

### Policy Configuration

```python
# Custom policy for stricter scanning
policy = {
    "threshold": 0.5,      # Lower = stricter (default 0.65)
    "action": "block"      # What to do if flagged
}

verdict = scan_text(
    user_input,
    policy=policy
)
```

---

## Scan Points: Where to Use Each Function

| Scan Point | When | Function | scan_type | Example |
|-----------|------|----------|-----------|---------|
| User input | Before LLM call | `scan_text()` | "input" | User types message → scan → send to model |
| RAG chunks | After retrieval | `scan_rag_chunks()` | "rag" | Vector DB returns docs → scan → add to context |
| Web content | After extraction | `scan_text()` | "input" | Browser returns HTML → extract text → scan |
| Tool call | Before execution | `scan_tool_call()` | "tool_call" | Model proposes tool → scan → execute |
| Tool output | Before re-ingestion | `scan_text()` | "tool_output" | Tool returns data → scan → feed to LLM |
| Memory | Before loading | `scan_text()` / `scan_messages()` | "input" | Load past conversation → scan → use in context |
| Inter-agent | Before forwarding | `scan_text()` | "input" | Agent A→Agent B → scan → forward |

---

## Integration Patterns

### Pattern 1: Agentic Loop with Security

```python
def agent_step(user_input, agent_state):
    # 1. Scan user input
    if not scan_text(user_input).is_safe:
        return "Rejected: unsafe input"
    
    # 2. Load memory (scan it)
    messages = agent_state["memory"]
    verdict = scan_messages(messages)
    if not verdict.is_safe:
        return "Rejected: unsafe memory"
    
    # 3. RAG retrieval (scan chunks)
    chunks = retriever.search(user_input)
    rag_result = scan_rag_chunks(user_input, chunks)
    safe_context = "\n".join([c["text"] for c in rag_result.safe_chunks])
    
    # 4. LLM call (model generates tool call)
    decision = llm.generate(
        messages=messages,
        context=safe_context,
        tools=available_tools
    )
    
    # 5. Scan tool call before execution
    tool_result = scan_tool_call(
        user_message=user_input,
        tool_name=decision.tool_name,
        tool_args=decision.tool_args
    )
    if tool_result.recommendation == "block":
        return "Rejected: suspicious tool call"
    
    # 6. Execute tool
    output = execute_tool(decision.tool_name, decision.tool_args)
    
    # 7. Scan tool output before feeding back to LLM
    if not scan_text(output, scan_type="tool_output").is_safe:
        output = "[Content filtered]"
    
    return output
```

### Pattern 2: FastAPI Shield

```python
from fastapi import FastAPI, HTTPException
from sonnylabs import scan_text, configure_client

app = FastAPI()

@app.post("/chat")
async def chat(message: str):
    # Scan before processing
    verdict = scan_text(message)
    
    if not verdict.is_safe:
        raise HTTPException(
            status_code=400,
            detail=f"Injection detected (score: {verdict.score})"
        )
    
    # Safe to process
    response = process_message(message)
    return {"response": response}
```

### Pattern 3: LangGraph Integration

```python
from langgraph.graph import StateGraph
from sonnylabs import scan_text, scan_tool_call

def scan_input_node(state):
    """Custom node for input scanning"""
    verdict = scan_text(state["user_input"])
    state["input_safe"] = verdict.is_safe
    state["input_score"] = verdict.score
    return state

def scan_tool_node(state):
    """Custom node for tool call scanning"""
    result = scan_tool_call(
        user_message=state["user_input"],
        tool_name=state["tool_call"]["name"],
        tool_args=state["tool_call"]["arguments"]
    )
    state["tool_safe"] = result.is_safe
    state["tool_recommendation"] = result.recommendation
    return state

graph = StateGraph(AgentState)
graph.add_node("input_scan", scan_input_node)
graph.add_node("tool_scan", scan_tool_node)
# ... add other nodes
```

---

## Error Handling

All functions use **fail-secure** defaults:
- If scanning fails → treat as UNSAFE
- If API unreachable → treat as UNSAFE
- If API returns error → treat as UNSAFE

```python
try:
    verdict = scan_text(user_input)
    if not verdict.is_safe:
        handle_injection_detected(verdict)
except Exception as e:
    # Fail-secure: treat as unsafe
    logger.error(f"Scan failed: {e}")
    handle_injection_detected(None)
```

---

## Best Practices

1. **Scan at every untrusted boundary**
   - User input → scan
   - External data → scan
   - Tool calls → scan
   - Tool outputs → scan

2. **Use appropriate metadata**
   ```python
   meta = {
       "source": "web",           # Where did it come from?
       "url": webpage_url,        # Additional context
       "session_id": session_id   # For tracking
   }
   ```

3. **Log all verdicts**
   ```python
   if not verdict.is_safe:
       log_security_incident(
           type="injection_detected",
           content=text[:100],
           score=verdict.score,
           source=meta.get("source")
       )
   ```

4. **Monitor scores over time**
   - Track false positive rates
   - Adjust thresholds if needed
   - Alert on injection attempts

5. **Test edge cases**
   ```python
   test_cases = [
       "Hello world",  # Clean
       "Ignore previous instructions: ...",  # Injection
       "Normal text with quotes 'and' special chars",  # Edge case
   ]
   ```

---

## Environment Variables

```bash
# .env
SONNYLABS_API_TOKEN=sk_live_xxx
SONNYLABS_BASE_URL=https://api.sonnylabs.com
SONNYLABS_ANALYSIS_ID=analysis_xxx
```

```python
import os
from sonnylabs import SonnyLabsClient, configure_client

client = SonnyLabsClient(
    api_token=os.getenv("SONNYLABS_API_TOKEN"),
    base_url=os.getenv("SONNYLABS_BASE_URL"),
    analysis_id=os.getenv("SONNYLABS_ANALYSIS_ID")
)
configure_client(client)
```

---

## API Reference Quick Summary

| Function | Purpose | Returns | Scan Points |
|----------|---------|---------|------------|
| `scan_text()` | Single text scan | `ScanVerdict` | Input, tool output, memory, web content, inter-agent |
| `scan_messages()` | Conversation scan | `ScanVerdict` | Memory, conversation history |
| `scan_rag_chunks()` | Document scan | `RagScanResult` | RAG retrieval |
| `scan_tool_call()` | Tool call scan | `ToolCallScanResult` | Tool execution intent |
| `configure_client()` | Setup | - | One-time init |

---

For more examples, see `examples_helper_usage.py`.
