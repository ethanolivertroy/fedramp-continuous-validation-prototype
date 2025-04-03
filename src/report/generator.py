import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from ..models import ValidationResult


class ReportGenerator:
    """Generator for encryption validation reports."""
    
    def __init__(self, output_dir: Optional[str] = None):
        """Initialize the report generator.
        
        Args:
            output_dir: Directory to save reports to. Defaults to current directory.
        """
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.output_dir.mkdir(exist_ok=True, parents=True)
    
    def generate_json(self, result: ValidationResult, filename: Optional[str] = None) -> str:
        """Generate a JSON report.
        
        Args:
            result: The validation result.
            filename: Optional filename for the report.
            
        Returns:
            Path to the generated file.
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"encryption-validation-{timestamp}.json"
            
        filepath = self.output_dir / filename
        
        # Convert to dictionary and write to file
        with open(filepath, 'w') as f:
            json.dump(result.dict(), f, indent=2, default=str)
            
        return str(filepath)
    
    def generate_csv(self, result: ValidationResult, filename: Optional[str] = None) -> str:
        """Generate a CSV report.
        
        Args:
            result: The validation result.
            filename: Optional filename for the report.
            
        Returns:
            Path to the generated file.
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"encryption-validation-{timestamp}.csv"
            
        filepath = self.output_dir / filename
        
        # Write locations to CSV
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow([
                'ID', 'Name', 'Type', 'Provider', 'Region', 
                'Encryption Type', 'Compliant'
            ])
            
            # Write data rows
            for location in result.storage_locations:
                writer.writerow([
                    location.id,
                    location.name,
                    location.type,
                    location.provider,
                    location.region or '',
                    location.encryption_type,
                    location.compliant
                ])
                
        return str(filepath)
    
    def generate_summary(self, result: ValidationResult, filename: Optional[str] = None) -> str:
        """Generate a summary text report.
        
        Args:
            result: The validation result.
            filename: Optional filename for the report.
            
        Returns:
            Path to the generated file.
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"encryption-validation-summary-{timestamp}.txt"
            
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(f"FedRAMP Encryption Validation Summary\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            
            f.write(f"Overall Status: {'COMPLIANT' if result.all_encrypted else 'NON-COMPLIANT'}\n\n")
            
            f.write(f"Storage Locations: {len(result.storage_locations)}\n")
            object_storage_count = sum(1 for loc in result.storage_locations if loc.type == 'object_storage')
            database_count = sum(1 for loc in result.storage_locations if loc.type == 'database')
            f.write(f" - Object Storage: {object_storage_count}\n")
            f.write(f" - Databases: {database_count}\n\n")
            
            compliant_count = sum(1 for loc in result.storage_locations if loc.compliant)
            f.write(f"Compliant Locations: {compliant_count}/{len(result.storage_locations)}\n\n")
            
            if result.errors:
                f.write(f"Errors: {len(result.errors)}\n")
                for error in result.errors:
                    f.write(f" - {error['resource_id']}: {error['error_message']}\n")
            
        return str(filepath)