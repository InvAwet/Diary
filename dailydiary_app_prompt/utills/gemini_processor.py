import google.generativeai as genai
from typing import Optional, Dict, List, Any
import json
import re
from datetime import datetime
from utils.data_models import DailyDiaryData

class GeminiProcessor:
    """Class for processing site reports using Gemini AI"""
    
    def __init__(self, api_key: str):
        """
        Initialize Gemini processor
        
        Args:
            api_key: Google Gemini API key
        """
        self.api_key = api_key
        self.setup_gemini()
    
    def setup_gemini(self):
        """Configure Gemini AI"""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            raise Exception(f"Failed to setup Gemini AI: {str(e)}")
    
    def extract_site_report_data(self, raw_text: str) -> Optional[DailyDiaryData]:
        """
        Extract structured data from site report text using Gemini AI
        
        Args:
            raw_text: Raw text extracted from site report
            
        Returns:
            DailyDiaryData: Structured data object
        """
        try:
            # Create a comprehensive prompt for data extraction
            prompt = self.create_extraction_prompt(raw_text)
            
            # Generate response from Gemini
            response = self.model.generate_content(prompt)
            
            if not response.text:
                raise Exception("No response received from Gemini AI")
            
            # Parse the response
            structured_data = self.parse_gemini_response(response.text)
            
            if structured_data:
                return self.convert_to_daily_diary_data(structured_data)
            else:
                return None
                
        except Exception as e:
            raise Exception(f"Error processing with Gemini AI: {str(e)}")
    
    def create_extraction_prompt(self, raw_text: str) -> str:
        """
        Create a detailed prompt for Gemini AI to extract site report data
        
        Args:
            raw_text: Raw text from site report
            
        Returns:
            str: Formatted prompt
        """
        
        prompt = f"""
You are an expert construction site report analyzer with enhanced accuracy capabilities. Extract structured information from the following daily site report text and format it as JSON.

CRITICAL ACCURACY REQUIREMENTS:
- This is a REAL construction site report requiring MAXIMUM precision
- Extract ALL actual data present with 100% accuracy
- Maintain original formatting, numbers, and codes exactly as written
- Do NOT invent or assume any data not explicitly present

**PRECISION EXTRACTION RULES:**
1. DATE EXTRACTION: Find exact date in any format (DD-MM-YYYY, DD/MM/YYYY, etc.)
2. EQUIPMENT PRECISION: Extract exact IDs/codes (EX-2806, BL-1463, LD-1458, Dozer-1359)
3. ACTIVITY DETAILS: Capture complete descriptions with locations and measurements
4. PERSONNEL ACCURACY: Extract exact job titles and quantities as stated
5. MATERIAL PRECISION: Find exact quantities with correct units (m³, m, kg, nos)
6. LOCATION ACCURACY: Extract station ranges and coordinates precisely
7. MANHOLE REFERENCES: Identify exact codes (M42C02, M42C04, etc.)
8. WEATHER CONDITIONS: Extract exact weather descriptions
9. SAFETY OBSERVATIONS: Capture all safety-related information
10. SIGNATURES/NAMES: Extract exact names and roles as written

**PRECISION TARGET EXTRACTION:**

PROJECT INFORMATION:
- Project name: Look for project title or name
- Date: Extract from "Date:" field or date patterns
- Location: Find "Location:", "Site Location:", or geographical references
- Station From/To: Extract exact chainages and coordinates
- MHo From/To: Find manhole references and numbers
- Prepared By: Look for "Prepared By:", signature fields, or responsible person
- Employer/Client: Find client or employer name
- Consultant: Look for consulting company or supervisor
- Contractor: Find contractor or construction company name

DETAILED ACTIVITIES:
- Exact activity descriptions (Trench Excavation, Pipe Laying, Concrete Pouring, etc.)
- Precise locations and station references
- Accurate quantities with proper units (m³, m, nos, kg, etc.)
- Work dimensions (Length × Width × Depth)
- Completion percentages if mentioned

COMPREHENSIVE EQUIPMENT LIST:
- All equipment IDs and codes (EX-2806, BL-1463, LD-1458, Dozer-1359, etc.)
- Equipment types (Excavator, Loader, Dozer, Truck, Pump, etc.)
- Operating hours from OH columns
- Idle hours if specified
- Equipment status and condition

COMPLETE PERSONNEL ROSTER:
- All job titles (Construction Engineer, Site Engineer, Foreman, Plumber, Daily Labor, etc.)
- Exact number of people for each role
- Working hours per person or role
- Supervisor and management staff

MATERIALS (find all materials):
- Material types (Local material, Redash, GRP pipe, Concrete, etc.)
- Quantities with units
- Locations where used

Please analyze this REAL site report and extract the actual data:

{raw_text}

Return the extracted information in the following JSON format:
{{
    "project": "project name",
    "employer": "employer name",
    "consultant": "consultant name",
    "contractor": "contractor name",
    "date": "DD-MM-YYYY",
    "location": "site location",
    "time_morning": true/false,
    "time_afternoon": true/false,
    "weather_condition": "weather description",
    "activities": [
        {{"sn": 1, "description": "activity description", "location": "location", "quantity": "quantity", "unit": "unit"}},
        ...
    ],
    "equipment": [
        {{"sn": 1, "equipment": "equipment name/id", "no": "quantity", "operating_hours": "hours", "idle_hours": "hours", "status": "status", "remarks": "remarks"}},
        ...
    ],
    "personnel": [
        {{"sn": 1, "personnel": "role/title", "no": "number of people", "hours": "working hours"}},
        ...
    ],
    "materials": [
        {{"type": "material type", "unit": "unit", "quantity": "quantity", "location": "location"}},
        ...
    ],
    "unsafe_acts": [
        {{"sn": 1, "description": "unsafe act description", "severity": "severity level", "action_taken": "action taken"}},
        ...
    ],
    "near_miss": "near miss description",
    "obstruction": "obstruction description",
    "engineers_note": "engineer's note",
    "prepared_by": "prepared by name",
    "checked_by": "checked by name",
    "approved_by": "approved by name"
}}

Extract all available information. If some fields are not found in the text, leave them empty or use reasonable defaults.
Focus on accuracy and completeness of the extraction.
"""
        
        return prompt
    
    def parse_gemini_response(self, response_text: str) -> Optional[Dict]:
        """
        Parse Gemini AI response and extract structured data
        
        Args:
            response_text: Raw response from Gemini AI
            
        Returns:
            Dict: Parsed structured data or None if parsing failed
        """
        try:
            # Try to find JSON content in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(0)
                # Clean up the JSON string
                json_str = json_str.strip()
                
                try:
                    # Parse JSON
                    data = json.loads(json_str)
                    return data
                except json.JSONDecodeError:
                    # Try to fix common JSON issues
                    cleaned_json = re.sub(r',(\s*[}\]])', r'\1', json_str)
                    data = json.loads(cleaned_json)
                    return data
            else:
                # If no JSON found, try to extract key-value pairs manually
                return self.extract_key_value_from_text(response_text)
        except Exception as e:
            raise Exception(f"Error parsing Gemini response: {str(e)}")
    
    def extract_key_value_from_text(self, text: str) -> Dict:
        """
        Extract key-value pairs from text when JSON parsing fails
        
        Args:
            text: Text to parse
            
        Returns:
            Dict: Extracted key-value pairs
        """
        data = {
            'project': '',
            'employer': '',
            'consultant': '',
            'contractor': '',
            'date': '',
            'location': '',
            'time_morning': False,
            'time_afternoon': False,
            'weather_condition': 'Sunny/Dry',
            'activities': [],
            'equipment': [],
            'personnel': [],
            'materials': [],
            'unsafe_acts': [],
            'near_miss': '',
            'obstruction': '',
            'engineers_note': '',
            'prepared_by': '',
            'checked_by': '',
            'approved_by': ''
        }
        
        # Extract basic information using regex patterns
        patterns = {
            'project': r'(?:project|title)[:\s]*([^\n]+)',
            'employer': r'employer[:\s]*([^\n]+)',
            'consultant': r'consultant[:\s]*([^\n]+)',
            'contractor': r'contractor[:\s]*([^\n]+)',
            'date': r'date[:\s]*([^\n]+)',
            'location': r'(?:location|site)[:\s]*([^\n]+)',
            'prepared_by': r'prepared by[:\s]*([^\n]+)',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text.lower())
            if match:
                data[key] = match.group(1).strip()
        
        return data
    
    def convert_to_daily_diary_data(self, structured_data: Dict) -> DailyDiaryData:
        """
        Convert structured data dictionary to DailyDiaryData object with enhanced validation
        
        Args:
            structured_data: Dictionary with extracted data
            
        Returns:
            DailyDiaryData: Structured data object
        """
        try:
            # Create DailyDiaryData object
            diary_data = DailyDiaryData()
            
            # Basic information with cleaning
            diary_data.project = self._clean_text(structured_data.get('project', ''))
            diary_data.employer = self._clean_text(structured_data.get('employer', ''))
            diary_data.consultant = self._clean_text(structured_data.get('consultant', ''))
            diary_data.contractor = self._clean_text(structured_data.get('contractor', ''))
            diary_data.date = self._validate_date(structured_data.get('date', ''))
            diary_data.location = self._clean_text(structured_data.get('location', ''))
            diary_data.weather_condition = self._clean_text(structured_data.get('weather_condition', 'Sunny/Dry'))
            
            # Time periods
            diary_data.time_morning = structured_data.get('time_morning', False)
            diary_data.time_afternoon = structured_data.get('time_afternoon', False)
            
            # If neither time period is set, default to morning
            if not diary_data.time_morning and not diary_data.time_afternoon:
                diary_data.time_morning = True
            
            # Activities
            activities = structured_data.get('activities', [])
            if isinstance(activities, list):
                diary_data.activities = activities
            
            # Equipment
            equipment = structured_data.get('equipment', [])
            if isinstance(equipment, list):
                diary_data.equipment = equipment
            
            # Personnel
            personnel = structured_data.get('personnel', [])
            if isinstance(personnel, list):
                diary_data.personnel = personnel
            
            # Materials
            materials = structured_data.get('materials', [])
            if isinstance(materials, list):
                diary_data.materials = materials
            
            # Safety information
            unsafe_acts = structured_data.get('unsafe_acts', [])
            if isinstance(unsafe_acts, list):
                diary_data.unsafe_acts = unsafe_acts
            
            diary_data.near_miss = structured_data.get('near_miss', '')
            diary_data.obstruction = structured_data.get('obstruction', '')
            diary_data.engineers_note = structured_data.get('engineers_note', '')
            
            # Signatures
            diary_data.prepared_by = structured_data.get('prepared_by', '')
            diary_data.checked_by = structured_data.get('checked_by', '')
            diary_data.approved_by = structured_data.get('approved_by', '')
            
            return diary_data
            
        except Exception as e:
            raise Exception(f"Error converting to DailyDiaryData: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text data"""
        if not text or text is None:
            return ""
        
        # Convert to string and clean
        clean_text = str(text).strip()
        
        # Remove multiple spaces
        clean_text = ' '.join(clean_text.split())
        
        # Remove special characters that might cause issues
        clean_text = clean_text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        
        return clean_text
    
    def _validate_date(self, date_str: str) -> str:
        """Validate and format date string"""
        if not date_str:
            return ""
        
        clean_date = self._clean_text(date_str)
        
        # Try to parse various date formats
        date_patterns = [
            r'(\d{1,2})-(\d{1,2})-(\d{4})',
            r'(\d{1,2})/(\d{1,2})/(\d{4})',
            r'(\d{1,2})\.(\d{1,2})\.(\d{4})',
            r'(\d{1,2})\s+(\d{1,2})\s+(\d{4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, clean_date)
            if match:
                day, month, year = match.groups()
                return f"{day.zfill(2)}-{month.zfill(2)}-{year}"
        
        return clean_date
    
    def _validate_and_clean_list(self, data_list: List[Dict], required_fields: List[str]) -> List[Dict]:
        """Validate and clean list data"""
        if not isinstance(data_list, list):
            return []
        
        cleaned_list = []
        for item in data_list:
            if isinstance(item, dict):
                cleaned_item = {}
                for field in required_fields:
                    cleaned_item[field] = self._clean_text(item.get(field, ''))
                
                # Only add non-empty items
                if any(cleaned_item.values()):
                    cleaned_list.append(cleaned_item)
        
        return cleaned_list
