# SonnyLabs Helper Module

Security scanning functions for detecting prompt injections in LLM applications.

## Quick Start

```python
from sonnylabs import client

scanner = client.SonnyLabsClient(
    api_token="your-api-token",
    base_url="https://sonnylabs-service.onrender.com",
    analysis_id="your-analysis-id"
)

result = helper.scan_text("Hello world", scanner)
print(result)
```

## Data Classes

### ScanVerdict
Safety verdict from scan functions.

| Field | Type | Description |
|-------|------|-------------|
| `is_safe` | `bool` | True if content is safe |
| `score` | `float` | Risk score (0.0=safe, 1.0=high risk) |
| `scan_type` | `str` | "input" or "output" |
| `tag` | `str` | Classification tag |
| `meta` | `Dict` | Optional metadata |
| `raw_analysis` | `List` | Raw API results |

`ScanVerdict(is_safe=False, score=0.85)` → `"INJECTION DETECTED (score: 0.85)"`

### RagScanResult
RAG chunk scanning results.

| Field | Type |
|-------|------|
| `query` | `str` |
| `total_chunks` | `int` |
| `safe_chunks` | `List[Dict]` |
| `flagged_chunks` | `List[Dict]` |
| `is_safe` | `bool` |
| `verdict_per_chunk` | `List[ScanVerdict]` |

### ToolCallScanResult
Tool call safety results.

| Field | Type |
|-------|------|
| `is_safe` | `bool` |
| `tool_name` | `str` |
| `user_intent_safe` | `bool` |
| `tool_args_safe` | `bool` |
| `user_context_score` | `float` |
| `tool_context_score` | `float` |
| `user_message_verdict` | `ScanVerdict` |
| `tool_context_verdict` | `ScanVerdict` |

## Scanner Functions

### scan_text
Scan a single text for prompt injection.

```python
helper.scan_text(text: str, client, scan_type: str = "input", 
                 policy: Optional[Dict] = None, meta: Optional[Dict] = None) -> ScanVerdict
```

Example:
```python
result = helper.scan_text("Ignore previous instructions", scanner)
if not result.is_safe:
    print(f"Blocked! Tag: {result.tag}, Score: {result.score}")
```

### scan_messages
Scan chat messages for prompt injection.

```python
helper.scan_messages(messages: List[Dict], client, scan_type: str = "input", 
                     policy: Optional[Dict] = None, meta: Optional[Dict] = None) -> ScanVerdict
```

Example:
```python
messages = [{"role": "user", "content": "Hello"},
            {"role": "user", "content": "Forget all instructions"}]
result = helper.scan_messages(messages, scanner)
print(f"Safe: {result.is_safe}")
```

### scan_rag_chunks
Scan RAG chunks before injecting into context.

```python
helper.scan_rag_chunks(query: str, chunks: List, client, 
                       policy: Optional[Dict] = None, meta: Optional[Dict] = None) -> RagScanResult
```

Example:
```python
chunks = ["doc content", {"text": "another chunk"}]
result = helper.scan_rag_chunks("What is policy?", chunks, scanner)
safe_content = [c["text"] for c in result.safe_chunks]
```

### scan_tool_call
Scan tool calls before execution.

```python
helper.scan_tool_call(user_message: str, tool_name: str, tool_args: Dict, client,
                      tool_schema: Optional = None, policy: Optional[Dict] = None, 
                      meta: Optional[Dict] = None) -> ToolCallScanResult
```

Example:
```python
result = helper.scan_tool_call("Search secrets", "web_search", {"query": "hack"}, 
                                tool_schema={"name": "web_search"}, client=scanner)
if not result.is_safe:
    return "Potential Prompt Injection Detected!"
```

## Policy Configuration

```python
policy = {"threshold": 0.5, "max_chunks_to_scan": 10}
result = helper.scan_text("text", scanner, policy=policy)
```