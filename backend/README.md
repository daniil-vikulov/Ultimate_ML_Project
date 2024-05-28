## Documentation for the image processing API

### General description

This API provides functionality for uploading images and performing various processing operations such as censorship,
classification, and detection of objects in an image. The API is implemented in Flask and uses various internal
functions for image processing.
The main server code is in the file `src/app/app.py`

### The main components

1. **`upload_file(action)`** is the main API entry point that processes uploaded files and delegates them for processing
   depending on the specified action.

2. **`sensor_image(filepath)`** is a function for censoring images.

3. **`classify_image(filepath)`** is a function for classifying images based on content.

4. **`detect_image(filepath)`** is a function for detecting objects in an image.

### Answers of server:

- _200 OK_: Successful file processing. Returns results depending on the action.
- _201 Created_: Successful creation of a new user account
- _400 Bad Request_: File upload error (e.g. file not found or not selected).
- _404 Not Found_: Server cannot find what was requested: the user is trying to log in with a username that
        does not exist in the database
- _409 Conflict_: Server is trying to register a new user with a username that is already occupied
- _500 Internal Server Error_: Fatal server error when processing a file.

### Usage examples in terminal

Enter commands in terminal.
For items 1-3, you need to upload the image to the folder `src/app/uploads` (it will be created automatically when the server starts).
The censored images will appear there too.

* If you are in the folder `uploads` , then just write the name of the uploaded file instead of `path_to_image`

#### 1. **Image censor request**:
   `curl -X POST -F "file=@path_to_image.jpg" http://localhost:5000/censor`

   **Return**: the censored image to the folder `uploads` by appending to the file name `_censored`

#### 2. **Request for image classification**:
   `curl -X POST -F "file=@path_to_image.jpg" http://localhost:5000/classify`

   **Return**: classification scores for _safe_ and _unsafe_

#### 3. **Request to detect objects in the image**:
   `curl -X POST -F "file=@path_to_image.jpg" http://localhost:5000/detect`

   **Return**: list of detected parts and their scores

- Enter the name of user instead of `new_user`

#### 4. **Request to registrate user**:
   `curl -X POST http://localhost:5000/register -H "Content-Type: application/json" -d "{\"username\": \"new_user\"}"`

   **Return**: _User registered successfully_ if this username is unique or _Username already exists_ and then you need
   to change the username

#### 5. **Request to login user**:
   `curl -X POST http://localhost:5000/login -H "Content-Type: application/json" -d "{\"username\": \"new_user\"}"`

   **Return**: _Login successful_ if this username exists or _User not found_ if it doesn't exist

### Usage examples in code

#### 1. **Image censor request using Python**:

`import requests, json`

    url = 'http://localhost:5000/censor'
    files = {'file': open('path_to_image.jpg', 'rb')}
    response = requests.post(url, files=files)
    if response.status_code == 200:
        with open('uploads/path_to_image_censored.jpg', 'wb') as f:
            f.write(response.content)

#### 2. **Request for image classification using Python**:

    url = 'http://localhost:5000/classify'
    files = {'file': open('path_to_image.jpg', 'rb')}
    response = requests.post(url, files=files)
    if response.status_code == 200:
        print(response.json())  # This will print the classification scores for 'safe' and 'unsafe'


#### 3. **Request to detect objects in the image using Python**:

    url = 'http://localhost:5000/detect'
    files = {'file': open('path_to_image.jpg', 'rb')}
    response = requests.post(url, files=files)
    if response.status_code == 200:
        print(response.json())  # This will print the list of detected parts and their scores


#### 4. **Request to register a user using Python**:

    url = 'http://localhost:5000/register'
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({"username": "new_user"})  # Replace 'new_user' with the desired username
    response = requests.post(url, headers=headers, data=data)
    print(response.text)  # This will print 'User registered successfully' or 'Username already exists'


#### 5. **Request to login a user using Python**:

    url = 'http://localhost:5000/login'
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({"username": "new_user"})  # Replace 'new_user' with the desired username
    response = requests.post(url, headers=headers, data=data)
    print(response.text)  # This will print 'Login successful' or 'User not found'


In each case, make sure to replace `path_to_image.jpg` with the actual path to your image and `new_user` with the actual
username you intend to use for registration and login.

