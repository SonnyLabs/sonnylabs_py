"""
Examples of using the SonnyLabs Helper Functions

This demonstrates how to integrate the scanning helpers into your agentic AI workflows
at all the critical untrusted→trusted boundaries.
"""

from sonnylabs import (
    SonnyLabsClient,
    configure_client,
    scan_text,
    scan_messages,
    scan_rag_chunks,
    scan_tool_call,
)

# ============================================================================
# Setup - Configure the client once at app startup
# ============================================================================

def setup_sonnylabs():
    """Initialize the SonnyLabs security client"""
    client = SonnyLabsClient(
        api_token="your_api_token",  # Load from env in production
        base_url="https://api.sonnylabs.com/v1",
        analysis_id="your_analysis_id"  # Load from env in production
    )
    configure_client(client)


# ============================================================================
# Scan Point 1: User Input Scan
# ============================================================================

def handle_user_message(user_input: str) -> bool:
    """
    SCAN POINT 1: Immediately when user message enters the agent (before LLM call)
    Why: Blocks direct goal hijacks / jailbreaks
    """
    # Scan the raw user input
    verdict = scan_text(user_input, scan_type="input")
    
    print(f"User Input Scan: {verdict}")
    print(f"  Safety: {verdict.is_safe}")
    print(f"  Confidence: {verdict.confidence:.2f}")
    
    if not verdict.is_safe:
        print("  ⚠️  Potential prompt injection detected!")
        # Log the incident
        log_security_incident("user_input_injection", user_input, verdict)
        # Reject or sanitize
        return False
    
    return True


# ============================================================================
# Scan Point 2: RAG Retrieved Chunk Scan
# ============================================================================

def process_rag_retrieval(user_query: str, vector_db) -> str:
    """
    SCAN POINT 2: Right after retrieval (vector DB), before chunks added to prompt
    Why: Stops "poisoned docs" / embedded instructions
    """
    # Retrieve chunks from vector DB (pseudo-code)
    chunks = vector_db.search(user_query, top_k=10)
    
    # Scan all chunks at once
    rag_result = scan_rag_chunks(
        query=user_query,
        chunks=chunks,
        meta={"retriever": "pinecone", "index": "documents_v1"}
    )
    
    print(f"RAG Scan: {rag_result}")
    print(f"  Safe chunks: {rag_result.safe_count}/{rag_result.total_chunks}")
    print(f"  Flagged chunks: {rag_result.flagged_count}")
    
    if rag_result.flagged_count > 0:
        print(f"  ⚠️  {rag_result.flagged_count} suspicious chunks detected!")
        for flagged in rag_result.flagged_chunks:
            print(f"    - Chunk {flagged['index']}: score {flagged['score']:.2f}")
            log_security_incident("rag_poisoned_doc", flagged["text"], 
                                 verdict=None, verdict_score=flagged["score"])
    
    # Build context from ONLY safe chunks
    safe_context = "\n\n".join([c["text"] for c in rag_result.safe_chunks])
    return safe_context


# ============================================================================
# Scan Point 3: Web/File/Email/API Ingestion Scan
# ============================================================================

def ingest_external_content(content: str, source: str, source_url: str = None) -> str:
    """
    SCAN POINT 3: After extracting text from external content, before LLM context
    Why: Browsing and ingestion are hostile by default
    """
    # Could be: HTML→text (web), PDF→text, email body, API response, etc.
    
    meta = {
        "source": source,  # "web", "pdf", "email", "api", etc.
        "url": source_url or "unknown"
    }
    
    verdict = scan_text(
        content,
        scan_type="input",
        meta=meta
    )
    
    print(f"External Content Scan ({source}): {verdict}")
    
    if not verdict.is_safe:
        print(f"  ⚠️  Suspicious {source} content detected (score: {verdict.score:.2f})")
        log_security_incident("external_content_injection", content[:200], verdict)
        # Sanitize or reject
        return sanitize_content(content)
    
    return content


# ============================================================================
# Scan Point 4: Tool Call Intent Scan (Pre-Execution)
# ============================================================================

