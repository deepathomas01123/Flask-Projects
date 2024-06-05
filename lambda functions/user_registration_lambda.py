import json
import boto3
from botocore.exceptions import ClientError

# Initialize a DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('login')

def lambda_handler(event, context):
    # Extract the user registration data from the incoming JSON payload
    email = event['email']
    user_name = event['user_name']
    password = event['password']

    try:
        # Check if email already exists
        response = table.get_item(Key={'email': email})
        if 'Item' in response:
            # Email exists
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'The email already exists'})
            }
        else:
            # Unique email - insert the user
            table.put_item(Item={'email': email, 'user_name': user_name, 'password': password})
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'New user registered successfully. Please login.'})
            }
    except ClientError as e:
        print(f"Error accessing database: {e.response['Error']['Message']}")
        return {'statusCode': 200, 'body': json.dumps({'message': 'An error occurred. Please try again.'})}
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {'statusCode': 200, 'body': json.dumps({'message': 'An error occurred. Please try again.'})}
