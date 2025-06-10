# Serverless Photo Application

A serverless application for uploading, storing, and retrieving photos using AWS services.

## Architecture

![Architecture Diagram](https://via.placeholder.com/800x400?text=Serverless+Photo+App+Architecture)

### Components

- **Frontend**: Simple HTML/CSS/JS interface for uploading and viewing photos
- **API Gateway**: HTTP API with endpoints for uploading and retrieving photos
- **Lambda Functions**: 
  - `UploadPhotoFunction`: Handles photo uploads, stores in S3, and saves metadata to DynamoDB
  - `GetPhotoFunction`: Retrieves photo metadata and generates pre-signed URLs for downloads
- **S3**: Private bucket for secure photo storage
- **DynamoDB**: NoSQL database for storing photo metadata

### API Endpoints

- `POST /photos`: Upload a photo with metadata
- `GET /photos/{photoId}`: Get a photo by ID (returns pre-signed URL)

## Setup Instructions

### Prerequisites

- [AWS CLI](https://aws.amazon.com/cli/) configured with appropriate permissions
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
- Python 3.9 or later

### Deployment

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/serverless-photo-app.git
   cd serverless-photo-app
   ```

2. Build the application:
   ```
   sam build
   ```

3. Deploy the application:
   ```
   sam deploy --guided
   ```
   Follow the prompts to configure your deployment.

4. After deployment, note the API Gateway endpoint URL from the outputs:
   ```
   -----------------------------------------------------
   Outputs
   -----------------------------------------------------
   PhotosApiEndpoint: https://xxxxxxxxxx.execute-api.region.amazonaws.com/dev
   ```

5. Update the frontend with your API endpoint:
   - Open `photo-app/src/frontend/index.html`
   - Replace `YOUR_API_GATEWAY_URL` with your actual API Gateway endpoint URL

### Local Testing

#### Running Unit Tests

```
cd photo-app
python -m pytest tests/unit/
```

#### Testing the Frontend Locally

You can test the frontend locally by opening the HTML file in a browser:

```
cd photo-app/src/frontend
# Open index.html in your browser
```

Note: You'll need to deploy the backend first and update the API endpoint in the HTML file.

## Usage

### Uploading Photos

1. Open the frontend application in a web browser
2. Click "Select a photo" and choose an image file
3. Click "Upload Photo"
4. The photo ID will be displayed upon successful upload

### Viewing Photos

1. Open the frontend application in a web browser
2. Previously uploaded photos will be displayed automatically
3. Click "Refresh Photos" to update the list

## Security Considerations

- S3 bucket is configured as private with no public access
- API Gateway uses IAM authentication
- Lambda functions follow least-privilege principle with specific IAM permissions
- Pre-signed URLs expire after 1 hour by default

## Development

### Project Structure

```
photo-app/
├── src/
│   ├── upload_photo/app.py         # Lambda function for photo uploads
│   ├── upload_photo/requirements.txt
│   ├── get_photo/app.py            # Lambda function for photo retrieval
│   ├── get_photo/requirements.txt
│   ├── frontend/index.html         # Simple web frontend
├── tests/
│   ├── unit/test_upload_photo.py   # Unit tests for upload function
│   ├── unit/test_get_photo.py      # Unit tests for get function
├── template.yaml                   # AWS SAM template
├── README.md                       # This file
```

### Adding Features

To add new features:

1. Modify the Lambda functions in `src/`
2. Update the SAM template in `template.yaml`
3. Add tests in `tests/unit/`
4. Update the frontend as needed
5. Rebuild and redeploy using SAM CLI

## License

This project is licensed under the MIT License - see the LICENSE file for details.