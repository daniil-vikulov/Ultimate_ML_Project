# Documentation for the image processing API

## General description

This API provides functionality for uploading images and performing various processing operations such as censorship,
classification, and detection of objects in an image. The API is implemented in Flask and uses various internal
functions for image processing.

The main server code is in the file `src/app/app.py`

**Base URL**: http://localhost:5000, when running through Docker http://server:5000

## Data Formats
**Supported Formats**: JSON for responses, multipart/form-data for requests with files.

## Endpoints

### POST /censor_colour
#### Description
Uploads an image and performs censorship using the specified color.

#### Request Body (multipart/form-data)
- file (file): The image to upload.
- colour (string): The color to use for censorship.

#### Example Request
`curl -X POST "http://localhost:5000/censor_colour" -F "file=@/path/to/your/image.jpg" -F "colour=red"`

#### Responses

##### Success (200)
    {"message": "Image censored with colour",
    "censored_image_path": "uploads/image_censored.jpg"}

##### Error (500)
    {"error": "Internal Server Error"}

### POST /classify

#### Description
Uploads an image and performs classification on it.

#### Request Body (multipart/form-data)
- file (file): The image to upload.

#### Example Request
`curl -X POST "http://localhost:5000/classify" -F "file=@/path/to/your/image.jpg"`

#### Responses
##### Success (200)
    {"safe": 0.987,
    "unsafe": 0.013}

##### Error (500)
    { "error": "Internal Server Error"}

### POST /detect

#### Description
Uploads an image and performs object detection on it.

#### Request Body (multipart/form-data)
- file (file): The image to upload.

#### Example Request
`curl -X POST "http://localhost:5000/detect" -F "file=@/path/to/your/image.jpg"`

#### Responses
##### Success (200)
    { "detected_parts": [
        {
            "class": "face_female",
            "score": 0.987
        },
        {
            "class": "face_male",
            "score": 0.876
        }
    ]}

##### Error (500)
    { "error": "Internal Server Error"}

### POST /message

#### Description
Logs a message containing information about the user and the message.

#### Headers
- Content-Type: application/json

#### Request Body (application/json)
    {"username": "user123",
    "user_id": 1,
    "group_id": 2,
    "message": "This is a sample message",
    "is_text": 1,
    "is_nsfw": 0}

#### Example Request
    curl -X POST "http://localhost:5000/message" -H "Content-Type: application/json" -d '{
    "username": "user123",
    "user_id": 1,
    "group_id": 2,
    "message": "This is a sample message",
    "is_text": 1,
    "is_nsfw": 0
    }

#### Responses
##### Success (200)
    { "message": "Message logged successfully"}

##### Error (500)
    { "error": "Internal Server Error"}

### GET /stats/{group_id}/{user_id}

#### Description
Retrieves statistics for a specific user within a specified group.

#### Request Parameters
- group_id (path): The ID of the group.
- user_id (path): The ID of the user.

#### Example Request
`curl -X GET "http://localhost:5000/stats/1/123"`

#### Responses

##### Success (200)
    {"user_id": 123,
    "group_id": 1,
    "username": "user123",
    "count_test_messages_sent": 50,
    "count_safe_photos_sent": 10,
    "count_nsfw_photos_sent": 5,
    "last_active": "2023-10-01T12:34:56" }

##### Not Found (404)
    {"message": "No stats found"}

##### Error (500)
    {"error": "Server error"}

### GET /group_stats/{group_id}

#### Description
Retrieves statistics for the top NSFW users and the top active users within a specified group.

#### Request Parameters
- group_id (path): The ID of the group.

#### Example Request
`curl -X GET "http://localhost:5000/group_stats/1"`

#### Responses

##### Success (200)
    {"top_nsfw_users": [
        {
            "user_id": 123,
            "username": "user123",
            "nsfw_count": 5
        },
        {
            "user_id": 456,
            "username": "user456",
            "nsfw_count": 3
        }
    ],
    "top_active_users": [
        {
            "user_id": 123,
            "username": "user123",
            "total_messages": 65
        },
        {
            "user_id": 789,
            "username": "user789",
            "total_messages": 50
        }
    ]}

##### Error (500)
    { "error": "Server error" }
### Answers of server:

- _200 OK_: Successful file processing. Returns results depending on the action.
- _201 Created_: Successful creation of a new user account
- _400 Bad Request_: File upload error (e.g. file not found or not selected).
- _404 Not Found_: Server cannot find what was requested: the user is trying to log in with a username that
        does not exist in the database
- _409 Conflict_: Server is trying to register a new user with a username that is already occupied
- _500 Internal Server Error_: Fatal server error when processing a file.

### Code examples

In each case, make sure to replace `path_to_image.jpg` with the actual path to your image
#### 1. **Image censor request using color**:
`import requests, json`

    url = 'http://localhost:5000/censor_colour'
    files = {'file': open('path_to_image.jpg', 'rb')}
    data = {'colour': 'red'}
    response = requests.post(url, files=files, data=data)
    if response.status_code == 200:
        with open('uploads/path_to_image_censored.jpg', 'wb') as f:
            f.write(response.content)
#### 2. **Image censor request**:
    url = 'http://localhost:5000/censor'
    files = {'file': open('path_to_image.jpg', 'rb')}
    response = requests.post(url, files=files)
    if response.status_code == 200:
        with open('uploads/path_to_image_censored.jpg', 'wb') as f:
            f.write(response.content)

#### 3. **Request for image classification**:
    url = 'http://localhost:5000/classify'
    files = {'file': open('path_to_image.jpg', 'rb')}
    response = requests.post(url, files=files)
    if response.status_code == 200:
        print(response.json())  # This will print the classification scores for 'safe' and 'unsafe'


#### 4. **Request to detect objects in the image**:

    url = 'http://localhost:5000/detect'
    files = {'file': open('path_to_image.jpg', 'rb')}
    response = requests.post(url, files=files)
    if response.status_code == 200:
        print(response.json())  # This will print the list of detected parts and their scores

#### 5. **Request for logging a message**:
     url = 'http://localhost:5000/message'
     data = {
    'username': 'user123',
    'user_id': 1,
    'group_id': 2,
    'message': 'This is a sample message',
    'is_text': 1,
    'is_nsfw': 0}
    response = requests.post(url, json=data)
    print(response.json())

#### 6. **Request for getting user statistics**
     url = 'http://localhost:5000/stats/1/123'
     response = requests.get(url)
     print(response.json())

#### 7. **Request for getting group statistics**
     url = 'http://localhost:5000/group_stats/1'
     response = requests.get(url)
     print(response.json())


