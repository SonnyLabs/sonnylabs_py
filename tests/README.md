# Tests for SonnyLabs Helper Module

Comprehensive test suite for the `sonnylabs.helper` module covering all scanning functions, data classes, and client configuration.

## Running Tests

### Prerequisites

```bash
pip install pytest pytest-cov pytest-mock
```

### Run All Tests

```bash
pytest tests/
```

### Run with Verbose Output

```bash
pytest tests/ -v
```

### Run with Coverage Report

```bash
pytest tests/ --cov=sonnylabs.helper --cov-report=html
# Coverage report will be in htmlcov/index.html
```

### Run Specific Test Class

```bash
pytest tests/test_helper.py::TestScanText -v
```

### Run Specific Test

```bash
pytest tests/test_helper.py::TestScanText::test_scan_text_clean_input -v
```

## Test Coverage

### Data Classes (27 tests)
- **ScanVerdict**: Safe/unsafe verdicts, properties, string representation, metadata
- **RagScanResult**: Safe/flagged chunks, counts, string representation
- **ToolCallScanResult**: Safe tool calls, recommendations, risky scenarios

### Core Functions (44 tests)

#### scan_text() (11 tests)
- Empty string handling
- Clean input detection
- Injection detection
- Custom thresholds
- Metadata tracking
- Different scan types
- API failure (fail-secure)
- Exception handling
- Explicit client passing
- Client configuration errors
- Raw analysis preservation

#### scan_messages() (7 tests)
- Empty message list
- Single and multiple messages
- Full conversations
- Injection detection in conversations
- Metadata tracking
- API failures
- Exception handling

#### scan_rag_chunks() (8 tests)
- Empty chunk list
- All safe chunks (string format)
- Mixed safe/unsafe chunks
- Dict format chunks
- Policy-based chunk limiting
- Metadata tracking
- Result structure validation

#### scan_tool_call() (8 tests)
- Safe tool calls
- Unsafe user intent
- Block recommendations (high score)
- Review recommendations (medium score)
- String schema format
- Dict schema format
- Exception handling

### Client Configuration (5 tests)
- Client configuration
- Getting configured client
- Error when not configured
- Client reconfiguration

### Integration Tests (2 tests)
- Full agentic workflow
- Injection attack detection

### Edge Cases (6 tests)
- Score at threshold boundary
- Very long text
- Special characters
- Unicode characters
- Large chunk lists with limiting

## Test Organization

```
tests/
├── __init__.py              # Package marker
├── conftest.py              # Shared fixtures and configuration
└── test_helper.py           # Main test suite (94 tests)
```

## Key Testing Patterns

### Mocking the SonnyLabsClient

```python
@pytest.fixture
def mock_client():
    return Mock()

def test_scan_text_clean_input(mock_client):
    mock_client.analyze_text.return_value = {
        "success": True,
        "tag": "test",
        "analysis": [{"type": "score", "name": "prompt_injection", "result": 0.15}]
    }
    configure_client(mock_client)
    verdict = scan_text("Hello")
    assert verdict.is_safe is True
```

### Testing Fail-Secure Behavior

```python
def test_scan_text_api_failure(mock_client):
    mock_client.analyze_text.return_value = {"success": False, "error": "API error"}
    configure_client(mock_client)
    
    verdict = scan_text("text")
    # Should fail-secure: treat as unsafe
    assert verdict.is_safe is False
    assert verdict.score == 1.0
```

### Testing Thresholds

```python
def test_scan_text_custom_threshold(mock_client):
    mock_client.analyze_text.return_value = {
        "success": True,
        "analysis": [{"type": "score", "name": "prompt_injection", "result": 0.7}]
    }
    configure_client(mock_client)
    
    # Default threshold 0.65: score 0.7 is unsafe
    verdict1 = scan_text("text")
    assert verdict1.is_safe is False
    
    # Higher threshold 0.75: score 0.7 is safe
    verdict2 = scan_text("text", policy={"threshold": 0.75})
    assert verdict2.is_safe is True
```

## Coverage Summary

- **Lines Covered**: ~94 tests covering all major functions and edge cases
- **Mocking Strategy**: Complete isolation from API through mocks
- **Fail-Secure Pattern**: All error paths verified to treat failures as unsafe
- **Edge Cases**: Empty inputs, unicode, special chars, large datasets
- **Integration**: Full workflow simulation without API calls

## Contributing Tests

When adding new features to `helper.py`:

1. Add tests to appropriate class in `test_helper.py`
2. Follow the existing naming convention: `test_{function}_{scenario}`
3. Use fixtures for common setup (`mock_client`, mock responses)
4. Test both success and failure paths
5. Verify fail-secure behavior for all error conditions
6. Add integration test if the feature affects the complete workflow

## Example: Adding a Test

```python
class TestScanText:
    def test_scan_text_new_feature(self, mock_client):
        """Test new feature description"""
        # Setup
        mock_client.analyze_text.return_value = {
            "success": True,
            "tag": "test",
            "analysis": [{"type": "score", "name": "prompt_injection", "result": 0.3}]
        }
        configure_client(mock_client)
        
        # Execute
        verdict = scan_text("text")
        
        # Assert
        assert verdict.is_safe is True
        assert verdict.score == 0.3
```

## GitHub Actions / CI/CD

Add to your GitHub Actions workflow:

```yaml
- name: Run Tests
  run: |
    pip install -e .
    pytest tests/ --cov=sonnylabs.helper --cov-report=xml

- name: Upload Coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
```

## Troubleshooting

### Import Errors

If you get import errors, ensure the package is installed in development mode:

```bash
pip install -e .
```

### Global State Issues

Tests automatically reset global client state through the `cleanup_global_state` fixture. If tests fail due to state leakage, check that the fixture is being used (it's marked `autouse=True`).

### Mock Issues

If a test expects a certain number of calls but gets different count:

```python
# Verify exact call count
assert mock_client.analyze_text.call_count == expected_count

# Check call arguments
mock_client.analyze_text.assert_called_with(expected_text, scan_type=expected_type)
```
