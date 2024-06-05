import boto3
from boto3.dynamodb.conditions import Key, Attr

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    music_table = dynamodb.Table('music')

    # Get filter expressions from the event
    title = event.get('title')
    artist = event.get('artist')
    year = event.get('year')

    # Build the DynamoDB filter expression
    filter_expression = None
    if title:
        filter_expression = Attr('title').eq(title)
    if artist:
        if filter_expression:
            filter_expression &= Attr('artist').eq(artist)
        else:
            filter_expression = Attr('artist').eq(artist)
    if year:
        if filter_expression:
            filter_expression &= Attr('year').eq(year)
        else:
            filter_expression = Attr('year').eq(year)

    # Execute the query
    if filter_expression:
        response = music_table.scan(
            FilterExpression=filter_expression
        )
        items = response.get('Items', [])
    else:
        items = []

    return {
        'statusCode': 200,
        'body': items
    }
