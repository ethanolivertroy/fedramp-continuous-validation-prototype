from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class EncryptionType(str, Enum):
    """Enumeration of possible encryption types."""
    NONE = "none"
    SERVER_SIDE = "server_side"
    CLIENT_SIDE = "client_side"
    CUSTOMER_MANAGED_KEY = "customer_managed_key"
    UNKNOWN = "unknown"


class ResourceType(str, Enum):
    """Enumeration of resource types to validate."""
    OBJECT_STORAGE = "object_storage"
    DATABASE = "database"


class StorageLocation(BaseModel):
    """Model representing a storage location."""
    id: str
    name: str
    type: ResourceType
    provider: str
    region: Optional[str] = None
    encryption_type: EncryptionType = EncryptionType.UNKNOWN
    encryption_details: Optional[Dict] = None
    compliant: bool = False


class ValidationResult(BaseModel):
    """Model representing the overall validation result."""
    all_encrypted: bool = False
    storage_locations: List[StorageLocation] = Field(default_factory=list)
    errors: List[Dict] = Field(default_factory=list)
    
    def add_location(self, location: StorageLocation) -> None:
        """Add a storage location to the results."""
        self.storage_locations.append(location)
        self._recalculate_encryption_status()
    
    def add_error(self, resource_id: str, error_message: str) -> None:
        """Add an error to the results."""
        self.errors.append({
            "resource_id": resource_id,
            "error_message": error_message
        })
        self._recalculate_encryption_status()
    
    def _recalculate_encryption_status(self) -> None:
        """Recalculate the overall encryption status."""
        if not self.storage_locations:
            self.all_encrypted = False
            return
            
        self.all_encrypted = all(
            location.compliant for location in self.storage_locations
        ) and not self.errors