def execute_tool_safely(
    user_message: str,
    tool_name: str,
    tool_args: dict
) -> bool:
    """
    SCAN POINT 4: After LLM proposes tool call, BEFORE executing it
    Why: Prevents prompt injection turning into real-world actions
          (exfiltration, destructive operations)
    """
    
    # Define tool schemas for context
    tool_schemas = {
        "web_search": "Search the web and return results. Args: query (string)",
        "delete_file": "Delete a file. Args: file_path (string)",
        "send_email": "Send an email. Args: to (email), subject, body",
        "database_query": "Execute database query. Args: query (SQL string)",
    }
    
    tool_schema = tool_schemas.get(tool_name, "")
    
    # Scan the proposed tool call
    result = scan_tool_call(
        user_message=user_message,
        tool_name=tool_name,
        tool_args=tool_args,
        tool_schema=tool_schema,
        meta={"component": "tool_execution"}
    )
    
    print(f"Tool Call Scan: {result}")
    print(f"  User intent safe: {result.user_intent_safe}")
    print(f"  Tool args safe: {result.tool_args_safe}")
    print(f"  Combined score: {result.combined_score:.2f}")
    print(f"  Recommendation: {result.recommendation.upper()}")
    
    # Decision tree based on recommendation
    if result.recommendation == "block":
        print(f"  ✗ BLOCKING tool execution - high injection confidence")
        log_security_incident("tool_injection_blocked", 
                            f"Tool: {tool_name}, Args: {tool_args}",
                            result.user_message_verdict)
        return False
    
    elif result.recommendation == "review":
        print(f"  ⚠️  REVIEW REQUIRED - suspicious but not definitive")
        # Queue for human review or use increased logging
        alert_security_team(tool_name, tool_args, result)
        # Decide: allow with logging, or block
        return True  # Example: allow with monitoring
    
    else:  # "proceed"
        print(f"  ✓ Proceeding with tool execution")
        return True


# ============================================================================
# Scan Point 5: Tool Output Re-ingestion Scan
# ============================================================================

def process_tool_output(tool_name: str, tool_output: str) -> str:
    """
    SCAN POINT 5: After tool runs, BEFORE appending to next LLM prompt
    Why: Tool outputs can contain injected instructions
         (e.g., web search results, CRM notes, tickets, database rows)
    """
    
    verdict = scan_text(
        tool_output,
        scan_type="tool_output",
        meta={"tool": tool_name}
    )
    
    print(f"Tool Output Scan ({tool_name}): {verdict}")
    
    if not verdict.is_safe:
        print(f"  ⚠️  Potential injection in tool output (score: {verdict.score:.2f})")
        log_security_incident("tool_output_injection", tool_output[:200], verdict)
        # Sanitize or use summary instead
        return create_safe_summary(tool_output)
    
    return tool_output


# ============================================================================
# Scan Point 6: Memory Reuse Scan
# ============================================================================

def load_user_memory(user_id: str) -> list:
    """
    SCAN POINT 6: Before loading stored memory into current context
    Why: Prevents persistent poisoning that carries across sessions
    """
    
    # Load past conversation / notes from database
    stored_memory = get_user_memory_from_db(user_id)
    
    # Convert to message format
    messages = [
        {"role": "user", "content": msg} for msg in stored_memory
    ]
    
    # Scan entire memory blob
    verdict = scan_messages(
        messages,
        scan_type="input",
        meta={"source": "memory", "user_id": user_id}
    )
    
    print(f"Memory Scan (user {user_id}): {verdict}")
    
    if not verdict.is_safe:
        print(f"  ⚠️  Potential injection detected in stored memory")
        # Either: purge, alert, or use only recent safe parts
        log_security_incident("memory_poisoning", f"User: {user_id}", verdict)
        # Example: use only recent messages
        return filter_safe_memory(messages)
    
    return messages


# ============================================================================
# Scan Point 7: Inter-Agent Message Scan
# ============================================================================

def forward_to_agent(source_agent: str, target_agent: str, message: str) -> bool:
    """
    SCAN POINT 7: Before one agent's message becomes input to another
    Why: Agent-to-agent is another untrusted boundary
         (especially if any agent touches external content)
    """
    
    verdict = scan_text(
        message,
        scan_type="input",
        meta={"source": f"agent:{source_agent}", "target": f"agent:{target_agent}"}
    )
    
    print(f"Inter-Agent Message Scan ({source_agent} → {target_agent}): {verdict}")
    
    if not verdict.is_safe:
        print(f"  ⚠️  Suspicious message detected")
        log_security_incident("inter_agent_injection",
                            f"{source_agent} -> {target_agent}: {message[:100]}",
                            verdict)
        return False
    
    return True


