import os
import click
from typing import List, Optional
from dotenv import load_dotenv
from rich.console import Console

from .validators.aws_validator import AWSValidator
from .report.generator import ReportGenerator


# Initialize console for pretty output
console = Console()


@click.group()
def cli():
    """FedRAMP Continuous Validation Tool.
    
    Validates encryption compliance for cloud resources.
    """
    # Load environment variables from .env file if present
    load_dotenv()


@cli.command()
@click.option('--provider', type=click.Choice(['aws', 'azure', 'gcp']), default='aws',
              help='Cloud provider to validate.')
@click.option('--region', help='Cloud provider region.')
@click.option('--profile', help='Cloud provider profile (e.g. AWS profile).')
@click.option('--s3-buckets', help='Comma-separated list of S3 bucket names to validate.')
@click.option('--dynamodb-tables', help='Comma-separated list of DynamoDB table names to validate.')
@click.option('--rds-instances', help='Comma-separated list of RDS instance identifiers to validate.')
@click.option('--output-dir', help='Directory to write reports to.')
@click.option('--format', 'output_format', type=click.Choice(['json', 'csv', 'all']), default='all',
              help='Output format for the report.')
def validate(provider: str, region: Optional[str], profile: Optional[str],
             s3_buckets: Optional[str], dynamodb_tables: Optional[str], 
             rds_instances: Optional[str], output_dir: Optional[str],
             output_format: str):
    """Validate encryption for cloud resources."""
    # Parse comma-separated lists
    s3_bucket_list = s3_buckets.split(',') if s3_buckets else []
    dynamodb_table_list = dynamodb_tables.split(',') if dynamodb_tables else []
    rds_instance_list = rds_instances.split(',') if rds_instances else []
    
    # Validate at least one resource type was specified
    if not any([s3_bucket_list, dynamodb_table_list, rds_instance_list]):
        console.print("[bold red]Error:[/bold red] No resources specified for validation.")
        console.print("Please specify at least one resource using --s3-buckets, --dynamodb-tables, or --rds-instances.")
        return
    
    # Initialize validator based on provider
    if provider == 'aws':
        validator = AWSValidator(region_name=region, profile=profile)
    else:
        console.print(f"[bold red]Error:[/bold red] Provider {provider} not yet implemented.")
        return
    
    console.print(f"[bold green]Starting validation for {provider.upper()} resources...[/bold green]")
    
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
    report_generator = ReportGenerator(output_dir=output_dir)
    
    if output_format == 'json' or output_format == 'all':
        json_path = report_generator.generate_json(result)
        console.print(f"JSON report written to: [bold]{json_path}[/bold]")
        
    if output_format == 'csv' or output_format == 'all':
        csv_path = report_generator.generate_csv(result)
        console.print(f"CSV report written to: [bold]{csv_path}[/bold]")
    
    # Always generate summary
    summary_path = report_generator.generate_summary(result)
    console.print(f"Summary report written to: [bold]{summary_path}[/bold]")
    
    # Print summary to console
    if result.all_encrypted:
        console.print("\n[bold green]✓ ALL RESOURCES ARE ENCRYPTED[/bold green]")
    else:
        console.print("\n[bold red]✗ SOME RESOURCES ARE NOT ENCRYPTED[/bold red]")
    
    console.print(f"\nTotal resources checked: {len(result.storage_locations)}")
    console.print(f"Compliant: {sum(1 for loc in result.storage_locations if loc.compliant)}")
    console.print(f"Non-compliant: {sum(1 for loc in result.storage_locations if not loc.compliant)}")
    
    if result.errors:
        console.print(f"\n[bold yellow]Errors: {len(result.errors)}[/bold yellow]")


if __name__ == '__main__':
    cli()