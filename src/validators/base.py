from abc import ABC, abstractmethod
from typing import List, Optional

from ..models import ResourceType, StorageLocation, ValidationResult


class BaseValidator(ABC):
    """Base class for all validators."""
    
    def __init__(self, provider_name: str):
        """Initialize the validator.
        
        Args:
            provider_name: The name of the cloud provider.
        """
        self.provider_name = provider_name
        self.result = ValidationResult()
    
    @abstractmethod
    def validate_object_storage(self, location_id: str, **kwargs) -> StorageLocation:
        """Validate encryption for object storage.
        
        Args:
            location_id: Identifier for the storage location.
            **kwargs: Additional arguments needed for validation.
            
        Returns:
            StorageLocation: Details about the validated location.
        """
        pass
    
    @abstractmethod
    def validate_database(self, location_id: str, **kwargs) -> StorageLocation:
        """Validate encryption for database.
        
        Args:
            location_id: Identifier for the database.
            **kwargs: Additional arguments needed for validation.
            
        Returns:
            StorageLocation: Details about the validated location.
        """
        pass
    
    def validate_all(self, object_storage_ids: List[str], database_ids: List[str], **kwargs) -> ValidationResult:
        """Validate all resources.
        
        Args:
            object_storage_ids: List of object storage identifiers.
            database_ids: List of database identifiers.
            **kwargs: Additional arguments needed for validation.
            
        Returns:
            ValidationResult: The validation results.
        """
        # Validate object storage
        for storage_id in object_storage_ids:
            try:
                location = self.validate_object_storage(storage_id, **kwargs)
                self.result.add_location(location)
            except Exception as e:
                self.result.add_error(storage_id, str(e))
        
        # Validate databases
        for db_id in database_ids:
            try:
                location = self.validate_database(db_id, **kwargs)
                self.result.add_location(location)
            except Exception as e:
                self.result.add_error(db_id, str(e))
                
        return self.result