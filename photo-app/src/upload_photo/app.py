import json
import os
import uuid
import boto3
from datetime import datetime

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Get environment variables
PHOTOS_TABLE = os.environ.get('PHOTOS_TABLE')
BUCKET_NAME = os.environ.get('PHOTOS_BUCKET')

def lambda_handler(event, context):
    """
    Lambda function to handle photo uploads.
    
    This function:
    1. Receives photo data from API Gateway
    2. Generates a unique ID for the photo
    3. Uploads the photo to S3
    4. Stores metadata in DynamoDB
    5. Returns the photo ID and other relevant information
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response with photo ID and status
    """
    try:
        # Parse the request body
        if 'body' not in event:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Missing request body'})
            }
            
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        
        # Validate required fields
        if 'fileName' not in body or 'image' not in body:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Missing required fields: fileName and image'})
            }
        
        file_name = body['fileName']
        image_data = body['image']
        
        # Check if image data is base64 encoded
        import base64
        try:
            # Try to decode the image data
            image_binary = base64.b64decode(image_data)
        except Exception:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Invalid image data format'})
            }
        
        # Generate a unique photo ID
        photo_id = str(uuid.uuid4())
        
        # Generate S3 key
        s3_key = f"{photo_id}/{file_name}"
        
        # Upload to S3
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=image_binary,
            ContentType='image/jpeg'  # Assuming JPEG, could be determined from file extension
        )
        
        # Get current timestamp
        timestamp = datetime.utcnow().isoformat()
        
        # Store metadata in DynamoDB
        table = dynamodb.Table(PHOTOS_TABLE)
        table.put_item(
            Item={
                'photoId': photo_id,
                'fileName': file_name,
                'uploadTimestamp': timestamp,
                's3Key': s3_key
            }
        )
        
        # Return success response
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'photoId': photo_id,
                'fileName': file_name,
                'uploadTimestamp': timestamp
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Internal server error'})
        }