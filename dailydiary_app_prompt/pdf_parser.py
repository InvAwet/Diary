
import pdfplumber
import io
import pytesseract
import cv2
import numpy as np
from PIL import Image
from typing import Optional, Dict, List
import streamlit as st
import fitz  # PyMuPDF
import re

class PDFParser:
    """Enhanced PDF Parser with high-accuracy OCR and multilingual support"""
    
    def __init__(self):
        """Initialize PDF parser with OCR configuration"""
        self.setup_ocr()
    
    def setup_ocr(self):
        """Setup OCR with enhanced configuration for maximum accuracy"""
        # Configure Tesseract for high accuracy
        self.ocr_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,!?@#$%^&*()_+-=[]{}|;:\'\"<>/?`~àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿĀāĂăĄąĆćĈĉĊċČčĎďĐđĒēĔĕĖėĘęĚěĜĝĞğĠġĢģĤĥĦħĨĩĪīĬĭĮįİıĲĳĴĵĶķĸĹĺĻļĽľĿŀŁłŃńŅņŇňŉŊŋŌōŎŏŐőŒœŔŕŖŗŘřŚśŜŝŞşŠšŢţŤťŦŧŨũŪūŬŭŮůŰűŲųŴŵŶŷŸŹźŻżŽž'
        
        # Language configuration for multilingual support
        self.languages = 'eng+fra+deu+spa+ita+por+ara+chi_sim+chi_tra+jpn+kor'
    
    def extract_text_from_pdf(self, uploaded_file) -> str:
        """
        Extract text from PDF using multiple methods for maximum accuracy
        
        Args:
            uploaded_file: Uploaded PDF file
            
        Returns:
            str: Extracted text with preserved formatting
        """
        try:
            # Reset file pointer
            uploaded_file.seek(0)
            
            # Method 1: Try pdfplumber first (best for text-based PDFs)
            text_content = self._extract_with_pdfplumber(uploaded_file)
            
            # If pdfplumber fails or returns minimal text, try OCR
            if not text_content.strip() or len(text_content.strip()) < 50:
                uploaded_file.seek(0)
                text_content = self._extract_with_ocr(uploaded_file)
            
            # Clean and preserve formatting
            cleaned_text = self._clean_and_preserve_text(text_content)
            
            return cleaned_text
            
        except Exception as e:
            st.error(f"Error extracting text from PDF: {str(e)}")
            return ""
    
    def _extract_with_pdfplumber(self, uploaded_file) -> str:
        """Extract text using pdfplumber for text-based PDFs"""
        try:
            text_content = ""
            
            with pdfplumber.open(uploaded_file) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content += f"\n--- Page {page_num + 1} ---\n"
                            text_content += page_text + "\n"
                        
                        # Also try to extract tables
                        tables = page.extract_tables()
                        for table_num, table in enumerate(tables):
                            if table:
                                text_content += f"\n--- Table {table_num + 1} on Page {page_num + 1} ---\n"
                                for row in table:
                                    if row:
                                        row_text = " | ".join([str(cell) if cell else "" for cell in row])
                                        text_content += row_text + "\n"
                    
                    except Exception as e:
                        st.warning(f"Error extracting from page {page_num + 1}: {str(e)}")
                        continue
            
            return text_content
            
        except Exception as e:
            st.warning(f"PDFPlumber extraction failed: {str(e)}")
            return ""
    
    def _extract_with_ocr(self, uploaded_file) -> str:
        """Extract text using OCR for image-based or scanned PDFs"""
        try:
            text_content = ""
            
            # Convert PDF to images using PyMuPDF
            pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            
            for page_num in range(len(pdf_document)):
                try:
                    page = pdf_document.load_page(page_num)
                    
                    # Convert to image with high DPI for better OCR
                    mat = fitz.Matrix(3.0, 3.0)  # High resolution matrix
                    pix = page.get_pixmap(matrix=mat)
                    img_data = pix.tobytes("png")
                    
                    # Convert to PIL Image
                    pil_image = Image.open(io.BytesIO(img_data))
                    
                    # Enhance image for better OCR
                    enhanced_image = self._enhance_image_for_ocr(pil_image)
                    
                    # Perform OCR with multiple methods
                    page_text = self._perform_enhanced_ocr(enhanced_image)
                    
                    if page_text.strip():
                        text_content += f"\n--- Page {page_num + 1} (OCR) ---\n"
                        text_content += page_text + "\n"
                
                except Exception as e:
                    st.warning(f"OCR failed for page {page_num + 1}: {str(e)}")
                    continue
            
            pdf_document.close()
            return text_content
            
        except Exception as e:
            st.warning(f"OCR extraction failed: {str(e)}")
            return ""
    
    def _enhance_image_for_ocr(self, pil_image):
        """Enhance image quality for better OCR accuracy"""
        try:
            # Convert PIL to OpenCV
            cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (1, 1), 0)
            
            # Apply adaptive threshold for better text separation
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Morphological operations to clean up
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            # Convert back to PIL Image
            enhanced_image = Image.fromarray(cleaned)
            
            return enhanced_image
            
        except Exception as e:
            # Return original if enhancement fails
            return pil_image
    
    def _perform_enhanced_ocr(self, image):
        """Perform OCR with multiple configurations for maximum accuracy"""
        try:
            # Try multiple OCR configurations
            configs = [
                r'--oem 3 --psm 6',  # Default
                r'--oem 3 --psm 4',  # Single column
                r'--oem 3 --psm 3',  # Fully automatic
                r'--oem 3 --psm 1',  # Automatic with OSD
            ]
            
            best_text = ""
            max_confidence = 0
            
            for config in configs:
                try:
                    # Add language support
                    full_config = f'-l {self.languages} {config}'
                    
                    # Extract text with confidence
                    data = pytesseract.image_to_data(image, config=full_config, output_type=pytesseract.Output.DICT)
                    
                    # Calculate average confidence
                    confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                    
                    # Get text
                    text = pytesseract.image_to_string(image, config=full_config)
                    
                    # Keep the best result
                    if avg_confidence > max_confidence and text.strip():
                        max_confidence = avg_confidence
                        best_text = text
                
                except Exception as e:
                    continue
            
            # If no good OCR result, try with just English
            if not best_text.strip():
                best_text = pytesseract.image_to_string(image, lang='eng', config=r'--oem 3 --psm 6')
            
            return best_text
            
        except Exception as e:
            return ""
    
    def _clean_and_preserve_text(self, text: str) -> str:
        """Clean text while preserving formatting and multilingual content"""
        if not text:
            return ""
        
        # Remove excessive whitespace but preserve structure
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove excessive spaces but keep single spaces
            cleaned_line = ' '.join(line.split())
            
            # Preserve important formatting indicators
            if cleaned_line.strip():
                cleaned_lines.append(cleaned_line)
            elif cleaned_lines and cleaned_lines[-1].strip():
                # Add a single empty line for paragraph breaks
                cleaned_lines.append("")
        
        # Join lines back together
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Fix common OCR errors while preserving foreign words
        cleaned_text = self._fix_common_ocr_errors(cleaned_text)
        
        # Remove duplicate consecutive spaces
        cleaned_text = re.sub(r' +', ' ', cleaned_text)
        
        # Remove excessive line breaks (more than 2 consecutive)
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
        
        return cleaned_text.strip()
    
    def _fix_common_ocr_errors(self, text: str) -> str:
        """Fix common OCR errors while preserving multilingual content"""
        # Common OCR character replacements (be conservative)
        replacements = {
            # Numbers often misread
            r'\b0(?=\d)': 'O',  # Leading zero might be O
            r'(?<=\d)0\b': 'O',  # Trailing zero might be O
            
            # Common punctuation errors
            r'\.{2,}': '...',  # Multiple dots to ellipsis
            r',{2,}': ',',     # Multiple commas to single
            
            # Common letter confusions (only obvious ones)
            r'\b1\b(?=\s+[A-Za-z])': 'I',  # Standalone 1 before letters is likely I
            r'\b0\b(?=\s+[A-Za-z])': 'O',  # Standalone 0 before letters is likely O
        }
        
        for pattern, replacement in replacements.items():
            text = re.sub(pattern, replacement, text)
        
        return text
    
    def extract_metadata(self, uploaded_file) -> Dict:
        """Extract metadata from PDF"""
        try:
            uploaded_file.seek(0)
            
            with pdfplumber.open(uploaded_file) as pdf:
                metadata = pdf.metadata or {}
                
                return {
                    'title': metadata.get('Title', ''),
                    'author': metadata.get('Author', ''),
                    'subject': metadata.get('Subject', ''),
                    'creator': metadata.get('Creator', ''),
                    'producer': metadata.get('Producer', ''),
                    'creation_date': metadata.get('CreationDate', ''),
                    'modification_date': metadata.get('ModDate', ''),
                    'page_count': len(pdf.pages)
                }
        
        except Exception as e:
            return {'error': str(e)}
