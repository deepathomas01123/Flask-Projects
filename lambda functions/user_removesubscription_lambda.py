import json
import boto3
from botocore.exceptions import ClientError

# Initialize a DynamoDB resource
dynamodb = boto3.resource('dynamodb')
subscription_table = dynamodb.Table('subscription')


def lambda_handler(event, context):
    user_email = event['email']
    title = event['title']

    try:
        # Perform the deletion from the DynamoDB table
        response = subscription_table.delete_item(
            Key={
                'email': user_email,
                'title': title
            }
        )
        # Prepare a success response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'message': 'Subscription removed successfully.'})
        }
    except Exception as e:
        # Log the error and prepare an error response
        print(e)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': 'Failed to remove the subscription.'})
        }


