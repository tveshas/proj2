"""Core quiz solving logic."""
import asyncio
import logging
import re
import json
import base64
from typing import Optional, Dict, Any, Union
from bs4 import BeautifulSoup
import httpx
from datetime import datetime, timedelta

from app.config import config
from app.browser import browser_manager
from app.llm_client import LLMClient

logger = logging.getLogger(__name__)


class QuizSolver:
    """Handles quiz solving workflow."""
    
    def __init__(self):
        self.llm_client = LLMClient()
        self.http_client = httpx.AsyncClient(timeout=60.0)
    
    async def solve_quiz(self, url: str, email: str, secret: str):
        """
        Main method to solve a quiz starting from a URL.
        Handles quiz chains automatically with retry logic.
        
        Args:
            url: Initial quiz URL
            email: Student email
            secret: Student secret
        """
        start_time = datetime.now()
        current_url = url
        
        try:
            while current_url:
                # Check timeout (3 minutes from start)
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed > config.QUIZ_TIMEOUT:
                    logger.error(f"Quiz timeout exceeded for {url}")
                    break
                
                logger.info(f"Solving quiz at: {current_url}")
                
                # Solve current quiz with retry logic
                result = await self._solve_single_quiz_with_retry(
                    current_url, email, secret, start_time
                )
                
                if not result:
                    logger.error(f"Failed to solve quiz at {current_url}")
                    break
                
                # Check if answer was correct
                if result.get("correct"):
                    logger.info("Answer was correct!")
                    # Check if we got a new URL to continue
                    if result.get("url"):  # Next URL in response
                        current_url = result["url"]
                        logger.info(f"Moving to next quiz: {current_url}")
                    else:
                        logger.info("Quiz chain completed")
                        break
                else:
                    # Answer was wrong
                    logger.warning(f"Answer was incorrect: {result.get('reason')}")
                    # Check if we got a next URL to skip to
                    if result.get("url"):
                        logger.info(f"Received next URL, skipping to: {result['url']}")
                        current_url = result["url"]
                    # Otherwise, retry logic is handled in _solve_single_quiz_with_retry
                    else:
                        logger.error("No next URL provided and answer was wrong")
                        break
                    
        except Exception as e:
            logger.error(f"Error in quiz solving workflow: {e}", exc_info=True)
        finally:
            await self.http_client.aclose()
    
    async def _solve_single_quiz_with_retry(
        self, 
        url: str, 
        email: str, 
        secret: str, 
        start_time: datetime,
        max_retries: int = 3
    ) -> Optional[Dict[str, Any]]:
        """
        Solve a single quiz with retry logic for wrong answers.
        
        Args:
            url: Quiz URL
            email: Student email
            secret: Student secret
            start_time: Start time of the quiz (for timeout checking)
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dict with 'correct', 'url' (next_url), 'reason' or None if failed
        """
        # Step 1: Load and parse quiz page (only once)
        html_content = await browser_manager.get_page_content(url)
        quiz_instructions = self._extract_quiz_instructions(html_content)
        
        if not quiz_instructions:
            logger.error("Could not extract quiz instructions")
            return None
        
        logger.info(f"Quiz instructions extracted: {quiz_instructions[:200]}...")
        
        # Step 2: Extract submit URL from instructions
        submit_url = self._extract_submit_url(quiz_instructions)
        if not submit_url:
            logger.error("Could not find submit URL in quiz instructions")
            return None
        
        logger.info(f"Submit URL: {submit_url}")
        
        # Try solving with retries
        for attempt in range(max_retries):
            # Check timeout before each attempt
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > config.QUIZ_TIMEOUT:
                logger.error("Timeout exceeded during retry")
                return None
            
            logger.info(f"Attempt {attempt + 1}/{max_retries}")
            
            # Step 3: Solve quiz using LLM
            answer = await self._solve_with_llm(quiz_instructions, url)
            
            if answer is None:
                logger.error("Failed to generate answer")
                continue  # Try again
            
            logger.info(f"Generated answer: {answer} (type: {type(answer).__name__})")
            
            # Step 4: Submit answer
            result = await self._submit_answer(
                submit_url, email, secret, url, answer
            )
            
            if not result:
                logger.error("Failed to submit answer")
                continue  # Try again
            
            # If correct, return immediately
            if result.get("correct"):
                return result
            
            # If wrong but we have a next URL, return it (can skip to next)
            if result.get("url"):
                return result
            
            # If wrong and no next URL, we can retry
            logger.warning(f"Answer incorrect, reason: {result.get('reason')}")
            if attempt < max_retries - 1:
                logger.info("Retrying with new answer...")
                # Could potentially use the reason to improve the next attempt
                # For now, just retry
        
        # All retries exhausted
        logger.error("All retry attempts exhausted")
        return None
    
    async def _solve_single_quiz(self, url: str, email: str, secret: str) -> Optional[Dict[str, Any]]:
        """
        Solve a single quiz (deprecated - use _solve_single_quiz_with_retry).
        
        Returns:
            Dict with 'correct', 'next_url', 'reason' or None if failed
        """
        # This method is kept for backwards compatibility but not used
        return await self._solve_single_quiz_with_retry(
            url, email, secret, datetime.now()
        )
    
    def _extract_quiz_instructions(self, html_content: str) -> Optional[str]:
        """Extract quiz instructions from HTML."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # First, try to get rendered content from result div (after JS execution)
            result_div = soup.find('div', id='result')
            if result_div and result_div.get_text(strip=True):
                # Get the inner HTML which should contain the rendered content
                inner_html = result_div.decode_contents()
                if inner_html:
                    inner_soup = BeautifulSoup(inner_html, 'html.parser')
                    return inner_soup.get_text(separator='\n', strip=True)
            
            # Look for script tags that might contain base64 encoded content
            scripts = soup.find_all('script')
            for script in scripts:
                script_content = script.string
                if script_content and 'atob' in script_content:
                    # Extract base64 content - handle multi-line strings with re.DOTALL
                    # Pattern: atob(`...`) or atob("...") or atob('...')
                    patterns = [
                        r'atob\(`([^`]+)`\)',  # Template literal with backticks
                        r'atob\(["\']([^"\']+)["\']\)',  # String with quotes
                        r'atob\(\s*["\']([^"\']+)["\']\s*\)',  # With whitespace
                    ]
                    
                    for pattern in patterns:
                        base64_match = re.search(pattern, script_content, re.DOTALL)
                        if base64_match:
                            try:
                                # Clean up the base64 string (remove whitespace/newlines)
                                base64_str = base64_match.group(1).strip().replace('\n', '').replace(' ', '')
                                decoded = base64.b64decode(base64_str).decode('utf-8')
                                # Parse the decoded HTML
                                decoded_soup = BeautifulSoup(decoded, 'html.parser')
                                return decoded_soup.get_text(separator='\n', strip=True)
                            except Exception as e:
                                logger.warning(f"Error decoding base64: {e}")
                                continue
            
            # Fallback: extract text from result div or body
            if result_div:
                return result_div.get_text(separator='\n', strip=True)
            
            # Last resort: get all text
            return soup.get_text(separator='\n', strip=True)
            
        except Exception as e:
            logger.error(f"Error extracting instructions: {e}")
            return None
    
    def _extract_submit_url(self, instructions: str) -> Optional[str]:
        """Extract submit URL from quiz instructions."""
        # Look for URLs in the instructions, prioritizing submit URLs
        url_patterns = [
            r'Post.*?to\s+(https?://[^\s<>"\'\)]+)',  # "Post to https://..."
            r'submit.*?to\s+(https?://[^\s<>"\'\)]+)',  # "submit to https://..."
            r'Post.*?your.*?answer.*?to\s+(https?://[^\s<>"\'\)]+)',  # "Post your answer to..."
            r'(https?://[^\s<>"\'\)]*submit[^\s<>"\'\)]*)',  # URLs containing "submit"
            r'https?://[^\s<>"\'\)]+',  # Standard URL pattern (fallback)
        ]
        
        # First, try patterns that capture submit URLs specifically
        for pattern in url_patterns:
            matches = re.findall(pattern, instructions, re.IGNORECASE)
            if matches:
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    # Clean up the URL (remove trailing punctuation)
                    url = match.rstrip('.,;:!?)')
                    # Prefer URLs with "submit" in them
                    if 'submit' in url.lower():
                        return url
                
                # Return first match if no submit URL found
                first_match = matches[0]
                if isinstance(first_match, tuple):
                    first_match = first_match[0]
                return first_match.rstrip('.,;:!?)')
        
        logger.warning("Could not extract submit URL from instructions")
        return None
    
    async def _solve_with_llm(self, instructions: str, url: str) -> Optional[Union[bool, int, float, str, Dict]]:
        """Use LLM to solve the quiz based on instructions."""
        return await self.llm_client.solve_quiz(instructions, url)
    
    async def _submit_answer(
        self, 
        submit_url: str, 
        email: str, 
        secret: str, 
        quiz_url: str, 
        answer: Union[bool, int, float, str, Dict]
    ) -> Optional[Dict[str, Any]]:
        """
        Submit answer to the quiz endpoint.
        
        Returns:
            Dict with 'correct', 'next_url', 'reason'
        """
        # Prepare payload
        payload = {
            "email": email,
            "secret": secret,
            "url": quiz_url,
            "answer": answer
        }
        
        # Check payload size
        payload_json = json.dumps(payload)
        if len(payload_json.encode('utf-8')) > config.MAX_PAYLOAD_SIZE:
            logger.error(f"Payload too large: {len(payload_json)} bytes")
            return None
        
        try:
            logger.info(f"Submitting answer to {submit_url}")
            response = await self.http_client.post(
                submit_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Submission result: {result}")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error submitting answer: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Error submitting answer: {e}")
            return None

