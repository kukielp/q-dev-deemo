import json
import os
import boto3
from botocore.exceptions import ClientError

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Get environment variables
BUCKET_NAME = os.environ.get('PHOTOS_BUCKET_NAME')
TABLE_NAME = os.environ.get('PHOTOS_TABLE_NAME')
URL_EXPIRATION = int(os.environ.get('PRESIGNED_URL_EXPIRATION', 3600))  # Default 1 hour

# Get DynamoDB table
photos_table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    """
    Lambda function to retrieve photos.
    
    This function:
    1. Receives a photoId from the path parameter
    2. Looks up the photo metadata in DynamoDB
    3. Generates a pre-signed URL for the S3 object
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response with photo metadata and pre-signed URL
    """
    try:
        # Get photoId from path parameters
        photo_id = event.get('pathParameters', {}).get('photoId')
        
        # Validate input
        if not photo_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Missing required parameter: photoId'})
            }
        
        # Get photo metadata from DynamoDB
        response = photos_table.get_item(
            Key={
                'photoId': photo_id
            }
        )
        
        # Check if photo exists
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Photo not found'})
            }
        
        # Get photo metadata
        photo_metadata = response['Item']
        s3_key = photo_metadata['s3Key']
        
        # Generate pre-signed URL
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': s3_key
            },
            ExpiresIn=URL_EXPIRATION
        )
        
        # Return success response with metadata and URL
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'photoId': photo_metadata['photoId'],
                'fileName': photo_metadata['fileName'],
                'uploadTimestamp': photo_metadata['uploadTimestamp'],
                'downloadUrl': presigned_url
            })
        }
        
    except ClientError as e:
        # Log error
        print(f"S3 Client Error: {str(e)}")
        
        # Return error response
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Failed to generate pre-signed URL'})
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
            'body': json.dumps({'error': 'Failed to retrieve photo'})
        }