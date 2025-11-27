"""Web scraping tools."""
import logging
import httpx
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any

from app.browser import browser_manager

logger = logging.getLogger(__name__)


async def scrape_url(url: str) -> Dict[str, Any]:
    """
    Scrape a URL and return its content.
    
    Args:
        url: URL to scrape
        
    Returns:
        Dict with 'text', 'html', and 'links'
    """
    try:
        # Try using browser for JS-heavy sites
        html = await browser_manager.get_page_content(url)
        soup = BeautifulSoup(html, 'html.parser')
        
        text = soup.get_text(separator='\n', strip=True)
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        
        return {
            "text": text,
            "html": html[:10000],  # Limit HTML size
            "links": links[:100]  # Limit links
        }
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return {"error": str(e)}


async def download_file(url: str) -> Dict[str, Any]:
    """
    Download a file from URL.
    
    Args:
        url: URL of file to download
        
    Returns:
        Dict with file info and base64 content if small enough
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=60.0)
            response.raise_for_status()
            
            content = response.content
            content_type = response.headers.get('content-type', 'application/octet-stream')
            
            result = {
                "url": url,
                "content_type": content_type,
                "size": len(content)
            }
            
            # If file is small enough, include base64
            if len(content) < 10 * 1024 * 1024:  # 10MB limit
                import base64
                result["base64"] = base64.b64encode(content).decode('utf-8')
            else:
                result["note"] = "File too large for base64 encoding"
            
            return result
    except Exception as e:
        logger.error(f"Error downloading {url}: {e}")
        return {"error": str(e)}

