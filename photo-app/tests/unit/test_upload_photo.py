import json
import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import base64

# Add the Lambda function directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src/upload_photo'))

# Import the Lambda function
import app

class TestUploadPhotoFunction(unittest.TestCase):
    """
    Unit tests for the upload_photo Lambda function
    """
    
    @patch('app.s3_client')
    @patch('app.dynamodb')
    def test_successful_upload(self, mock_dynamodb, mock_s3_client):
        """Test successful photo upload"""
        # Mock environment variables
        os.environ['PHOTOS_TABLE'] = 'test-photos-table'
        os.environ['PHOTOS_BUCKET'] = 'test-photos-bucket'
        
        # Mock DynamoDB table
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        
        # Create test image data
        test_image = b'test image data'
        base64_image = base64.b64encode(test_image).decode('utf-8')
        
        # Create test event
        event = {
            'body': json.dumps({
                'fileName': 'test-image.jpg',
                'image': base64_image
            })
        }
        
        # Call the Lambda function
        response = app.lambda_handler(event, {})
        
        # Verify the response
        self.assertEqual(response['statusCode'], 201)
        
        # Parse the response body
        body = json.loads(response['body'])
        self.assertIn('photoId', body)
        self.assertEqual(body['fileName'], 'test-image.jpg')
        self.assertIn('uploadTimestamp', body)
        
        # Verify S3 upload was called
        mock_s3_client.put_object.assert_called_once()
        args, kwargs = mock_s3_client.put_object.call_args
        self.assertEqual(kwargs['Bucket'], 'test-photos-bucket')
        self.assertTrue(kwargs['Key'].endswith('test-image.jpg'))
        self.assertEqual(kwargs['Body'], test_image)
        
        # Verify DynamoDB put_item was called
        mock_table.put_item.assert_called_once()
        args, kwargs = mock_table.put_item.call_args
        item = kwargs['Item']
        self.assertEqual(item['fileName'], 'test-image.jpg')
        self.assertEqual(item['photoId'], body['photoId'])
        self.assertIn('s3Key', item)
        self.assertIn('uploadTimestamp', item)
    
    @patch('app.s3_client')
    @patch('app.dynamodb')
    def test_missing_body(self, mock_dynamodb, mock_s3_client):
        """Test error handling when request body is missing"""
        # Create test event with missing body
        event = {}
        
        # Call the Lambda function
        response = app.lambda_handler(event, {})
        
        # Verify the response
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertIn('error', body)
        
        # Verify no S3 or DynamoDB calls were made
        mock_s3_client.put_object.assert_not_called()
        mock_dynamodb.Table.assert_not_called()
    
    @patch('app.s3_client')
    @patch('app.dynamodb')
    def test_missing_required_fields(self, mock_dynamodb, mock_s3_client):
        """Test error handling when required fields are missing"""
        # Create test event with missing fields
        event = {
            'body': json.dumps({
                'fileName': 'test-image.jpg'
                # Missing 'image' field
            })
        }
        
        # Call the Lambda function
        response = app.lambda_handler(event, {})
        
        # Verify the response
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertIn('error', body)
        
        # Verify no S3 or DynamoDB calls were made
        mock_s3_client.put_object.assert_not_called()
        mock_dynamodb.Table.assert_not_called()
    
    @patch('app.s3_client')
    @patch('app.dynamodb')
    def test_invalid_image_data(self, mock_dynamodb, mock_s3_client):
        """Test error handling when image data is invalid"""
        # Create test event with invalid base64 data
        event = {
            'body': json.dumps({
                'fileName': 'test-image.jpg',
                'image': 'not-valid-base64!'
            })
        }
        
        # Call the Lambda function
        response = app.lambda_handler(event, {})
        
        # Verify the response
        self.assertEqual(response['statusCode'], 400)
        body = json.loads(response['body'])
        self.assertIn('error', body)
        
        # Verify no S3 or DynamoDB calls were made
        mock_s3_client.put_object.assert_not_called()
        mock_dynamodb.Table.assert_not_called()
    
    @patch('app.s3_client')
    @patch('app.dynamodb')
    def test_s3_error_handling(self, mock_dynamodb, mock_s3_client):
        """Test error handling when S3 upload fails"""
        # Mock environment variables
        os.environ['PHOTOS_TABLE'] = 'test-photos-table'
        os.environ['PHOTOS_BUCKET'] = 'test-photos-bucket'
        
        # Mock S3 error
        mock_s3_client.put_object.side_effect = Exception("S3 error")
        
        # Create test image data
        test_image = b'test image data'
        base64_image = base64.b64encode(test_image).decode('utf-8')
        
        # Create test event
        event = {
            'body': json.dumps({
                'fileName': 'test-image.jpg',
                'image': base64_image
            })
        }
        
        # Call the Lambda function
        response = app.lambda_handler(event, {})
        
        # Verify the response
        self.assertEqual(response['statusCode'], 500)
        body = json.loads(response['body'])
        self.assertIn('error', body)
        
        # Verify S3 was called but DynamoDB was not
        mock_s3_client.put_object.assert_called_once()
        mock_dynamodb.Table.assert_not_called()

if __name__ == '__main__':
    unittest.main()