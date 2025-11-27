"""Browser automation using Playwright for rendering JavaScript pages."""
import asyncio
import logging
from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError
from typing import Optional

logger = logging.getLogger(__name__)


class BrowserManager:
    """Manages Playwright browser instances."""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self._lock = asyncio.Lock()
    
    async def initialize(self):
        """Initialize Playwright and browser."""
        if self.browser is None:
            async with self._lock:
                if self.browser is None:
                    self.playwright = await async_playwright().start()
                    self.browser = await self.playwright.chromium.launch(
                        headless=True,
                        args=['--no-sandbox', '--disable-setuid-sandbox']
                    )
                    logger.info("Browser initialized")
    
    async def close(self):
        """Close browser and playwright."""
        if self.browser:
            await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            self.browser = None
            self.playwright = None
            logger.info("Browser closed")
    
    async def get_page_content(self, url: str, timeout: int = 30000) -> str:
        """
        Navigate to URL and return rendered HTML content.
        
        Args:
            url: URL to visit
            timeout: Timeout in milliseconds
            
        Returns:
            Rendered HTML content
        """
        await self.initialize()
        
        page = await self.browser.new_page()
        try:
            logger.info(f"Navigating to {url}")
            await page.goto(url, wait_until="networkidle", timeout=timeout)
            
            # Wait a bit for any dynamic content
            await asyncio.sleep(2)
            
            # Get the rendered HTML
            content = await page.content()
            logger.info(f"Successfully loaded page: {len(content)} characters")
            return content
            
        except PlaywrightTimeoutError:
            logger.error(f"Timeout loading {url}")
            # Still try to get content even if timeout
            try:
                content = await page.content()
                return content
            except Exception as e:
                logger.error(f"Error getting content after timeout: {e}")
                raise
        except Exception as e:
            logger.error(f"Error loading page {url}: {e}")
            raise
        finally:
            await page.close()
    
    async def get_page_text(self, url: str, timeout: int = 30000) -> str:
        """
        Navigate to URL and return rendered text content.
        
        Args:
            url: URL to visit
            timeout: Timeout in milliseconds
            
        Returns:
            Rendered text content
        """
        await self.initialize()
        
        page = await self.browser.new_page()
        try:
            logger.info(f"Navigating to {url} for text extraction")
            await page.goto(url, wait_until="networkidle", timeout=timeout)
            
            # Wait for dynamic content
            await asyncio.sleep(2)
            
            # Get the text content
            text = await page.inner_text("body")
            logger.info(f"Successfully extracted text: {len(text)} characters")
            return text
            
        except PlaywrightTimeoutError:
            logger.error(f"Timeout loading {url}")
            try:
                text = await page.inner_text("body")
                return text
            except Exception as e:
                logger.error(f"Error getting text after timeout: {e}")
                raise
        except Exception as e:
            logger.error(f"Error loading page {url}: {e}")
            raise
        finally:
            await page.close()


# Global browser manager instance
browser_manager = BrowserManager()

