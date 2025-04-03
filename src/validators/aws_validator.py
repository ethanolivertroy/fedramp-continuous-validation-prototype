from typing import Dict, Optional, Any

from ..models import EncryptionType, ResourceType, StorageLocation
from ..providers.aws import AWSProvider
from .base import BaseValidator


class AWSValidator(BaseValidator):
    """AWS implementation of the validator."""
    
    def __init__(self, region_name: Optional[str] = None, profile: Optional[str] = None):
        """Initialize the AWS validator.
        
        Args:
            region_name: AWS region name.
            profile: AWS profile name.
        """
        super().__init__(provider_name="aws")
        self.aws = AWSProvider(region_name=region_name, profile=profile)
        self.region = region_name or self.aws.region
    
    def validate_object_storage(self, location_id: str, **kwargs) -> StorageLocation:
        """Validate encryption for an S3 bucket.
        
        Args:
            location_id: S3 bucket name.
            
        Returns:
            StorageLocation: Details about the validated bucket.
        """
        encryption_info = self.aws.get_s3_bucket_encryption(location_id)
        
        # Determine encryption type
        encryption_type = EncryptionType.NONE
        compliant = False
        
        if encryption_info.get('status') == 'encrypted':
            encryption_type_str = encryption_info.get('type')
            if encryption_type_str == 'server_side':
                encryption_type = EncryptionType.SERVER_SIDE
                compliant = True
            elif encryption_type_str == 'customer_managed_key':
                encryption_type = EncryptionType.CUSTOMER_MANAGED_KEY
                compliant = True
        
        return StorageLocation(
            id=location_id,
            name=location_id,
            type=ResourceType.OBJECT_STORAGE,
            provider=self.provider_name,
            region=self.region,
            encryption_type=encryption_type,
            encryption_details=encryption_info,
            compliant=compliant
        )
    
    def validate_database(self, location_id: str, **kwargs) -> StorageLocation:
        """Validate encryption for a database.
        
        Args:
            location_id: Database identifier.
            db_type: Type of database ('dynamodb' or 'rds')
            
        Returns:
            StorageLocation: Details about the validated database.
        """
        db_type = kwargs.get('db_type', 'dynamodb')
        
        if db_type == 'dynamodb':
            encryption_info = self.aws.get_dynamodb_encryption(location_id)
        elif db_type == 'rds':
            encryption_info = self.aws.get_rds_encryption(location_id)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
        
        # Determine encryption type
        encryption_type = EncryptionType.NONE
        compliant = False
        
        if encryption_info.get('status') == 'encrypted':
            encryption_type_str = encryption_info.get('type')
            if encryption_type_str == 'server_side':
                encryption_type = EncryptionType.SERVER_SIDE
                compliant = True
            elif encryption_type_str == 'customer_managed_key':
                encryption_type = EncryptionType.CUSTOMER_MANAGED_KEY
                compliant = True
        
        return StorageLocation(
            id=location_id,
            name=location_id,
            type=ResourceType.DATABASE,
            provider=self.provider_name,
            region=self.region,
            encryption_type=encryption_type,
            encryption_details=encryption_info,
            compliant=compliant
        )