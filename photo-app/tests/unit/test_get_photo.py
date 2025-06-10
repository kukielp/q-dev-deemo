import json
import unittest
from unittest.mock import patch, MagicMock
import os
import sys
from botocore.exceptions import ClientError

# Add the Lambda function directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/get_photo'))

# Import the Lambda function
import app

class TestGetPhotoFunction(unittest.TestCase):
    """
    Unit tests for the get_photo Lambda function
    """
    
    @patch('app.s3_client')
    @patch('app.dynamodb')
    def test_successful_get_photo(self, mock_dynamodb, mock_s3_client):
        """Test successful photo retrieval"""
        # Mock environment variables
        os.environ['PHOTOS_TABLE'] = 'test-photos-table'
        os.environ['PHOTOS_BUCKET'] = 'test-photos-bucket'
        os.environ['URL_EXPIRATION'] = '3600'
        
        # Mock DynamoDB response
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.get_item.return_value = {
            'Item': {
                'photoId': 'test-photo-id',
                'fileName': 'test-image.jpg',
                'uploadTimestamp': '2023-01-01T12:00:00',
                's3Key': 'test-photo-id/test-image.jpg'
            }
        }
        
        # Mock S3 presigned URL
        mock_s3_client.generate_presigned_url.return_value = 'https://test-presigned-url.com'
        
        # Create test event
        event = {
            'pathParameters': {
                'photoId': 'test-photo-id'
            }
        }
        
        # Call the Lambda function
        response = app.lambda_handler(event, {})
        
        # Verify the response
        self.assertEqual(response['statusCode'], 200)
        
        # Parse the response body
        body = json.loads(response['body'])
        self.assertEqual(body['photoId'], 'test-photo-id')
        self.assertEqual(body['fileName'], 'test-image.jpg')
        self.assertEqual(body['uploadTimestamp'], '2023-01-01T12:00:00')
        self.assertEqual(body['downloadUrl'], 'https://test-presigned-url.com')
        
        # Verify DynamoDB get_item was called
        mock_table.get_item.assert_called_once_with(
            Key={'photoId': 'test-photo-id'}
        )
        
        # Verify S3 generate_presigned_url was called
        mock_s3_client.generate_presigned_url.assert_called_once_with(
            'get_object',
            Params={
                'Bucket': 'test-photos-bucket',
                'Key': 'test-photo-id/test-image.jpg'
            },
            ExpiresIn=3600
        )
    
    @patch('app.s3_client')
    @patch('app.dynamodb')
    def test_missing_photo_id(self, mock_dynamodb, mock_s3_client):
        """Test error handling when photo ID is missing"""
        # Create test event with missing photo ID
        event = {
            'pathParameters': {}  # Missing photoId
        }
        
        # Call the Lambda function
        response = app.lambda_handler(event, {})
        
        # Verify the response
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertIn('error', body)
        
        # Verify no DynamoDB or S3 calls were made
        mock_dynamodb.Table.assert_not_called()
        mock_s3_client.generate_presigned_url.assert_not_called()
    
    @patch('app.s3_client')
    @patch('app.dynamodb')
    def test_photo_not_found(self, mock_dynamodb, mock_s3_client):
        """Test error handling when photo is not found in DynamoDB"""
        # Mock environment variables
        os.environ['PHOTOS_TABLE'] = 'test-photos-table'
        
        # Mock DynamoDB response for photo not found
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.get_item.return_value = {}  # No Item in response
        
        # Create test event
        event = {
            'pathParameters': {
                'photoId': 'non-existent-photo-id'
            }
        }
        
        # Call the Lambda function
        response = app.lambda_handler(event, {})
        
        # Verify the response
        self.assertEqual(response['statusCode'], 404)
        body = json.loads(response['body'])
        self.assertIn('error', body)
        
        # Verify DynamoDB was called but S3 was not
        mock_table.get_item.assert_called_once()
        mock_s3_client.generate_presigned_url.assert_not_called()
    
    @patch('app.s3_client')
    @patch('app.dynamodb')
    def test_s3_error_handling(self, mock_dynamodb, mock_s3_client):
        """Test error handling when S3 presigned URL generation fails"""
        # Mock environment variables
        os.environ['PHOTOS_TABLE'] = 'test-photos-table'
        os.environ['PHOTOS_BUCKET'] = 'test-photos-bucket'
        os.environ['URL_EXPIRATION'] = '3600'
        
        # Mock DynamoDB response
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.get_item.return_value = {
            'Item': {
                'photoId': 'test-photo-id',
                'fileName': 'test-image.jpg',
                'uploadTimestamp': '2023-01-01T12:00:00',
                's3Key': 'test-photo-id/test-image.jpg'
            }
        }
        
        # Mock S3 error
        mock_s3_client.generate_presigned_url.side_effect = ClientError(
            {'Error': {'Code': 'AccessDenied', 'Message': 'Access Denied'}},
            'generate_presigned_url'
        )
        
        # Create test event
        event = {
            'pathParameters': {
                'photoId': 'test-photo-id'
            }
        }
        
        # Call the Lambda function
        response = app.lambda_handler(event, {})
        
        # Verify the response
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertIn('error', body)
        
        # Verify both DynamoDB and S3 were called
        mock_table.get_item.assert_called_once()
        mock_s3_client.generate_presigned_url.assert_called_once()

if __name__ == '__main__':
    unittest.main()