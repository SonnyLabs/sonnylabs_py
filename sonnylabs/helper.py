from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
import logging

logger = logging.getLogger("sonnylabs.helper")


# ============================================================================
# Data Classes - Return types for scanner functions
# ============================================================================

@dataclass
class ScanVerdict:
    """Safety verdict for scanned text"""
    is_safe: bool
    score: float
    scan_type: str
    tag: str
    meta: Dict[str, Any] = field(default_factory=dict)
    raw_analysis: List[Dict[str, Any]] = field(default_factory=list)
    
    def __str__(self) -> str:
        status = "SAFE" if self.is_safe else "INJECTION DETECTED"
        return f"{status} (score: {self.score:.2f})"


@dataclass
class RagScanResult:
    """Result from scanning RAG chunks"""
    query: str
    total_chunks: int
    safe_chunks: List[Dict[str, Any]]
    flagged_chunks: List[Dict[str, Any]]
    is_safe: bool
    verdict_per_chunk: List[ScanVerdict] = field(default_factory=list)


@dataclass
class ToolCallScanResult:
    """Result from scanning tool call before execution"""
    is_safe: bool
    tool_name: str
    user_intent_safe: bool
    tool_args_safe: bool
    combined_score: float
    user_message_verdict: ScanVerdict
    tool_context_verdict: Optional[ScanVerdict] = None
    recommendation: str = "proceed"


# ============================================================================
# Core Scanner Functions
# ============================================================================

def scan_text(text: str, client, scan_type: str = "input", policy: Optional[Dict[str, Any]] = None, meta: Optional[Dict[str, Any]] = None) -> ScanVerdict:
    """Scan text for prompt injection. Returns ScanVerdict with is_safe and score."""
    if not text:
        return ScanVerdict(is_safe=True, score=0.0, scan_type=scan_type, tag="empty_input", meta=meta or {})
    
    threshold = (policy or {}).get("threshold", 0.65)
    
    try:
        result = client.analyze_text(text, scan_type=scan_type)
        if not result["success"]:
            logger.warning(f"Analysis failed: {result.get('error')}")
            return ScanVerdict(is_safe=False, score=1.0, scan_type=scan_type, 
                            tag=result.get("tag", "unknown"), meta=meta or {})
        
        score = next((item["result"] for item in result.get("analysis", [])
                    if item.get("type") == "score" and item.get("name") == "prompt_injection"), 0.0)
        
        return ScanVerdict(
            is_safe=score < threshold,
            score=score,
            scan_type=scan_type,
            tag=result.get("tag", ""),
            meta=meta or {},
            raw_analysis=result.get("analysis", [])
        )
    except Exception as e:
        logger.error(f"Error scanning text: {str(e)}")
        return ScanVerdict(is_safe=False, score=1.0, scan_type=scan_type, tag="error", meta=meta or {})


def scan_messages(messages: List[Dict[str, str]], client, scan_type: str = "input", 
                policy: Optional[Dict[str, Any]] = None, meta: Optional[Dict[str, Any]] = None) -> ScanVerdict:
    """Scan a list of chat messages for prompt injection."""
    if not messages:
        return ScanVerdict(is_safe=True, score=0.0, scan_type=scan_type, tag="empty_messages", meta=meta or {})
    
    threshold = (policy or {}).get("threshold", 0.65)
    texted_content = "\n".join([f"[{msg.get('role', 'unknown')}]: {msg.get('content', '')}" for msg in messages])
    
    try:
        result = client.analyze_text(texted_content, scan_type=scan_type)
        if not result["success"]:
            logger.warning(f"Messages analysis failed: {result.get('error')}")
            return ScanVerdict(is_safe=False, score=1.0, scan_type=scan_type, 
                            tag=result.get("tag", "unknown"), meta=meta or {})
        
        score = next((item["result"] for item in result.get("analysis", [])
                    if item.get("type") == "score" and item.get("name") == "prompt_injection"), 0.0)
        
        return ScanVerdict(is_safe=score < threshold, score=score, scan_type=scan_type,
                        tag=result.get("tag", ""), meta=meta or {}, raw_analysis=result.get("analysis", []))
    except Exception as e:
        logger.error(f"Error scanning messages: {str(e)}")
        return ScanVerdict(is_safe=False, score=1.0, scan_type=scan_type, tag="error", meta=meta or {})


