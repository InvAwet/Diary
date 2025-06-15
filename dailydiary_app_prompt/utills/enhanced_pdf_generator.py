
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.utils import ImageReader
import io
import os
from typing import List, Dict, Optional
from utils.data_models import DailyDiaryData
from PIL import Image

class EnhancedPDFGenerator:
    """Enhanced PDF Generator that creates a clean single-page Daily Diary form"""
    
    def __init__(self):
        self.page_width, self.page_height = A4
        self.margin = 10 * mm  # Reduced margin for more space
        self.setup_styles()
    
    def setup_styles(self):
        """Setup text styles for the PDF"""
        self.styles = getSampleStyleSheet()
        
        # Custom styles optimized for single page
        self.header_style = ParagraphStyle(
            'HeaderStyle',
            parent=self.styles['Normal'],
            fontSize=7,
            fontName='Helvetica-Bold'
        )
        
        self.normal_style = ParagraphStyle(
            'NormalStyle',
            parent=self.styles['Normal'],
            fontSize=6,
            fontName='Helvetica'
        )
        
        self.small_style = ParagraphStyle(
            'SmallStyle',
            parent=self.styles['Normal'],
            fontSize=5,
            fontName='Helvetica'
        )
    
    def generate_daily_diary_pdf(self, data: DailyDiaryData) -> bytes:
        """Generate clean single-page Daily Diary PDF"""
        try:
            buffer = io.BytesIO()
            
            # Create custom canvas for precise control
            c = canvas.Canvas(buffer, pagesize=A4)
            
            # Draw the complete form on single page
            self._draw_header_section(c, data)
            self._draw_title_section(c, data)
            self._draw_project_section(c, data)
            self._draw_date_time_section(c, data)
            self._draw_weather_section(c, data)
            self._draw_activities_section(c, data)
            self._draw_equipment_section(c, data)
            self._draw_personnel_section(c, data)
            self._draw_unsafe_acts_section(c, data)
            self._draw_additional_sections(c, data)
            self._draw_signatures_section(c, data)
            
            c.save()
            
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
            
        except Exception as e:
            raise Exception(f"Error generating PDF: {str(e)}")
    
    def _draw_header_section(self, c, data):
        """Draw compact header section with actual logos"""
        # Nicholas O'Dwyer logo (left)
        try:
            # Check for Nicholas O'Dwyer logo in attached_assets
            nicholas_logo_path = None
            ms_logo_path = None
            
            if os.path.exists("attached_assets"):
                for file in os.listdir("attached_assets"):
                    if "nicholas" in file.lower() or "dwyer" in file.lower() or "o'dwyer" in file.lower():
                        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                            nicholas_logo_path = os.path.join("attached_assets", file)
                    elif "ms" in file.lower() and "consultancy" in file.lower():
                        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                            ms_logo_path = os.path.join("attached_assets", file)
                    elif "MS-LOGO" in file:
                        ms_logo_path = os.path.join("attached_assets", file)
            
            # Draw Nicholas O'Dwyer logo or text
            if nicholas_logo_path and os.path.exists(nicholas_logo_path):
                try:
                    c.drawImage(nicholas_logo_path, 12*mm, 277*mm, width=28*mm, height=8*mm, preserveAspectRatio=True, mask='auto')
                except:
                    # Fallback to text if image fails
                    c.setFont("Helvetica-Bold", 8)
                    c.drawString(15*mm, 280*mm, "NICHOLAS O'DWYER")
                    c.rect(12*mm, 275*mm, 20*mm, 10*mm)
            else:
                c.setFont("Helvetica-Bold", 8)
                c.drawString(15*mm, 280*mm, "NICHOLAS O'DWYER")
                c.rect(12*mm, 275*mm, 20*mm, 10*mm)
            
        except Exception as e:
            # Fallback to text
            c.setFont("Helvetica-Bold", 8)
            c.drawString(15*mm, 280*mm, "NICHOLAS O'DWYER")
            c.rect(12*mm, 275*mm, 20*mm, 10*mm)
        
        # Company details (center) - Compact layout
        c.setFont("Helvetica", 5)
        company_details = [
            "Unit E4, Nutgrove Office Park, Nutgrove Avenue, Dublin 14",
            "T +353 1 296 9000 | F +353 1 296 9001 | E dublin@nodwyer.com | W www.nodwyer.com"
        ]
        
        c.drawString(45*mm, 282*mm, company_details[0])
        c.drawString(45*mm, 278*mm, company_details[1])
        
        # MS Consultancy logo (right)
        try:
            c.setFont("Helvetica", 6)
            c.drawString(160*mm, 282*mm, "in Jv with")
            
            if ms_logo_path and os.path.exists(ms_logo_path):
                try:
                    c.drawImage(ms_logo_path, 157*mm, 276*mm, width=25*mm, height=7*mm, preserveAspectRatio=True, mask='auto')
                except:
                    # Fallback to text
                    c.setFont("Helvetica-Bold", 7)
                    c.drawString(160*mm, 278*mm, "MS CONSULTANCY")
                    c.rect(157*mm, 275*mm, 25*mm, 10*mm)
            else:
                c.setFont("Helvetica-Bold", 7)
                c.drawString(160*mm, 278*mm, "MS CONSULTANCY")
                c.rect(157*mm, 275*mm, 25*mm, 10*mm)
                
        except Exception as e:
            # Fallback to text
            c.setFont("Helvetica-Bold", 7)
            c.drawString(160*mm, 278*mm, "MS CONSULTANCY")
            c.rect(157*mm, 275*mm, 25*mm, 10*mm)
        
        # Header border
        c.rect(12*mm, 274*mm, 170*mm, 12*mm)
    
    def _draw_title_section(self, c, data):
        """Draw compact title section"""
        c.rect(12*mm, 268*mm, 170*mm, 6*mm)
        
        # Divide into three columns
        c.line(70*mm, 268*mm, 70*mm, 274*mm)
        c.line(130*mm, 268*mm, 130*mm, 274*mm)
        
        c.setFont("Helvetica-Bold", 7)
        c.drawString(15*mm, 270.5*mm, "Title: Daily Diary")
        c.drawString(73*mm, 270.5*mm, "Document No:")
        c.drawString(133*mm, 270.5*mm, "Page No. of")
    
    def _draw_project_section(self, c, data):
        """Draw compact project section"""
        c.rect(12*mm, 256*mm, 170*mm, 12*mm)
        
        # Column dividers
        c.line(54.5*mm, 256*mm, 54.5*mm, 268*mm)
        c.line(97*mm, 256*mm, 97*mm, 268*mm)
        c.line(139.5*mm, 256*mm, 139.5*mm, 268*mm)
        
        # Row divider
        c.line(12*mm, 264*mm, 182*mm, 264*mm)
        
        # Headers
        c.setFont("Helvetica-Bold", 6)
        self._draw_centered_text(c, "PROJECT", 33.25*mm, 265.5*mm)
        self._draw_centered_text(c, "EMPLOYER", 75.75*mm, 265.5*mm)
        self._draw_centered_text(c, "CONSULTANT", 118.25*mm, 265.5*mm)
        self._draw_centered_text(c, "CONTRACTOR", 160.75*mm, 265.5*mm)
        
        # Data
        c.setFont("Helvetica", 5)
        self._draw_wrapped_text(c, self._safe_text(data.project), 13*mm, 261*mm, 40*mm, 1.5*mm)
        self._draw_wrapped_text(c, self._safe_text(data.employer), 55.5*mm, 261*mm, 40*mm, 1.5*mm)
        self._draw_wrapped_text(c, self._safe_text(data.consultant), 98*mm, 261*mm, 40*mm, 1.5*mm)
        self._draw_wrapped_text(c, self._safe_text(data.contractor), 140.5*mm, 261*mm, 40*mm, 1.5*mm)
    
    def _draw_date_time_section(self, c, data):
        """Draw compact date and time section"""
        c.rect(12*mm, 248*mm, 120*mm, 8*mm)
        c.rect(132*mm, 248*mm, 50*mm, 8*mm)
        
        c.setFont("Helvetica", 6)
        c.drawString(15*mm, 251*mm, f"1. Date: {self._safe_text(data.date)}")
        
        # Time section
        c.drawString(135*mm, 252*mm, "Time:")
        c.drawString(150*mm, 252*mm, "Morning")
        c.drawString(167*mm, 252*mm, "Afternoon")
        
        # Checkboxes
        c.rect(147*mm, 251*mm, 2*mm, 2*mm)
        c.rect(164*mm, 251*mm, 2*mm, 2*mm)
        
        if data.time_morning:
            c.setFont("Helvetica", 6)
            c.drawString(147.3*mm, 251.3*mm, "✓")
        if data.time_afternoon:
            c.setFont("Helvetica", 6)
            c.drawString(164.3*mm, 251.3*mm, "✓")
    
    def _draw_weather_section(self, c, data):
        """Draw compact weather section"""
        c.rect(12*mm, 242*mm, 170*mm, 6*mm)
        c.setFont("Helvetica", 6)
        weather_text = f"2. Weather condition: {self._safe_text(data.weather_condition) or '(Sunny/Dry, Rainy/Wet)'}"
        c.drawString(15*mm, 244.5*mm, weather_text)
    
    def _draw_activities_section(self, c, data):
        """Draw compact activities section with improved spacing"""
        c.rect(12*mm, 210*mm, 170*mm, 32*mm)
        c.setFont("Helvetica", 6)
        c.drawString(15*mm, 238*mm, "3. Major Activities on progress, Chain age and Location")
        
        # Table header
        c.line(12*mm, 235*mm, 182*mm, 235*mm)
        c.line(27*mm, 210*mm, 27*mm, 242*mm)
        
        c.setFont("Helvetica-Bold", 5)
        self._draw_centered_text(c, "sn", 19.5*mm, 236.5*mm)
        c.drawString(29*mm, 236.5*mm, "Description/Topic - Contractor's work")
        
        # Activity rows - 6 rows with optimized spacing
        row_height = 4*mm
        for i in range(6):
            y_pos = 232*mm - (i * row_height)
            if y_pos < 212*mm:  # Prevent overflow
                break
            c.line(12*mm, y_pos, 182*mm, y_pos)
            
            c.setFont("Helvetica", 5)
            self._draw_centered_text(c, str(i + 1), 19.5*mm, y_pos + 1.5*mm)
            
            if i < len(data.activities):
                activity = data.activities[i]
                desc = self._safe_text(activity.get('description', ''))
                if desc:
                    # Smart text wrapping for activities
                    self._draw_wrapped_text_in_cell(c, desc, 29*mm, y_pos + 1.5*mm, 150*mm, row_height - 0.5*mm)
    
    def _draw_equipment_section(self, c, data):
        """Draw compact equipment section"""
        c.rect(12*mm, 177*mm, 170*mm, 30*mm)
        c.setFont("Helvetica", 6)
        c.drawString(15*mm, 204*mm, "4. Contractor's Equipment (dumper truck, excavator, water pump etc.)")
        
        # Table headers
        c.line(12*mm, 201*mm, 182*mm, 201*mm)
        
        # Column lines - better positioned
        c.line(27*mm, 177*mm, 27*mm, 201*mm)
        c.line(67*mm, 177*mm, 67*mm, 201*mm)
        c.line(82*mm, 177*mm, 82*mm, 201*mm)
        c.line(97*mm, 177*mm, 97*mm, 201*mm)
        c.line(137*mm, 177*mm, 137*mm, 201*mm)
        c.line(152*mm, 177*mm, 152*mm, 201*mm)
        
        c.setFont("Helvetica-Bold", 5)
        self._draw_centered_text(c, "sn", 19.5*mm, 202.5*mm)
        self._draw_centered_text(c, "Equipment", 47*mm, 202.5*mm)
        self._draw_centered_text(c, "NO", 74.5*mm, 202.5*mm)
        self._draw_centered_text(c, "sn", 89.5*mm, 202.5*mm)
        self._draw_centered_text(c, "Equipment", 117*mm, 202.5*mm)
        self._draw_centered_text(c, "NO", 144.5*mm, 202.5*mm)
        
        # Equipment rows - 5 rows with better spacing
        for i in range(5):
            y_pos = 198*mm - (i * 4.2*mm)
            c.line(12*mm, y_pos, 182*mm, y_pos)
            
            c.setFont("Helvetica", 5)
            self._draw_centered_text(c, str(i + 1), 19.5*mm, y_pos + 1.2*mm)
            
            if i < len(data.equipment):
                eq = data.equipment[i]
                equipment_name = self._safe_text(eq.get('equipment', ''))
                equipment_no = self._safe_text(eq.get('no', ''))
                self._draw_text_in_cell(c, equipment_name, 29*mm, y_pos + 1.2*mm, 36*mm)
                self._draw_centered_text(c, equipment_no, 74.5*mm, y_pos + 1.2*mm)
            
            # Right side
            right_idx = i + 5
            self._draw_centered_text(c, str(right_idx + 1), 89.5*mm, y_pos + 1.2*mm)
            
            if right_idx < len(data.equipment):
                eq = data.equipment[right_idx]
                equipment_name = self._safe_text(eq.get('equipment', ''))
                equipment_no = self._safe_text(eq.get('no', ''))
                self._draw_text_in_cell(c, equipment_name, 99*mm, y_pos + 1.2*mm, 36*mm)
                self._draw_centered_text(c, equipment_no, 144.5*mm, y_pos + 1.2*mm)
    
    def _draw_personnel_section(self, c, data):
        """Draw compact personnel section with optimized layout"""
        c.rect(12*mm, 115*mm, 170*mm, 57*mm)
        c.setFont("Helvetica", 6)
        c.drawString(15*mm, 169*mm, "5. Contractor's Personnel (Foreman, laborer, driver etc.)")
        
        # Table headers
        c.line(12*mm, 166*mm, 182*mm, 166*mm)
        
        # Column dividers
        c.line(27*mm, 115*mm, 27*mm, 166*mm)
        c.line(67*mm, 115*mm, 67*mm, 166*mm)
        c.line(82*mm, 115*mm, 82*mm, 166*mm)
        c.line(97*mm, 115*mm, 97*mm, 166*mm)
        c.line(137*mm, 115*mm, 137*mm, 166*mm)
        c.line(152*mm, 115*mm, 152*mm, 166*mm)
        
        c.setFont("Helvetica-Bold", 5)
        self._draw_centered_text(c, "sn", 19.5*mm, 167.5*mm)
        self._draw_centered_text(c, "Personnel", 47*mm, 167.5*mm)
        self._draw_centered_text(c, "No.", 74.5*mm, 167.5*mm)
        self._draw_centered_text(c, "sn", 89.5*mm, 167.5*mm)
        self._draw_centered_text(c, "Personnel", 117*mm, 167.5*mm)
        self._draw_centered_text(c, "No.", 144.5*mm, 167.5*mm)
        
        # Personnel rows - optimized spacing
        row_height = 4.2*mm
        max_rows = min(12, int((166*mm - 120*mm) / row_height))
        
        for i in range(max_rows):
            y_pos = 163*mm - (i * row_height)
            if y_pos < 120*mm:
                break
            c.line(12*mm, y_pos, 182*mm, y_pos)
            
            c.setFont("Helvetica", 5)
            self._draw_centered_text(c, str(i + 1), 19.5*mm, y_pos + 1.5*mm)
            
            if i < len(data.personnel):
                person = data.personnel[i]
                personnel_name = self._safe_text(person.get('personnel', ''))
                personnel_no = self._safe_text(person.get('no', ''))
                self._draw_text_in_cell(c, personnel_name, 29*mm, y_pos + 1.5*mm, 36*mm)
                self._draw_centered_text(c, personnel_no, 74.5*mm, y_pos + 1.5*mm)
            
            # Right side
            right_idx = i + max_rows
            self._draw_centered_text(c, str(right_idx + 1), 89.5*mm, y_pos + 1.5*mm)
            
            if right_idx < len(data.personnel):
                person = data.personnel[right_idx]
                personnel_name = self._safe_text(person.get('personnel', ''))
                personnel_no = self._safe_text(person.get('no', ''))
                self._draw_text_in_cell(c, personnel_name, 99*mm, y_pos + 1.5*mm, 36*mm)
                self._draw_centered_text(c, personnel_no, 144.5*mm, y_pos + 1.5*mm)
    
    def _draw_unsafe_acts_section(self, c, data):
        """Draw compact unsafe acts section"""
        c.rect(12*mm, 100*mm, 170*mm, 12*mm)
        c.setFont("Helvetica", 6)
        c.drawString(15*mm, 109*mm, "6. Unsafe Acts / Conditions Observed")
        
        # Table headers
        c.line(12*mm, 106*mm, 182*mm, 106*mm)
        c.line(27*mm, 100*mm, 27*mm, 106*mm)
        
        c.setFont("Helvetica-Bold", 5)
        self._draw_centered_text(c, "sn", 19.5*mm, 107.5*mm)
        c.drawString(29*mm, 107.5*mm, "Description of Unsafe Acts")
        
        # Two rows for unsafe acts
        c.line(12*mm, 103*mm, 182*mm, 103*mm)
        
        c.setFont("Helvetica", 5)
        self._draw_centered_text(c, "1", 19.5*mm, 104.5*mm)
        self._draw_centered_text(c, "2", 19.5*mm, 101.5*mm)
        
        # Fill unsafe acts if available
        for i, unsafe_act in enumerate(data.unsafe_acts[:2]):
            y_pos = 104.5*mm - (i * 3*mm)
            desc = self._safe_text(unsafe_act.get('description', ''))
            if desc:
                self._draw_text_in_cell(c, desc, 29*mm, y_pos, 150*mm)
    
    def _draw_additional_sections(self, c, data):
        """Draw compact additional sections"""
        # Near Miss section
        c.rect(12*mm, 80*mm, 170*mm, 18*mm)
        c.setFont("Helvetica", 6)
        c.drawString(15*mm, 96*mm, "7. Near Miss/Accidents/Incidents:")
        c.setFont("Helvetica", 5)
        if data.near_miss:
            self._draw_wrapped_text(c, self._safe_text(data.near_miss), 15*mm, 92*mm, 165*mm, 1.5*mm)
        
        # Obstruction section
        c.rect(12*mm, 62*mm, 85*mm, 16*mm)
        c.setFont("Helvetica", 6)
        c.drawString(15*mm, 76*mm, "8. Obstruction/Action Plans:")
        c.setFont("Helvetica", 5)
        if data.obstruction:
            self._draw_wrapped_text(c, self._safe_text(data.obstruction), 15*mm, 72*mm, 80*mm, 1.5*mm)
        
        # Engineer's Note section
        c.rect(99*mm, 62*mm, 83*mm, 16*mm)
        c.setFont("Helvetica", 6)
        c.drawString(102*mm, 76*mm, "9. Engineer's Note:")
        c.setFont("Helvetica", 5)
        if data.engineers_note:
            self._draw_wrapped_text(c, self._safe_text(data.engineers_note), 102*mm, 72*mm, 78*mm, 1.5*mm)
    
    def _draw_signatures_section(self, c, data):
        """Draw compact signatures section"""
        y_start = 58*mm
        col_width = 56*mm
        box_height = 18*mm
        
        # Prepared by
        c.rect(12*mm, y_start - box_height, col_width, box_height)
        c.setFont("Helvetica-Bold", 6)
        c.drawString(15*mm, y_start - 3*mm, "Prepared by")
        c.setFont("Helvetica", 5)
        c.drawString(15*mm, y_start - 6*mm, "Construction Staff")
        c.drawString(15*mm, y_start - 10*mm, f"Name: {self._safe_text(data.prepared_by)}")
        c.drawString(15*mm, y_start - 15*mm, "Sign: _______________")
        
        # Checked by
        c.rect(70*mm, y_start - box_height, col_width, box_height)
        c.setFont("Helvetica-Bold", 6)
        c.drawString(73*mm, y_start - 3*mm, "Checked by")
        c.setFont("Helvetica", 5)
        c.drawString(73*mm, y_start - 6*mm, "Consultant Supervision Staff")
        c.drawString(73*mm, y_start - 10*mm, f"Name: {self._safe_text(data.checked_by)}")
        c.drawString(73*mm, y_start - 15*mm, "Sign: _______________")
        
        # Approved by
        c.rect(128*mm, y_start - box_height, col_width, box_height)
        c.setFont("Helvetica-Bold", 6)
        c.drawString(131*mm, y_start - 3*mm, "Approved by")
        c.setFont("Helvetica", 5)
        c.drawString(131*mm, y_start - 6*mm, "Consultant Supervision Staff")
        c.drawString(131*mm, y_start - 10*mm, f"Name: {self._safe_text(data.approved_by)}")
        c.drawString(131*mm, y_start - 15*mm, "Sign: _______________")
    
    def _draw_wrapped_text(self, c, text, x, y, max_width, line_height):
        """Draw text that wraps within a given width with improved spacing"""
        if not text:
            return
        
        words = str(text).split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if c.stringWidth(test_line, "Helvetica", 5) <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Handle very long words
                    lines.append(word[:50] + "..." if len(word) > 50 else word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw lines with proper spacing
        for i, line in enumerate(lines[:2]):  # Limit to 2 lines for better fit
            if line.strip():
                c.drawString(x, y - (i * line_height), line)
    
    def _draw_centered_text(self, c, text, x, y):
        """Draw text centered at the given position"""
        text_width = c.stringWidth(str(text), c._fontname, c._fontsize)
        c.drawString(x - text_width/2, y, str(text))
    
    def _safe_text(self, text):
        """Safely convert text to string, handling None values"""
        if text is None or text == "":
            return ""
        return str(text).strip()
    
    def _draw_text_in_cell(self, c, text, x, y, max_width):
        """Draw text within a cell with smart truncation and proper spacing"""
        safe_text = self._safe_text(text)
        if not safe_text:
            return
        
        # Clean up the text
        safe_text = ' '.join(safe_text.split())  # Remove extra spaces
        
        if c.stringWidth(safe_text, "Helvetica", 5) <= max_width:
            c.drawString(x, y, safe_text)
        else:
            # Smart truncation - try to keep meaningful words
            words = safe_text.split()
            truncated_words = []
            
            for word in words:
                test_text = ' '.join(truncated_words + [word])
                if c.stringWidth(test_text + "...", "Helvetica", 5) <= max_width:
                    truncated_words.append(word)
                else:
                    break
            
            if truncated_words:
                final_text = ' '.join(truncated_words) + "..."
            else:
                # If even one word is too long, truncate the first word
                first_word = words[0] if words else safe_text
                final_text = first_word
                while c.stringWidth(final_text + "...", "Helvetica", 5) > max_width and len(final_text) > 1:
                    final_text = final_text[:-1]
                final_text += "..."
            
            c.drawString(x, y, final_text)
    
    def _draw_wrapped_text_in_cell(self, c, text, x, y, max_width, max_height):
        """Draw text with smart wrapping within cell bounds"""
        safe_text = self._safe_text(text)
        if not safe_text:
            return
        
        words = safe_text.split()
        lines = []
        current_line = []
        line_height = 1.2*mm
        max_lines = int(max_height / line_height) if max_height > 0 else 2
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if c.stringWidth(test_line, "Helvetica", 5) <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Handle very long single words
                    truncated_word = word
                    while c.stringWidth(truncated_word + "...", "Helvetica", 5) > max_width and len(truncated_word) > 1:
                        truncated_word = truncated_word[:-1]
                    lines.append(truncated_word + "..." if len(truncated_word) < len(word) else word)
                
                if len(lines) >= max_lines:
                    break
        
        if current_line and len(lines) < max_lines:
            lines.append(' '.join(current_line))
        
        # Draw lines with proper spacing
        for i, line in enumerate(lines[:max_lines]):
            if line.strip():
                line_y = y - (i * line_height)
                if i == max_lines - 1 and len(lines) > max_lines:
                    # Add ellipsis to last line if text is truncated
                    if not line.endswith("..."):
                        line = line.rsplit(' ', 1)[0] + "..." if ' ' in line else line + "..."
                c.drawString(x, line_y, line)