# ============================================================================
# Helper Functions (Simple Implementations)
# ============================================================================

def log_security_incident(incident_type: str, content: str, verdict=None, verdict_score=None):
    """Log security incidents to monitoring system"""
    score = verdict.score if verdict else verdict_score
    print(f"  [LOG] Incident: {incident_type}, Score: {score:.2f}")


def alert_security_team(tool_name: str, tool_args: dict, result):
    """Alert security team for manual review"""
    print(f"  [ALERT] Security team notification sent for {tool_name}")


def sanitize_content(content: str) -> str:
    """Basic content sanitization"""
    return content[:200] + "..."


def create_safe_summary(content: str) -> str:
    """Create safe summary from suspicious content"""
    return f"[Content filtered - potential injection detected. Original length: {len(content)} chars]"


def filter_safe_memory(messages: list) -> list:
    """Keep only recent safe messages"""
    # Example: keep only last 5 messages
    return messages[-5:]


def get_user_memory_from_db(user_id: str) -> list:
    """Fetch user memory (pseudo-code)"""
    return [f"Memory entry {i}" for i in range(3)]


# ============================================================================
# Complete Agentic Loop Example
# ============================================================================

def agentic_loop(user_input: str, agent_context: dict):
    """
    Complete example of an agent loop with security scanning at all points
    """
    print("\n" + "="*60)
    print("AGENTIC LOOP WITH SECURITY SCANNING")
    print("="*60)
    
    # SCAN POINT 1: User input
    print("\n[1/5] Scanning user input...")
    if not handle_user_message(user_input):
        return "Rejected: Potential prompt injection in user input"
    
    # SCAN POINT 6: Load memory
    print("\n[2/5] Loading and scanning user memory...")
    memory = load_user_memory(agent_context.get("user_id"))
    
    # Build context: system + memory + user query
    full_messages = [
        {"role": "system", "content": agent_context.get("system_prompt", "")},
    ] + memory + [
        {"role": "user", "content": user_input}
    ]
    
    # Simulate LLM call would happen here...
    # For demo: assume LLM decides to use web_search tool
    
    # SCAN POINT 4: Tool call intent
    print("\n[3/5] Scanning proposed tool call...")
    tool_decision = {
        "tool": "web_search",
        "args": {"query": "latest news about " + user_input[:30]}
    }
    
    if not execute_tool_safely(user_input, tool_decision["tool"], tool_decision["args"]):
        return "Rejected: Potential injection in tool call"
    
    # Simulate tool execution...
    tool_output = "Mock search results with potentially injected content..."
    
    # SCAN POINT 5: Tool output re-ingestion
    print("\n[4/5] Scanning tool output before re-ingestion...")
    safe_tool_output = process_tool_output(tool_decision["tool"], tool_output)
    
    # SCAN POINT 2: RAG retrieval (if using knowledge base)
    print("\n[5/5] Scanning RAG-retrieved chunks...")
    # rag_context = process_rag_retrieval(user_input, vector_db)
    
    return "All security checks passed. Ready for LLM processing."


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    # Setup
    setup_sonnylabs()
    
    # Run examples
    print("\n" + "█"*60)
    print(" SonnyLabs Helper Functions - Security Scanning Examples")
    print("█"*60)
    
    # Example 1: User input scan
    print("\n[EXAMPLE 1] User Input Scanning")
    print("-" * 60)
    handle_user_message("What is the weather?")
    
    # Example 2: Tool call scanning
    print("\n[EXAMPLE 2] Tool Call Scanning")
    print("-" * 60)
    execute_tool_safely(
        "Search the web",
        "web_search",
        {"query": "information"}
    )
    
    # Example 3: Complete agentic loop
    result = agentic_loop(
        user_input="Tell me about recent AI developments",
        agent_context={"user_id": "user_123", "system_prompt": "You are a helpful assistant"}
    )
    print(f"\nFinal Result: {result}")
