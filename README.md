# FedRAMP Continuous Validation Prototype

A prototype tool to validate FedRAMP compliance requirements, specifically focused on data encryption.

## Problem Statement

This prototype addresses the following scenario:

> I have a simple application deployed on cloud native services on a major IaaS offering. My information storage includes:
> - A few hundred files stored in a single object storage location.
> - Tens of thousands of database records stored in a cloud native database.
> 
> How can I prove programmatically that all information in the above locations is encrypted?

## Features

- Validates encryption for multiple cloud storage types:
  - Object Storage (AWS S3)
  - Databases (AWS DynamoDB, RDS)
- Checks for different encryption types:
  - Server-side encryption
  - Customer managed keys
- Generates machine-readable reports in multiple formats:
  - JSON
  - CSV
  - Text summary

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/fedramp-continuous-validation-prototype.git
cd fedramp-continuous-validation-prototype

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### AWS Example

```bash
# Set up AWS credentials
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=us-east-1

# Or use a profile
python -m src.main validate --provider aws --profile your-profile-name --s3-buckets bucket1,bucket2 --dynamodb-tables table1,table2
```

### CLI Options

```
Usage: python -m src.main validate [OPTIONS]

  Validate encryption for cloud resources.

Options:
  --provider [aws|azure|gcp]     Cloud provider to validate.
  --region TEXT                  Cloud provider region.
  --profile TEXT                 Cloud provider profile (e.g. AWS profile).
  --s3-buckets TEXT              Comma-separated list of S3 bucket names to
                                 validate.
  --dynamodb-tables TEXT         Comma-separated list of DynamoDB table names
                                 to validate.
  --rds-instances TEXT           Comma-separated list of RDS instance
                                 identifiers to validate.
  --output-dir TEXT              Directory to write reports to.
  --format [json|csv|all]        Output format for the report.
  --help                         Show this message and exit.
```

## Report Format

The JSON report structure follows this format:

```json
{
  "all_encrypted": true,
  "storage_locations": [
    {
      "id": "my-s3-bucket",
      "name": "my-s3-bucket",
      "type": "object_storage",
      "provider": "aws",
      "region": "us-east-1",
      "encryption_type": "server_side",
      "encryption_details": {
        "status": "encrypted",
        "type": "server_side",
        "algorithm": "AES256"
      },
      "compliant": true
    },
    {
      "id": "my-dynamodb-table",
      "name": "my-dynamodb-table",
      "type": "database",
      "provider": "aws",
      "region": "us-east-1",
      "encryption_type": "customer_managed_key",
      "encryption_details": {
        "status": "encrypted",
        "type": "customer_managed_key",
        "key_id": "arn:aws:kms:us-east-1:123456789012:key/abcd1234-a123-456a-a12b-a123b4cd56ef"
      },
      "compliant": true
    }
  ],
  "errors": []
}
```

## Scheduled Execution

The tool can be set up to run automatically on a regular schedule using various methods:

### Using Cron

A sample cron script is provided in `cron-example.sh` that can be scheduled to run at your preferred frequency:

```bash
# Make the script executable
chmod +x cron-example.sh

# Edit your crontab
crontab -e

# Add one of these lines:
# Run weekly (every Sunday at 1:00 AM)
0 1 * * 0 /path/to/fedramp-continuous-validation-prototype/cron-example.sh

# Run monthly (1st day of month at 2:00 AM)
0 2 1 * * /path/to/fedramp-continuous-validation-prototype/cron-example.sh
```

### Using Docker

The included Docker setup allows for containerized execution:

```bash
# Build the Docker image
docker build -t fedramp-validator .

# Run the validation
docker run --env-file .env -v ./reports:/app/reports fedramp-validator validate --provider aws --s3-buckets bucket1,bucket2
```

### CI/CD Integration

The `.github/workflows/example-ci.yml` file demonstrates how to integrate the validation into a CI/CD pipeline with GitHub Actions.

## Extending the Tool

### Adding New Cloud Providers

1. Create a new provider file in `src/providers/`
2. Create a new validator in `src/validators/`
3. Update the main CLI to include the new provider

### Adding New Resource Types

1. Add the new resource type to the `ResourceType` enum in `src/models.py`
2. Implement the validation logic in the appropriate provider class
3. Add a new validation method to the relevant validator class

## License

MIT