import json
import boto3
from botocore.exceptions import ClientError

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb')
subscription_table = dynamodb.Table('subscription')


def lambda_handler(event, context):
    # Extracting user email from the request header
    headers = event.get('headers', {})
    user_email = headers.get('X-User-Email')
    if not user_email:
        return {
            'statusCode': 403,
            'body': json.dumps('You must be logged in to subscribe.')
        }

    # Assuming the request body is JSON and contains title, artist, and year
    try:
        body = json.loads(event['body'])
        title = body['title'].lower()
        artist = body['artist'].lower()
        year = body['year']
    except KeyError as e:
        return {
            'statusCode': 400,
            'body': json.dumps(f'Missing data for subscription: {str(e)}')
        }

    try:
        # Check if the subscription already exists
        response = subscription_table.get_item(
            Key={'email': user_email, 'title': title}
        )
        if 'Item' in response:
            # If the subscription exists, inform the user
            return {
                'statusCode': 200,
                'body': json.dumps('You have already subscribed to this music.')
            }

        # If the subscription does not exist, create a new one
        subscription_item = {
            'email': user_email,  # Partition key
            'title': title,  # Sort key
            'artist': artist,
            'year': year
        }
        # Insert the new item into the subscription table
        subscription_table.put_item(Item=subscription_item)
        return {
            'statusCode': 200,
            'body': json.dumps('Successfully subscribed!')
        }

    except ClientError as e:
        print(f"Failed to subscribe: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Failed to subscribe. Please try again.')
        }

