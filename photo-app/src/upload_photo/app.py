import json
import os
import uuid
import base64
import boto3
from datetime import datetime

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Get environment variables
BUCKET_NAME = os.environ.get('PHOTOS_BUCKET_NAME')
TABLE_NAME = os.environ.get('PHOTOS_TABLE_NAME')

# Get DynamoDB table
photos_table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    """
    Lambda function to handle photo uploads.
    
    This function:
    1. Receives a base64 encoded image and metadata from API Gateway
    2. Decodes the image
    3. Uploads the image to S3
    4. Stores metadata in DynamoDB
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response with photoId
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        
        # Extract image data and metadata
        image_data = body.get('image')
        file_name = body.get('fileName')
        
        # Validate input
        if not image_data or not file_name:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Missing required fields: image and fileName'})
            }
        
        # Generate unique photo ID
        photo_id = str(uuid.uuid4())
        
        # Decode base64 image
        image_content = base64.b64decode(image_data)
        
        # Generate S3 key
        s3_key = f"{photo_id}/{file_name}"
        
        # Upload to S3
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=image_content,
            ContentType='image/jpeg'  # Assuming JPEG, could be determined from file extension
        )
        
        # Current timestamp
        timestamp = datetime.utcnow().isoformat()
        
        # Store metadata in DynamoDB
        photos_table.put_item(
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
                'message': 'Photo uploaded successfully'
            })
        }
        
    except Exception as e:
        # Log error
        print(f"Error: {str(e)}")
        
        # Return error response
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Failed to upload photo'})
        }