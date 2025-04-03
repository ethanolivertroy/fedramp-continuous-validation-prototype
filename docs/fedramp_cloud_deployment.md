# Deploying to FedRAMP-Authorized Cloud Environments

This guide explains how to deploy the FedRAMP Continuous Validation Tool within FedRAMP-authorized cloud environments.

## Deployment Options

### AWS GovCloud

AWS GovCloud is FedRAMP High authorized and ideal for running this validation tool.

#### AWS Lambda Deployment

1. Package your application:
```bash
pip install -r requirements.txt -t ./package
cp -r src ./package/
cp check_encryption.py ./package/
cd package
zip -r ../lambda_package.zip .
```

2. Create a Lambda function with appropriate IAM permissions:
   - Read-only permissions for S3, DynamoDB, RDS
   - CloudWatch Logs for output
   - KMS for encryption verification

3. Schedule with EventBridge:
```json
{
  "name": "FedRAMPValidationSchedule",
  "description": "Runs FedRAMP validation monthly",
  "schedule_expression": "cron(0 1 1 * ? *)"
}
```

4. Configure environment variables:
```
S3_BUCKETS=bucket1,bucket2,bucket3
DYNAMODB_TABLES=table1,table2
RDS_INSTANCES=instance1,instance2
OUTPUT_S3_BUCKET=compliance-reports
```

#### AWS ECS/Fargate Task

Use this approach for longer-running validations or more complex environments:

1. Create an ECR repository for the container:
```bash
aws ecr create-repository --repository-name fedramp-validator
```

2. Build and push the Docker image:
```bash
docker build -t fedramp-validator .
aws ecr get-login-password | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com
docker tag fedramp-validator:latest $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/fedramp-validator:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/fedramp-validator:latest
```

3. Create an ECS Cluster, Task Definition, and Scheduled Task

### Azure Government

Azure Government is FedRAMP High authorized.

#### Azure Functions

1. Create a Function App with a Timer trigger:
```bash
func init FedRAMPValidator --python
cd FedRAMPValidator
func new --name ValidationFunction --template "Timer trigger"
```

2. Update `function.json`:
```json
{
  "scriptFile": "__init__.py",
  "bindings": [
    {
      "name": "mytimer",
      "type": "timerTrigger",
      "direction": "in",
      "schedule": "0 0 1 * *"
    }
  ]
}
```

3. Deploy:
```bash
func azure functionapp publish FedRAMPValidator
```

#### Azure Container Instances

For containerized deployment:

1. Create an Azure Container Registry:
```bash
az acr create --resource-group MyResourceGroup --name fedrampvalidator --sku Basic
```

2. Build and push:
```bash
az acr build --registry fedrampvalidator --image fedramp-validator:latest .
```

3. Deploy as a scheduled container task with Logic Apps

## Security Considerations

### Data Access

- Use managed identities instead of storing credentials
- Implement least privilege IAM policies
- Consider using AWS Nitro enclaves or confidential computing for enhanced security

### Logging and Monitoring

- Enable AWS CloudTrail or Azure Activity Logs
- Ship logs to a SIEM that's already part of your FedRAMP ATO
- Add alerts for compliance deviations

### Encryption

- Encrypt all validation reports at rest
- Use TLS 1.2+ for any data in transit
- Consider client-side encryption for sensitive findings

## Compliance Documentation

When deploying this tool in a FedRAMP-authorized environment, document:

1. **Purpose**: How the tool helps maintain compliance
2. **Component Inventory**: Where the tool runs, what resources it accesses
3. **Configuration Management**: How changes to the tool are controlled
4. **Continuous Monitoring**: How results are reviewed and tracked
5. **Incident Response**: Procedures for handling non-compliant findings

## Example: AWS CloudFormation Template

A basic CloudFormation template for deploying as a Lambda function is included in `aws-govcloud-cfn.yaml`