def scan_rag_chunks(query: str, chunks: List[Union[str, Dict[str, Any]]], client, policy: Optional[Dict[str, Any]] = None, meta: Optional[Dict[str, Any]] = None) -> RagScanResult:
    if not chunks:
        return RagScanResult(query=query, total_chunks=0, safe_chunks=[], flagged_chunks=[], is_safe=True)
    policy = policy or {}
    meta = meta or {}
    
    threshold = policy.get("threshold", 0.65)
    limit = policy.get("max_chunks_to_scan", len(chunks))
    
    safe_chunks = []
    flagged_chunks = []
    verdicts = []

    for i, chunk in enumerate(chunks[:limit]):
        if isinstance(chunk, str):
            chunk_text = chunk
        else:
            chunk_text = chunk.get("text") or chunk.get("content") or str(chunk)
        
        verdict = scan_text(
            chunk_text, 
            scan_type="input", 
            policy={"threshold": threshold},
            meta={**meta, "chunk_index": i},
            client=client
        )
        verdicts.append(verdict)

        chunk_data = {"text": chunk_text, "index": i, "score": verdict.score, "original": chunk}
        
        if verdict.is_safe:
            safe_chunks.append(chunk_data)
        else:
            flagged_chunks.append({**chunk_data, "reason": "flagged"})

    query_verdict = scan_text(query, scan_type="input", policy={"threshold": threshold}, client=client)
    all_verdicts = [query_verdict] + verdicts

    return RagScanResult(
        query=query,
        total_chunks=len(chunks),
        safe_chunks=safe_chunks,
        flagged_chunks=flagged_chunks,
        is_safe=query_verdict.is_safe and len(flagged_chunks) == 0,
        verdict_per_chunk=all_verdicts
    )


def scan_tool_call(user_message: str, tool_name: str, tool_args: Dict[str, Any], client,
                tool_schema: Optional[Union[str, Dict[str, Any]]] = None, 
                policy: Optional[Dict[str, Any]] = None, meta: Optional[Dict[str, Any]] = None) -> ToolCallScanResult:
    """Scan a tool call before execution to prevent injection-based attacks."""
    threshold = (policy or {}).get("threshold", 0.65)
    
    tool_context_parts = [f"Tool: {tool_name}"]
    if tool_schema:
        tool_context_parts.append(f"{'Description' if isinstance(tool_schema, str) else 'Schema'}: {tool_schema}")
    tool_context_parts.append(f"Arguments: {str(tool_args)}")
    tool_context = "\n".join(tool_context_parts)
    
    try:
        user_verdict = scan_text(user_message, client, scan_type="input", 
                                policy={"threshold": threshold}, meta={**(meta or {}), "component": "tool_call_user_intent"})
        tool_context_verdict = scan_text(tool_context, client, scan_type="input",
                                        policy={"threshold": threshold}, meta={**(meta or {}), "tool": tool_name, "component": "tool_context"})
        
        combined_score = round(((user_verdict.score + tool_context_verdict.score) / 2.0), 1)
        is_safe = user_verdict.is_safe and tool_context_verdict.is_safe
        recommendation = "proceed" if is_safe else ("block" if combined_score >= 0.85 else "review" if combined_score >= 0.50 else "proceed")
        
        return ToolCallScanResult(is_safe=is_safe, tool_name=tool_name, user_intent_safe=user_verdict.is_safe,
                                tool_args_safe=tool_context_verdict.is_safe, combined_score=combined_score,
                                user_message_verdict=user_verdict, tool_context_verdict=tool_context_verdict, recommendation=recommendation)
    except Exception as e:
        logger.error(f"Error scanning tool call: {str(e)}")
        return ToolCallScanResult(is_safe=False, tool_name=tool_name, user_intent_safe=False, tool_args_safe=False,
                                combined_score=1.0, user_message_verdict=ScanVerdict(is_safe=False, score=1.0, scan_type="input", tag="error"),
                                recommendation="block")