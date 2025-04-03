import unittest
from unittest.mock import MagicMock, patch

from src.validators.aws_validator import AWSValidator
from src.models import EncryptionType, ResourceType, StorageLocation


class TestAWSValidator(unittest.TestCase):
    """Test cases for AWS validator."""
    
    @patch('src.providers.aws.AWSProvider')
    def test_validate_s3_encryption_server_side(self, mock_provider):
        """Test validation of S3 bucket with server-side encryption."""
        # Setup mock
        mock_aws = MagicMock()
        mock_aws.get_s3_bucket_encryption.return_value = {
            'status': 'encrypted',
            'type': 'server_side',
            'algorithm': 'AES256'
        }
        mock_provider.return_value = mock_aws
        mock_aws.region = 'us-east-1'
        
        # Create validator
        validator = AWSValidator(region_name='us-east-1')
        
        # Run validation
        result = validator.validate_object_storage('test-bucket')
        
        # Verify results
        self.assertEqual(result.id, 'test-bucket')
        self.assertEqual(result.type, ResourceType.OBJECT_STORAGE)
        self.assertEqual(result.encryption_type, EncryptionType.SERVER_SIDE)
        self.assertTrue(result.compliant)
        
        # Verify mock was called correctly
        mock_aws.get_s3_bucket_encryption.assert_called_once_with('test-bucket')
    
    @patch('src.providers.aws.AWSProvider')
    def test_validate_s3_encryption_none(self, mock_provider):
        """Test validation of S3 bucket with no encryption."""
        # Setup mock
        mock_aws = MagicMock()
        mock_aws.get_s3_bucket_encryption.return_value = {
            'status': 'unencrypted'
        }
        mock_provider.return_value = mock_aws
        mock_aws.region = 'us-east-1'
        
        # Create validator
        validator = AWSValidator(region_name='us-east-1')
        
        # Run validation
        result = validator.validate_object_storage('test-bucket')
        
        # Verify results
        self.assertEqual(result.id, 'test-bucket')
        self.assertEqual(result.type, ResourceType.OBJECT_STORAGE)
        self.assertEqual(result.encryption_type, EncryptionType.NONE)
        self.assertFalse(result.compliant)
        
        # Verify mock was called correctly
        mock_aws.get_s3_bucket_encryption.assert_called_once_with('test-bucket')
    
    @patch('src.providers.aws.AWSProvider')
    def test_validate_dynamodb_encryption(self, mock_provider):
        """Test validation of DynamoDB table with encryption."""
        # Setup mock
        mock_aws = MagicMock()
        mock_aws.get_dynamodb_encryption.return_value = {
            'status': 'encrypted',
            'type': 'customer_managed_key',
            'key_id': 'arn:aws:kms:us-east-1:123456789012:key/abcd1234'
        }
        mock_provider.return_value = mock_aws
        mock_aws.region = 'us-east-1'
        
        # Create validator
        validator = AWSValidator(region_name='us-east-1')
        
        # Run validation
        result = validator.validate_database('test-table', db_type='dynamodb')
        
        # Verify results
        self.assertEqual(result.id, 'test-table')
        self.assertEqual(result.type, ResourceType.DATABASE)
        self.assertEqual(result.encryption_type, EncryptionType.CUSTOMER_MANAGED_KEY)
        self.assertTrue(result.compliant)
        
        # Verify mock was called correctly
        mock_aws.get_dynamodb_encryption.assert_called_once_with('test-table')


if __name__ == "__main__":
    unittest.main()