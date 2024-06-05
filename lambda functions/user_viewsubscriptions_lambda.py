import boto3

def lambda_handler(event, context):
    headers = event.get('headers', {})
    user_email = headers.get('X-User-Email')
    if not user_email:
        return {'statusCode': 400, 'body': 'Email address is required'}

    dynamodb = boto3.resource('dynamodb')
    s3_client = boto3.client('s3')
    bucket_name = 's3952532-s3bucket'

    subscription_table = dynamodb.Table('subscription')
    try:
        response = subscription_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('email').eq(user_email)
        )
        subscriptions = response.get('Items', [])
    except Exception as e:
        return {'statusCode': 500, 'body': f'An error occurred: {str(e)}'}

    # Function to construct the key based on title and artist
    def get_artist_image_url(artist):
        object_key = f'{artist}.jpg'
        # Generate a URL that allows public access to the object
        url = s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket_name, 'Key': object_key},
                                               ExpiresIn=3600)
        return url

    # Enhance subscription details with artist image URL
    enhanced_subscriptions = []
    for sub in subscriptions:
        artist = sub.get('artist')
        if artist:
            artist_image_url = get_artist_image_url(artist)
            sub['artist_image_url'] = artist_image_url
        enhanced_subscriptions.append(sub)

    return {
        'statusCode': 200,
        'body': enhanced_subscriptions
    }

