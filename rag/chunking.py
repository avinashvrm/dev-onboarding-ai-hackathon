import re
import ast
import pdfplumber
from typing import List, Union
import io

def chunk_document(content: Union[bytes, str], file_type: str) -> List[str]:
    """
    Chunk document content based on file type.
    
    Args:
        content: Document content as bytes or string
        file_type: Type of the document (pdf, txt, md)
        
    Returns:
        List of text chunks
    """
    if file_type == 'pdf':
        return chunk_pdf(content)
    elif file_type in ['txt', 'md']:
        return chunk_text(content)
    else:
        raise ValueError(f"Unsupported document type: {file_type}")

def chunk_pdf(content: bytes) -> List[str]:
    """
    Chunk PDF content by paragraphs.
    """
    chunks = []
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                # Split by double newlines to get paragraphs
                paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
                chunks.extend(paragraphs)
    return chunks

def chunk_text(content: Union[bytes, str]) -> List[str]:
    """
    Chunk text content by paragraphs.
    """
    if isinstance(content, bytes):
        content = content.decode('utf-8')
    
    # Split by double newlines to get paragraphs
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    return paragraphs

def chunk_code(content: Union[bytes, str], language: str) -> List[str]:
    """
    Chunk code content by functions and classes.
    
    Args:
        content: Code content as bytes or string
        language: Programming language of the code
        
    Returns:
        List of code chunks
    """
    if isinstance(content, bytes):
        content = content.decode('utf-8')
    
    if language == 'py':
        return chunk_python(content)
    else:
        # For other languages, use regex-based chunking
        return chunk_code_regex(content, language)

def chunk_python(content: str) -> List[str]:
    """
    Chunk Python code using AST.
    """
    chunks = []
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                # Get the source code of the function/class
                chunk = ast.get_source_segment(content, node)
                if chunk:
                    chunks.append(chunk)
    except SyntaxError:
        # Fallback to regex-based chunking if AST parsing fails
        return chunk_code_regex(content, 'py')
    
    return chunks

def chunk_code_regex(content: str, language: str) -> List[str]:
    """
    Chunk code using regex patterns based on language.
    """
    chunks = []
    
    # Common patterns for different languages
    patterns = {
        'py': r'def\s+\w+\s*\([^)]*\)\s*:.*?(?=def|\Z)',
        'js': r'(?:function\s+\w+\s*\([^)]*\)|class\s+\w+).*?(?=function|class|\Z)',
        'php': r'function\s+\w+\s*\([^)]*\).*?(?=function|\Z)',
        'ts': r'(?:function\s+\w+\s*\([^)]*\)|class\s+\w+).*?(?=function|class|\Z)'
    }
    
    pattern = patterns.get(language)
    if pattern:
        matches = re.finditer(pattern, content, re.DOTALL)
        chunks = [match.group(0).strip() for match in matches if match.group(0).strip()]
    
    return chunks 