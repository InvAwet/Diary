from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime

@dataclass
class ActivityData:
    """Data class for activity information"""
    sn: int
    description: str
    location: Optional[str] = None
    quantity: Optional[str] = None
    unit: Optional[str] = None

@dataclass
class EquipmentData:
    """Data class for equipment information"""
    sn: int
    equipment: str
    no: str
    operating_hours: Optional[str] = None
    idle_hours: Optional[str] = None
    status: Optional[str] = None
    remarks: Optional[str] = None

@dataclass
class PersonnelData:
    """Data class for personnel information"""
    sn: int
    personnel: str
    no: str
    hours: Optional[str] = None
    role: Optional[str] = None

@dataclass
class MaterialData:
    """Data class for material information"""
    type: str
    unit: str
    quantity: str
    location: Optional[str] = None

@dataclass
class UnsafeActData:
    """Data class for unsafe acts/conditions"""
    sn: int
    description: str
    severity: Optional[str] = None
    action_taken: Optional[str] = None

@dataclass
class DailyDiaryData:
    """Main data class for Daily Diary information"""
    # Project information
    project: str = ""
    employer: str = ""
    consultant: str = ""
    contractor: str = ""
    
    # Date and time information
    date: str = ""  # Format: DD-MM-YYYY
    time_morning: bool = False
    time_afternoon: bool = False
    
    # Location and weather
    location: str = ""
    weather_condition: str = "Sunny/Dry"
    
    # Work information
    activities: List[Dict[str, Any]] = field(default_factory=list)
    equipment: List[Dict[str, Any]] = field(default_factory=list)
    personnel: List[Dict[str, Any]] = field(default_factory=list)
    materials: List[Dict[str, Any]] = field(default_factory=list)
    
    # Safety and issues
    unsafe_acts: List[Dict[str, Any]] = field(default_factory=list)
    near_miss: str = ""
    obstruction: str = ""
    engineers_note: str = ""
    
    # Signatures
    prepared_by: str = ""
    checked_by: str = ""
    approved_by: str = ""
    
    # Additional metadata
    document_number: str = ""
    page_number: str = ""
    revision: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert data class to dictionary"""
        return {
            'project': self.project,
            'employer': self.employer,
            'consultant': self.consultant,
            'contractor': self.contractor,
            'date': self.date,
            'time_morning': self.time_morning,
            'time_afternoon': self.time_afternoon,
            'location': self.location,
            'weather_condition': self.weather_condition,
            'activities': self.activities,
            'equipment': self.equipment,
            'personnel': self.personnel,
            'materials': self.materials,
            'unsafe_acts': self.unsafe_acts,
            'near_miss': self.near_miss,
            'obstruction': self.obstruction,
            'engineers_note': self.engineers_note,
            'prepared_by': self.prepared_by,
            'checked_by': self.checked_by,
            'approved_by': self.approved_by,
            'document_number': self.document_number,
            'page_number': self.page_number,
            'revision': self.revision
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DailyDiaryData':
        """Create data class from dictionary"""
        return cls(
            project=data.get('project', ''),
            employer=data.get('employer', ''),
            consultant=data.get('consultant', ''),
            contractor=data.get('contractor', ''),
            date=data.get('date', ''),
            time_morning=data.get('time_morning', False),
            time_afternoon=data.get('time_afternoon', False),
            location=data.get('location', ''),
            weather_condition=data.get('weather_condition', 'Sunny/Dry'),
            activities=data.get('activities', []),
            equipment=data.get('equipment', []),
            personnel=data.get('personnel', []),
            materials=data.get('materials', []),
            unsafe_acts=data.get('unsafe_acts', []),
            near_miss=data.get('near_miss', ''),
            obstruction=data.get('obstruction', ''),
            engineers_note=data.get('engineers_note', ''),
            prepared_by=data.get('prepared_by', ''),
            checked_by=data.get('checked_by', ''),
            approved_by=data.get('approved_by', ''),
            document_number=data.get('document_number', ''),
            page_number=data.get('page_number', ''),
            revision=data.get('revision', '')
        )
    
    def validate(self) -> List[str]:
        """Validate the data and return list of validation errors"""
        errors = []
        
        # Required fields validation
        if not self.project.strip():
            errors.append("Project name is required")
        
        if not self.date.strip():
            errors.append("Date is required")
        
        if not self.contractor.strip():
            errors.append("Contractor name is required")
        
        # Date format validation
        if self.date:
            try:
                datetime.strptime(self.date, '%d-%m-%Y')
            except ValueError:
                errors.append(f"Date must be in DD-MM-YYYY format, got: {self.date}")
        
        # Time period validation
        if not self.time_morning and not self.time_afternoon:
            errors.append("At least one time period (Morning/Afternoon) must be selected")
        
        # Activities validation
        if not self.activities or not any(act.get('description', '').strip() for act in self.activities):
            errors.append("At least one activity is required")
        
        # Equipment validation - ensure proper structure
        for i, eq in enumerate(self.equipment):
            if not isinstance(eq, dict):
                errors.append(f"Equipment item {i+1} must be a dictionary")
            elif eq.get('equipment', '').strip() and not eq.get('no', '').strip():
                errors.append(f"Equipment item {i+1} is missing quantity/number")
        
        # Personnel validation - ensure proper structure
        for i, person in enumerate(self.personnel):
            if not isinstance(person, dict):
                errors.append(f"Personnel item {i+1} must be a dictionary")
            elif person.get('personnel', '').strip() and not person.get('no', '').strip():
                errors.append(f"Personnel item {i+1} is missing number")
        
        return errors
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the data"""
        return {
            'project': self.project,
            'date': self.date,
            'location': self.location,
            'activities_count': len([a for a in self.activities if a.get('description', '').strip()]),
            'equipment_count': len([e for e in self.equipment if e.get('equipment', '').strip()]),
            'personnel_count': len([p for p in self.personnel if p.get('personnel', '').strip()]),
            'unsafe_acts_count': len([u for u in self.unsafe_acts if u.get('description', '').strip()]),
            'has_near_miss': bool(self.near_miss.strip()),
            'has_obstruction': bool(self.obstruction.strip()),
            'has_engineers_note': bool(self.engineers_note.strip()),
            'time_periods': {
                'morning': self.time_morning,
                'afternoon': self.time_afternoon
            },
            'signatures_complete': all([
                self.prepared_by.strip(),
                self.checked_by.strip(),
                self.approved_by.strip()
            ])
        }

