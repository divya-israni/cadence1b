"""
PDF parsing module for extracting text from PDF files.
"""
import io
from typing import Optional
from fastapi import UploadFile


def parse_pdf(file: UploadFile) -> str:
    """
    Extract text from PDF file.
    
    Args:
        file: FastAPI UploadFile object containing PDF
    
    Returns:
        Extracted text as string
    
    Raises:
        ValueError: If PDF cannot be parsed or is invalid
    """
    try:
        # Try pdfplumber first (better for complex PDFs)
        try:
            import pdfplumber
            
            content = file.file.read()
            file.file.seek(0)  # Reset file pointer
            
            text_parts = []
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            
            if not text_parts:
                raise ValueError("No text could be extracted from PDF")
            
            return "\n".join(text_parts)
        
        except ImportError:
            # Fallback to PyPDF2
            import PyPDF2
            
            content = file.file.read()
            file.file.seek(0)  # Reset file pointer
            
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text_parts = []
            
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
            
            if not text_parts:
                raise ValueError("No text could be extracted from PDF")
            
            return "\n".join(text_parts)
    
    except Exception as e:
        raise ValueError(f"Error parsing PDF: {str(e)}")

