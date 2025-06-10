# Serverless Photo Upload Application

A serverless application for uploading and retrieving photos using AWS services. This application provides a simple way to store and retrieve photos with associated metadata.

## Architecture

![Architecture Diagram](https://via.placeholder.com/800x400?text=Photo+App+Architecture)

### Components

- **Frontend**: Simple HTML/CSS/JavaScript application for uploading and retrieving photos
- **API Gateway**: HTTP API with endpoints for uploading and retrieving photos
- **Lambda Functions**: Serverless functions for handling photo uploads and retrievals
- **S3**: Private bucket for storing photos
- **DynamoDB**: Table for storing photo metadata

### API Endpoints

- `POST /photos`: Upload a photo with metadata
- `GET /photos/{photoId}`: Retrieve a photo by ID (returns pre-signed URL)

### Data Model

**Photos Table (DynamoDB)**
- `photoId` (Partition Key): Unique identifier for the photo
- `fileName`: Original file name of the photo
- `uploadTimestamp`: Timestamp when the photo was uploaded
- `s3Key`: Key for retrieving the photo from S3

## Setup Instructions

### Prerequisites

- [AWS CLI](https://aws.amazon.com/cli/) installed and configured
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) installed
- [Python 3.9](https://www.python.org/downloads/) or later

### Deployment

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/photo-app.git
   cd photo-app
   ```

2. Deploy the application using SAM:
   ```
   sam build
   sam deploy --guided
   ```

3. Follow the prompts to configure the deployment:
   - Stack Name: `photo-app`
   - AWS Region: Your preferred region
   - Parameter Stage: `dev` (or your preferred stage)
   - Confirm changes before deployment: `Y`
   - Allow SAM CLI to create IAM roles: `Y`

4. Note the outputs from the deployment:
   - `ApiEndpoint`: The URL of your API
   - `PhotosBucketName`: The name of the S3 bucket
   - `PhotosTableName`: The name of the DynamoDB table

5. Update the frontend configuration:
   - Open `src/frontend/index.html`
   - Replace the `API_URL` value with your API endpoint URL

### Local Development

#### Running the Frontend Locally

You can run the frontend locally by opening the `src/frontend/index.html` file in your browser. Make sure to update the `API_URL` to point to your deployed API.

#### Testing Lambda Functions Locally

1. Install dependencies:
   ```
   pip install -r src/upload_photo/requirements.txt
   pip install -r src/get_photo/requirements.txt
   ```

2. Use SAM CLI to invoke functions locally:
   ```
   # Test upload_photo function
   sam local invoke UploadPhotoFunction -e events/upload_photo_event.json
   
   # Test get_photo function
   sam local invoke GetPhotoFunction -e events/get_photo_event.json
   ```

### Running Tests

Run unit tests with:
```
python -m unittest discover tests/unit
```

## Security Considerations

- The S3 bucket is configured as private
- API Gateway endpoints use CORS to restrict access
- Lambda functions use least-privilege IAM roles
- DynamoDB table uses server-side encryption

## Limitations and Future Improvements

- Currently, there's no authentication or user management
- No image processing or resizing
- Limited error handling in the frontend
- No pagination for listing photos

## License

This project is licensed under the MIT License - see the LICENSE file for details.