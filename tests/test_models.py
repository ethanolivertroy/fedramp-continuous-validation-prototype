import unittest
from src.models import ValidationResult, StorageLocation, ResourceType, EncryptionType


class TestModels(unittest.TestCase):
    """Test cases for model classes."""
    
    def test_validation_result_calculation(self):
        """Test that the encryption status is correctly calculated."""
        # Create a validation result
        result = ValidationResult()
        
        # Initially should be false
        self.assertFalse(result.all_encrypted)
        
        # Add compliant location
        location1 = StorageLocation(
            id="test-bucket-1",
            name="test-bucket-1",
            type=ResourceType.OBJECT_STORAGE,
            provider="aws",
            region="us-east-1",
            encryption_type=EncryptionType.SERVER_SIDE,
            compliant=True
        )
        result.add_location(location1)
        
        # With one compliant location, should be true
        self.assertTrue(result.all_encrypted)
        
        # Add non-compliant location
        location2 = StorageLocation(
            id="test-bucket-2",
            name="test-bucket-2",
            type=ResourceType.OBJECT_STORAGE,
            provider="aws",
            region="us-east-1",
            encryption_type=EncryptionType.NONE,
            compliant=False
        )
        result.add_location(location2)
        
        # With one non-compliant location, should be false
        self.assertFalse(result.all_encrypted)
        
        # Add error
        result.add_error("test-bucket-3", "Could not access bucket")
        
        # With error, should still be false
        self.assertFalse(result.all_encrypted)
        
        # Remove non-compliant location and error
        result.storage_locations = [location1]
        result.errors = []
        result._recalculate_encryption_status()
        
        # Should be true again
        self.assertTrue(result.all_encrypted)


if __name__ == "__main__":
    unittest.main()