import fitz  # PyMuPDF
from typing import List
import os
from loguru import logger

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise

def extract_text_from_txt(file_path: str) -> str:
    """Extract text from a TXT file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error reading text file: {str(e)}")
        raise

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        if end > text_length:
            end = text_length
        
        # Find the last period or newline in the chunk
        if end < text_length:
            last_period = text.rfind('.', start, end)
            last_newline = text.rfind('\n', start, end)
            split_point = max(last_period, last_newline)
            if split_point != -1:
                end = split_point + 1

        chunks.append(text[start:end])
        start = end - overlap

    return chunks

def process_document(file_path: str) -> List[str]:
    """Process a document and return chunks of text."""
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.pdf':
        text = extract_text_from_pdf(file_path)
    elif file_ext == '.txt':
        text = extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")
    
    return chunk_text(text) 