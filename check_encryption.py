#!/usr/bin/env python3
"""
FedRAMP Continuous Validation Tool - Encryption Check Script

This script can be run as a CLI tool or as an AWS Lambda function.
"""

import sys
import os
import json
import datetime
import boto3
from src.main import cli
from src.validators.aws_validator import AWSValidator
from src.report.generator import ReportGenerator


def lambda_handler(event, context):
    """
    AWS Lambda handler function.
    
    Args:
        event: AWS Lambda event
        context: AWS Lambda context
        
    Returns:
        Dict with validation results
    """
    # Get parameters from environment or event
    s3_buckets = event.get('s3_buckets', os.environ.get('S3_BUCKETS', ''))
    dynamodb_tables = event.get('dynamodb_tables', os.environ.get('DYNAMODB_TABLES', ''))
    rds_instances = event.get('rds_instances', os.environ.get('RDS_INSTANCES', ''))
    
    output_s3_bucket = event.get('output_s3_bucket', os.environ.get('OUTPUT_S3_BUCKET'))
    
    # Parse comma-separated lists
    s3_bucket_list = s3_buckets.split(',') if s3_buckets else []
    dynamodb_table_list = dynamodb_tables.split(',') if dynamodb_tables else []
    rds_instance_list = rds_instances.split(',') if rds_instances else []
    
    # Initialize validator
    validator = AWSValidator()
    
    # Track databases to validate with their type
    database_ids = []
    database_types = {}
    
    for table in dynamodb_table_list:
        database_ids.append(table)
        database_types[table] = 'dynamodb'
        
    for instance in rds_instance_list:
        database_ids.append(instance)
        database_types[instance] = 'rds'
    
    # Run validation
    result = validator.validate_all(
        object_storage_ids=s3_bucket_list,
        database_ids=database_ids,
        db_type=lambda db_id: database_types.get(db_id, 'dynamodb')
    )
    
    # Generate reports
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    
    # Create a temporary directory for reports
    import tempfile
    temp_dir = tempfile.mkdtemp()
    report_generator = ReportGenerator(output_dir=temp_dir)
    
    # Generate JSON report
    json_path = report_generator.generate_json(result, f"encryption-validation-{timestamp}.json")
    summary_path = report_generator.generate_summary(result, f"encryption-validation-summary-{timestamp}.txt")
    
    # Upload reports to S3 if bucket is specified
    if output_s3_bucket:
        s3_client = boto3.client('s3')
        
        with open(json_path, 'rb') as json_file:
            s3_client.upload_fileobj(
                json_file, 
                output_s3_bucket, 
                f"reports/encryption-validation-{timestamp}.json"
            )
            
        with open(summary_path, 'rb') as summary_file:
            s3_client.upload_fileobj(
                summary_file, 
                output_s3_bucket, 
                f"reports/encryption-validation-summary-{timestamp}.txt"
            )
    
    # Return result
    return {
        'statusCode': 200,
        'all_encrypted': result.all_encrypted,
        'compliant_count': sum(1 for loc in result.storage_locations if loc.compliant),
        'non_compliant_count': sum(1 for loc in result.storage_locations if not loc.compliant),
        'error_count': len(result.errors),
        'report_location': f"s3://{output_s3_bucket}/reports/encryption-validation-{timestamp}.json" if output_s3_bucket else json_path
    }


if __name__ == "__main__":
    sys.exit(cli())