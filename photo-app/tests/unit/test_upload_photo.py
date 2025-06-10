import json
import os
import unittest
from unittest.mock import patch, MagicMock

# Set environment variables for testing
os.environ['PHOTOS_BUCKET_NAME'] = 'test-bucket'
os.environ['PHOTOS_TABLE_NAME'] = 'test-table'

# Import the Lambda function
from src.upload_photo.app import lambda_handler

class TestUploadPhoto(unittest.TestCase):
    """
    Unit tests for the upload_photo Lambda function
    """
    
    @patch('src.upload_photo.app.boto3.client')
    @patch('src.upload_photo.app.boto3.resource')
    @patch('src.upload_photo.app.uuid.uuid4')
    def test_successful_upload(self, mock_uuid, mock_resource, mock_client):
        """Test successful photo upload"""
        # Mock UUID
        mock_uuid.return_value = "test-uuid"
        
        # Mock S3 client
        mock_s3 = MagicMock()
        mock_client.return_value = mock_s3
        
        # Mock DynamoDB table
        mock_table = MagicMock()
        mock_dynamodb = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_resource.return_value = mock_dynamodb
        
        # Create test event
        event = {
            'body': json.dumps({
                'image': 'SGVsbG8gV29ybGQ=',  # Base64 encoded "Hello World"
                'fileName': 'test-image.jpg'
            })
        }
        
        # Call the Lambda function
        response = lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 201)
        self.assertIn('photoId', json.loads(response['body']))
        
        # Verify S3 upload was called
        mock_s3.put_object.assert_called_once()
        
        # Verify DynamoDB put_item was called
        mock_table.put_item.assert_called_once()
    
    @patch('src.upload_photo.app.boto3.client')
    @patch('src.upload_photo.app.boto3.resource')
    def test_missing_fields(self, mock_resource, mock_client):
        """Test handling of missing required fields"""
        # Create test event with missing fields
        event = {
            'body': json.dumps({
                'image': 'SGVsbG8gV29ybGQ='  # Missing fileName
            })
        }
        
        # Call the Lambda function
        response = lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('error', json.loads(response['body']))
    
    @patch('src.upload_photo.app.boto3.client')
    @patch('src.upload_photo.app.boto3.resource')
    def test_s3_upload_error(self, mock_resource, mock_client):
        """Test handling of S3 upload error"""
        # Mock S3 client to raise exception
        mock_s3 = MagicMock()
        mock_s3.put_object.side_effect = Exception("S3 upload failed")
        mock_client.return_value = mock_s3
        
        # Mock DynamoDB table
        mock_table = MagicMock()
        mock_dynamodb = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_resource.return_value = mock_dynamodb
        
        # Create test event
        event = {
            'body': json.dumps({
                'image': 'SGVsbG8gV29ybGQ=',
                'fileName': 'test-image.jpg'
            })
        }
        
        # Call the Lambda function
        response = lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('error', json.loads(response['body']))

if __name__ == '__main__':
    unittest.main()