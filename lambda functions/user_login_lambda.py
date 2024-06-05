import json
import boto3
from botocore.exceptions import ClientError

# Initialize a DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('login')

def lambda_handler(event, context):
    # Extract the email key and use it to get the password from the event
    email = list(event.keys())[0]  # Assuming the first key is the email
    password = event[email]  # The value of the key is the password

    try:
        # Retrieve user details from DynamoDB using the email as the key
        response = table.get_item(Key={'email': email})
        if 'Item' in response:
            # Check if the provided password matches the stored password
            user_details = response['Item']
            if user_details['password'] == password:
                return {
                    'statusCode': 200,
                    'body': json.dumps({'message': 'Login successful.',
                                        'user_name':user_details['user_name'],
                                        'user_email':user_details['email']
                    })
                }
            else:
                return {
                    'statusCode': 401,
                    'body': json.dumps({'message': 'Email or password is invalid'})
                }
        else:
            # No user found with the provided email
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Email or password is invalid'})
            }
    except ClientError as e:
        print(f"Error accessing database: {e.response['Error']['Message']}")
        return {'statusCode': 500, 'body': json.dumps({'message': 'An error occurred. Please try again.'})}
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {'statusCode': 500, 'body': json.dumps({'message': 'An error occurred. Please try again.'})}
