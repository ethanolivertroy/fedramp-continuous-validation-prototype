import boto3
from typing import Dict, Optional, Any

from botocore.exceptions import ClientError

class AWSProvider:
    """AWS Cloud Provider implementation."""
    
    def __init__(self, region_name: Optional[str] = None, profile: Optional[str] = None):
        """Initialize AWS provider.
        
        Args:
            region_name: AWS region name.
            profile: AWS profile name.
        """
        self.session = boto3.Session(region_name=region_name, profile_name=profile)
        self.region = region_name or self.session.region_name
    
    def get_s3_bucket_encryption(self, bucket_name: str) -> Dict[str, Any]:
        """Get encryption configuration for an S3 bucket.
        
        Args:
            bucket_name: Name of the S3 bucket.
            
        Returns:
            Dict containing encryption details or None if unencrypted.
        """
        s3_client = self.session.client('s3')
        try:
            response = s3_client.get_bucket_encryption(Bucket=bucket_name)
            rules = response.get('ServerSideEncryptionConfiguration', {}).get('Rules', [])
            
            if not rules:
                return {'status': 'unencrypted'}
                
            rule = rules[0]
            sse_algorithm = rule.get('ApplyServerSideEncryptionByDefault', {}).get('SSEAlgorithm')
            kms_key_id = rule.get('ApplyServerSideEncryptionByDefault', {}).get('KMSMasterKeyID')
            
            if sse_algorithm == 'AES256':
                return {
                    'status': 'encrypted',
                    'type': 'server_side',
                    'algorithm': 'AES256'
                }
            elif sse_algorithm == 'aws:kms':
                key_type = 'aws_managed' if not kms_key_id else 'customer_managed'
                return {
                    'status': 'encrypted',
                    'type': 'customer_managed_key' if key_type == 'customer_managed' else 'server_side',
                    'algorithm': 'aws:kms',
                    'key_id': kms_key_id,
                    'key_type': key_type
                }
            else:
                return {'status': 'unknown', 'algorithm': sse_algorithm}
                
        except ClientError as e:
            if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                return {'status': 'unencrypted'}
            raise
    
    def get_dynamodb_encryption(self, table_name: str) -> Dict[str, Any]:
        """Get encryption configuration for a DynamoDB table.
        
        Args:
            table_name: Name of the DynamoDB table.
            
        Returns:
            Dict containing encryption details.
        """
        dynamodb_client = self.session.client('dynamodb')
        try:
            response = dynamodb_client.describe_table(TableName=table_name)
            table_info = response.get('Table', {})
            
            # DynamoDB tables are always encrypted at rest, but we check for
            # customer managed key (CMK) vs AWS owned key
            sse_desc = table_info.get('SSEDescription', {})
            status = sse_desc.get('Status')
            sse_type = sse_desc.get('SSEType')
            kms_key_id = sse_desc.get('KMSMasterKeyArn')
            
            if status == 'ENABLED':
                if sse_type == 'KMS' and kms_key_id:
                    return {
                        'status': 'encrypted',
                        'type': 'customer_managed_key',
                        'key_id': kms_key_id
                    }
                else:
                    return {
                        'status': 'encrypted',
                        'type': 'server_side'
                    }
            else:
                # All DynamoDB tables are encrypted with AWS owned keys by default
                return {
                    'status': 'encrypted',
                    'type': 'server_side',
                    'note': 'Default AWS owned key encryption'
                }
                
        except ClientError:
            raise
    
    def get_rds_encryption(self, db_identifier: str) -> Dict[str, Any]:
        """Get encryption configuration for an RDS database.
        
        Args:
            db_identifier: RDS database identifier.
            
        Returns:
            Dict containing encryption details.
        """
        rds_client = self.session.client('rds')
        try:
            response = rds_client.describe_db_instances(DBInstanceIdentifier=db_identifier)
            instances = response.get('DBInstances', [])
            
            if not instances:
                raise ValueError(f"DB instance {db_identifier} not found")
                
            instance = instances[0]
            storage_encrypted = instance.get('StorageEncrypted', False)
            kms_key_id = instance.get('KmsKeyId')
            
            if storage_encrypted:
                if kms_key_id:
                    return {
                        'status': 'encrypted',
                        'type': 'customer_managed_key',
                        'key_id': kms_key_id
                    }
                else:
                    return {
                        'status': 'encrypted',
                        'type': 'server_side'
                    }
            else:
                return {'status': 'unencrypted'}
                
        except ClientError:
            raise