@dataclass 
class SiteReportData:
    """Data class for raw site report information"""
    # Basic information
    date: str = ""
    location: str = ""
    station_from: str = ""
    station_to: str = ""
    mho_from: str = ""
    mho_to: str = ""
    site_location: str = ""
    prepared_by: str = ""
    
    # Extracted activities
    activities: List[Dict[str, Any]] = field(default_factory=list)
    
    # Equipment information
    equipment_used: List[Dict[str, Any]] = field(default_factory=list)
    
    # Personnel information
    personnel: List[Dict[str, Any]] = field(default_factory=list)
    
    # Materials used
    materials: List[Dict[str, Any]] = field(default_factory=list)
    
    # Raw extracted text
    raw_text: str = ""
    
    # Processing metadata
    processed_date: str = ""
    source_file: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'date': self.date,
            'location': self.location,
            'station_from': self.station_from,
            'station_to': self.station_to,
            'mho_from': self.mho_from,
            'mho_to': self.mho_to,
            'site_location': self.site_location,
            'prepared_by': self.prepared_by,
            'activities': self.activities,
            'equipment_used': self.equipment_used,
            'personnel': self.personnel,
            'materials': self.materials,
            'raw_text': self.raw_text,
            'processed_date': self.processed_date,
            'source_file': self.source_file
        }
