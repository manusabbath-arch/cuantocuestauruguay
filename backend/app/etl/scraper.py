"""
Web scraping utilities for tariff data extraction.

This module provides optional Playwright-based scraping for websites
that require JavaScript rendering (like URSEA, Antel, etc.).

Usage:
    pip install playwright
    playwright install chromium
    
    from app.etl.scraper import scrape_with_playwright
    data = await scrape_with_playwright('https://example.com', selector='table')
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Playwright is optional; graceful fallback if not installed
try:
    from playwright.async_api import async_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not installed. Web scraping features unavailable. Install with: pip install playwright")


async def scrape_with_playwright(
    url: str, selector: str, timeout: int = 30000, wait_for_selector: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Scrape webpage using Playwright (handles JavaScript-rendered content).

    Args:
        url: Target URL to scrape
        selector: CSS selector for content to extract
        timeout: Maximum time to wait (ms)
        wait_for_selector: Optional selector to wait for before extracting

    Returns:
        Dictionary with page metadata and extracted content, or None on failure

    Requires:
        playwright >= 1.40.0
        chromium browser (install via: playwright install chromium)
    """
    if not PLAYWRIGHT_AVAILABLE:
        logger.error("Playwright not available. Install with: pip install playwright")
        return None

    try:
        async with async_playwright() as p:
            # Use chromium (headless, faster than full browser)
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                # Navigate and wait for content
                await page.goto(url, wait_until="networkidle", timeout=timeout)

                # Wait for specific selector if provided
                if wait_for_selector:
                    await page.wait_for_selector(wait_for_selector, timeout=timeout)

                # Extract HTML content
                content = await page.locator(selector).inner_html()

                return {"url": url, "status": "success", "content": content, "title": await page.title()}

            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                return {"url": url, "status": "error", "error": str(e)}

            finally:
                await browser.close()

    except Exception as e:
        logger.error(f"Playwright session error for {url}: {e}")
        return None


async def extract_table_from_page(url: str, table_selector: str = "table") -> Optional[List[Dict[str, str]]]:
    """
    Scrape a table from a web page and convert to structured data.

    Args:
        url: Target URL
        table_selector: CSS selector for table element

    Returns:
        List of dictionaries (rows) from the table
    """
    if not PLAYWRIGHT_AVAILABLE:
        logger.error("Playwright not available")
        return None

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(url, wait_until="networkidle")

                # Extract table and convert to JSON
                table_data = await page.evaluate(
                    f"""() => {{
                    const table = document.querySelector('{table_selector}');
                    if (!table) return null;
                    
                    const rows = [];
                    const headers = [];
                    
                    // Get headers
                    const headerCells = table.querySelectorAll('thead th, thead td');
                    headerCells.forEach(cell => headers.push(cell.textContent.trim()));
                    
                    // Get rows
                    const bodyCells = table.querySelectorAll('tbody tr');
                    bodyCells.forEach(row => {{
                        const rowData = {{}};
                        const cells = row.querySelectorAll('td');
                        cells.forEach((cell, idx) => {{
                            rowData[headers[idx] || `col_${{idx}}`] = cell.textContent.trim();
                        }});
                        rows.push(rowData);
                    }});
                    
                    return rows;
                }}"""
                )

                return table_data

            finally:
                await browser.close()

    except Exception as e:
        logger.error(f"Error extracting table from {url}: {e}")
        return None
