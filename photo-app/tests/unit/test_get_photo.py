import json
import os
import unittest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError

# Set environment variables for testing
os.environ['PHOTOS_BUCKET_NAME'] = 'test-bucket'
os.environ['PHOTOS_TABLE_NAME'] = 'test-table'
os.environ['PRESIGNED_URL_EXPIRATION'] = '3600'

# Import the Lambda function
from src.get_photo.app import lambda_handler

class TestGetPhoto(unittest.TestCase):
    """
    Unit tests for the get_photo Lambda function
    """
    
    @patch('src.get_photo.app.boto3.client')
    @patch('src.get_photo.app.boto3.resource')
    def test_successful_retrieval(self, mock_resource, mock_client):
        """Test successful photo retrieval"""
        # Mock S3 client
        mock_s3 = MagicMock()
        mock_s3.generate_presigned_url.return_value = "https://test-presigned-url.com"
        mock_client.return_value = mock_s3
        
        # Mock DynamoDB table and response
        mock_table = MagicMock()
        mock_table.get_item.return_value = {
            'Item': {
                'photoId': 'test-photo-id',
                'fileName': 'test-image.jpg',
                'uploadTimestamp': '2023-01-01T12:00:00',
                's3Key': 'test-photo-id/test-image.jpg'
            }
        }
        mock_dynamodb = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_resource.return_value = mock_dynamodb
        
        # Create test event
        event = {
            'pathParameters': {
                'photoId': 'test-photo-id'
            }
        }
        
        # Call the Lambda function
        response = lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 200)
        response_body = json.loads(response['body'])
        self.assertEqual(response_body['photoId'], 'test-photo-id')
        self.assertEqual(response_body['fileName'], 'test-image.jpg')
        self.assertEqual(response_body['downloadUrl'], 'https://test-presigned-url.com')
        
        # Verify DynamoDB get_item was called
        mock_table.get_item.assert_called_once()
        
        # Verify S3 generate_presigned_url was called
        mock_s3.generate_presigned_url.assert_called_once()
    
    @patch('src.get_photo.app.boto3.client')
    @patch('src.get_photo.app.boto3.resource')
    def test_missing_photo_id(self, mock_resource, mock_client):
        """Test handling of missing photoId"""
        # Create test event with missing photoId
        event = {
            'pathParameters': {}
        }
        
        # Call the Lambda function
        response = lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 400)
        self.assertIn('error', json.loads(response['body']))
    
    @patch('src.get_photo.app.boto3.client')
    @patch('src.get_photo.app.boto3.resource')
    def test_photo_not_found(self, mock_resource, mock_client):
        """Test handling of photo not found in DynamoDB"""
        # Mock DynamoDB table and response for item not found
        mock_table = MagicMock()
        mock_table.get_item.return_value = {}  # No Item in response
        mock_dynamodb = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_resource.return_value = mock_dynamodb
        
        # Create test event
        event = {
            'pathParameters': {
                'photoId': 'non-existent-id'
            }
        }
        
        # Call the Lambda function
        response = lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 404)
        self.assertIn('error', json.loads(response['body']))
    
    @patch('src.get_photo.app.boto3.client')
    @patch('src.get_photo.app.boto3.resource')
    def test_s3_client_error(self, mock_resource, mock_client):
        """Test handling of S3 client error"""
        # Mock DynamoDB table and response
        mock_table = MagicMock()
        mock_table.get_item.return_value = {
            'Item': {
                'photoId': 'test-photo-id',
                'fileName': 'test-image.jpg',
                'uploadTimestamp': '2023-01-01T12:00:00',
                's3Key': 'test-photo-id/test-image.jpg'
            }
        }
        mock_dynamodb = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_resource.return_value = mock_dynamodb
        
        # Mock S3 client to raise ClientError
        mock_s3 = MagicMock()
        mock_s3.generate_presigned_url.side_effect = ClientError(
            {'Error': {'Code': 'AccessDenied', 'Message': 'Access Denied'}},
            'generate_presigned_url'
        )
        mock_client.return_value = mock_s3
        
        # Create test event
        event = {
            'pathParameters': {
                'photoId': 'test-photo-id'
            }
        }
        
        # Call the Lambda function
        response = lambda_handler(event, {})
        
        # Verify response
        self.assertEqual(response['statusCode'], 500)
        self.assertIn('error', json.loads(response['body']))

if __name__ == '__main__':
    unittest.main()