import boto3
from botocore.exceptions import ClientError
from datetime import datetime
import os

# DynamoDB setup
dynamodb = boto3.resource('dynamodb', region_name='your-region')

# Get or create the DynamoDB table
def get_events_table():
    table_name = 'Events'
    try:
        table = dynamodb.Table(table_name)
        # Try to describe the table to check if it exists
        table.load()
        print(f"Table {table_name} already exists.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            # Create the table
            print(f"Creating table {table_name}...")
            table = dynamodb.create_table(
                TableName=table_name,
                KeySchema=[
                    {'AttributeName': 'id', 'KeyType': 'HASH'},  # Partition key
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'id', 'AttributeType': 'S'},
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5,
                }
            )
            # Wait until the table exists
            table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
            print(f"Table {table_name} created.")
        else:
            raise
    return table

events_table = get_events_table()
