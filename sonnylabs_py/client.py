import requests
import logging
import random
import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sonnylabs_py")

class SonnyLabsClient:
    def __init__(self, api_token, base_url, analysis_id, timeout=5):
        """
        Initialize a SonnyLabs API client for a specific chatbot application
        
        Args:
            api_token: Your SonnyLabs API token (recommended to load from .env as SONNYLABS_API_TOKEN)
            base_url: Base URL for the SonnyLabs API
            analysis_id: The analysis ID associated with this chatbot (from website UI, recommended to load from .env as SONNYLABS_ANALYSIS_ID)
            timeout: Request timeout in seconds (default: 5)
        """
        self.api_token = api_token
        self.base_url = base_url
        self.analysis_id = analysis_id
        self.timeout = timeout
    
    def _generate_tag(self):
        """
        Generate a unique tag with analysis_id, datetime, and random integers
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = ''.join([str(random.randint(0, 9)) for _ in range(4)])
        return f"{self.analysis_id}_{timestamp}_{random_suffix}"
    
    def analyze_text(self, text, scan_type="input", tag=None):
        """
        Analyze text for security concerns
        
        Args:
            text: Text to analyze (from chatbot)
            scan_type: Either "input" or "output"
            tag: Optional tag to use for this analysis. If provided, this exact tag will be used instead of generating a new one. Useful for linking prompts with their responses.
        
        Returns:
            Dictionary with analysis results
        """
        try:
            # Use provided tag or generate a new one if none provided
            if tag is None:
                tag = self._generate_tag()
            
            logger.info(f"Analyzing {scan_type} content with tag '{tag}'")
            
            url = f"{self.base_url}/v1/analysis/{self.analysis_id}"
            headers = {'Authorization': f'Bearer {self.api_token}'}
            params = {
                "tag": tag,
                "scan_type": scan_type
            }
            
            response = requests.post(
                url,
                params=params,
                data=text,
                headers=headers,
                timeout=self.timeout
            )
            
            logger.info(f"Response status: {response.status_code}")
            
            if 200 <= response.status_code < 300:
                return {
                    "success": True,
                    "tag": tag,
                    "analysis": response.json()["analysis"]
                }
            else:
                logger.error(f"API error: {response.status_code}")
                return {
                    "success": False,
                    "tag": tag,
                    "error": f"API error: {response.status_code}",
                    "analysis": []
                }
                
        except Exception as e:
            logger.error(f"Error analyzing text: {str(e)}")
            return {
                "success": False,
                "tag": tag if 'tag' in locals() else None,
                "error": str(e),
                "analysis": []
            }
    
    def get_prompt_injections(self, analysis_result, threshold=0.65):
        """
        Extract prompt injection issues from analysis results
        
        Args:
            analysis_result: The result dictionary from analyze_text
            threshold: The confidence threshold above which to consider a prompt injection detected (default: 0.65)
            
        Returns:
            Dictionary with prompt injection score and detection status or None if no issue
        """
        if not analysis_result["success"]:
            return None
            
        for item in analysis_result["analysis"]:
            if item["type"] == "score" and item["name"] == "prompt_injection":
                score = item["result"]
                return {
                    "score": score,
                    "tag": analysis_result["tag"],
                    "detected": score > threshold,
                    "threshold": threshold
                }
                
        return None
    
    def is_prompt_injection(self, analysis_result, threshold=0.65):
        """
        Directly check if prompt injection was detected in analysis results
        
        Args:
            analysis_result: The result dictionary from analyze_text
            threshold: The confidence threshold above which to consider a prompt injection detected (default: 0.65)
            
        Returns:
            Boolean: True if prompt injection was detected above threshold, False otherwise
        """
        injection_info = self.get_prompt_injections(analysis_result, threshold)
        if injection_info is None:
            return False
        return injection_info["detected"]
        
    def get_pii(self, analysis_result):
        """
        Extract PII issues from analysis results
        
        Args:
            analysis_result: The result dictionary from analyze_text
            
        Returns:
            List of PII items found or empty list if none
        """
        if not analysis_result["success"]:
            return []
            
        for item in analysis_result["analysis"]:
            if item["type"] == "PII":
                return [{
                    "label": pii_item["label"],
                    "text": pii_item["text"],
                    "tag": analysis_result["tag"]
                } for pii_item in item["result"]]
                
        return []