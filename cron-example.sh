#!/bin/bash
# FedRAMP Continuous Validation Cron Job Script

# Set path to the project directory
PROJECT_DIR="/path/to/fedramp-continuous-validation-prototype"
cd "$PROJECT_DIR" || exit 1

# Load environment variables if needed
if [ -f "$PROJECT_DIR/.env" ]; then
  source "$PROJECT_DIR/.env"
fi

# Activate virtual environment if using one
if [ -d "$PROJECT_DIR/venv" ]; then
  source "$PROJECT_DIR/venv/bin/activate"
fi

# Set timestamp for reports
TIMESTAMP=$(date +"%Y%m%d-%H%M%S")
REPORT_DIR="$PROJECT_DIR/reports/$TIMESTAMP"
mkdir -p "$REPORT_DIR"

# Run the validation
python check_encryption.py validate \
  --provider aws \
  --s3-buckets "$S3_BUCKETS" \
  --dynamodb-tables "$DYNAMODB_TABLES" \
  --rds-instances "$RDS_INSTANCES" \
  --output-dir "$REPORT_DIR"

# Optional: Retention policy - keep only the last 10 reports
cd "$PROJECT_DIR/reports" || exit 1
ls -t | tail -n +11 | xargs -I {} rm -rf {}

# Optional: Send notification if non-compliant resources detected
if grep -q '"all_encrypted": false' "$REPORT_DIR"/*.json; then
  # Send email or notification - example using mail command
  echo "FedRAMP Compliance Alert: Non-compliant resources detected!" | mail -s "FedRAMP Validation Failed" admin@example.com
fi

# Deactivate virtual environment if using one
if [ -d "$PROJECT_DIR/venv" ]; then
  deactivate
fi