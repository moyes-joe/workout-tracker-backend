import os

import boto3
from mypy_boto3_dynamodb import DynamoDBClient


def main() -> None:
    """Create a DynamoDB table locally."""
    client: DynamoDBClient = boto3.client(
        "dynamodb", endpoint_url="http://localhost:9999"
    )  # type: ignore
    if table_name := os.getenv("TABLE_NAME"):
        client.create_table(
            AttributeDefinitions=[
                {"AttributeName": "PK", "AttributeType": "S"},
                {"AttributeName": "SK", "AttributeType": "S"},
            ],
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "PK", "KeyType": "HASH"},
                {"AttributeName": "SK", "KeyType": "RANGE"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
    else:
        print("TABLE_NAME environment variable not set")


if __name__ == "__main__":
    main()
