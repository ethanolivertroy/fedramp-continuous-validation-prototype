.PHONY: setup test validate clean

# Variables
PYTHON = python
VENV = venv
OUTPUT_DIR = ./reports

setup:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install -r requirements.txt

test:
	$(PYTHON) -m unittest discover -s tests

validate-aws:
	$(PYTHON) check_encryption.py validate --provider aws \
		--s3-buckets $(S3_BUCKETS) \
		--dynamodb-tables $(DYNAMODB_TABLES) \
		--rds-instances $(RDS_INSTANCES) \
		--output-dir $(OUTPUT_DIR)

validate-aws-profile:
	$(PYTHON) check_encryption.py validate --provider aws \
		--profile $(AWS_PROFILE) \
		--s3-buckets $(S3_BUCKETS) \
		--dynamodb-tables $(DYNAMODB_TABLES) \
		--rds-instances $(RDS_INSTANCES) \
		--output-dir $(OUTPUT_DIR)

clean:
	rm -rf $(OUTPUT_DIR)/*.json $(OUTPUT_DIR)/*.csv $(OUTPUT_DIR)/*.txt