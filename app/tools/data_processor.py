"""Data processing tools."""
import logging
import base64
import io
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from PIL import Image
import PyPDF2
import pdfplumber

logger = logging.getLogger(__name__)


async def process_pdf(base64_content: str) -> Dict[str, Any]:
    """
    Process a PDF file from base64.
    
    Args:
        base64_content: Base64 encoded PDF content
        
    Returns:
        Dict with extracted text and metadata
    """
    try:
        pdf_bytes = base64.b64decode(base64_content)
        
        # Try pdfplumber first (better for tables)
        try:
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                text_parts = []
                for page in pdf.pages:
                    text_parts.append(page.extract_text() or "")
                    # Extract tables
                    tables = page.extract_tables()
                    if tables:
                        text_parts.append(f"\n[Found {len(tables)} table(s) on page {page.page_number}]\n")
                
                return {
                    "text": "\n".join(text_parts),
                    "num_pages": len(pdf.pages),
                    "method": "pdfplumber"
                }
        except Exception as e:
            logger.warning(f"pdfplumber failed: {e}, trying PyPDF2")
        
        # Fallback to PyPDF2
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        text_parts = []
        for page in pdf_reader.pages:
            text_parts.append(page.extract_text())
        
        return {
            "text": "\n".join(text_parts),
            "num_pages": len(pdf_reader.pages),
            "method": "PyPDF2"
        }
        
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        return {"error": str(e)}


async def process_csv(base64_content: str) -> Dict[str, Any]:
    """
    Process a CSV file from base64.
    
    Args:
        base64_content: Base64 encoded CSV content
        
    Returns:
        Dict with DataFrame info and summary
    """
    try:
        csv_bytes = base64.b64decode(base64_content)
        df = pd.read_csv(io.BytesIO(csv_bytes))
        
        return {
            "shape": list(df.shape),
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "head": df.head(10).to_dict('records'),
            "summary": df.describe().to_dict() if len(df.select_dtypes(include=[np.number]).columns) > 0 else None
        }
    except Exception as e:
        logger.error(f"Error processing CSV: {e}")
        return {"error": str(e)}


async def process_image(base64_content: str) -> Dict[str, Any]:
    """
    Process an image from base64.
    
    Args:
        base64_content: Base64 encoded image content (with or without data URI prefix)
        
    Returns:
        Dict with image metadata
    """
    try:
        # Remove data URI prefix if present
        if ',' in base64_content:
            base64_content = base64_content.split(',')[1]
        
        image_bytes = base64.b64decode(base64_content)
        image = Image.open(io.BytesIO(image_bytes))
        
        return {
            "format": image.format,
            "mode": image.mode,
            "size": list(image.size),
            "width": image.width,
            "height": image.height
        }
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return {"error": str(e)}

