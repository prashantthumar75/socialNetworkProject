# Social Network Project

## Introduction
This project contains two Django applications:

- **authentication:** an API for user signup, login, and authentication
- **socialApp:** an API for sending/accepting/rejecting friend requests, searching users, and listing friends

## Installation

### Using Docker
To install the project using Docker, follow these steps:

1. Build the Docker image:
    ```
    docker build -t socialnetwork .
    ```

2. Start the Docker container:
    ```
    docker-compose up
    ```

### Using a Virtual Environment
To install the project using a virtual environment, follow these steps:

1. Create a virtual environment:
    ```
    python -m venv env
    ```

2. Activate the virtual environment:
    - On Windows:
        ```
        .\env\Scripts\activate
        ```
    - On Mac/Linux:
        ```
        source env/bin/activate
        ```

3. Install the required packages:
    ```
    pip install -r requirements.txt
    ```

4. Run the project:
    ```
    python manage.py runserver
    ```

## Usage

### Authentication
To authenticate, you can use the following API endpoints:
- (POST) `{{url}}/api/auth/signup/`: Sign up using name, email, and password
- (POST) `{{url}}/api/auth/login/`: Log in using email and password

Note: Authentication is done using JWT tokens. To authenticate, you should obtain a token by logging in and then provide the token in the Authorization header of subsequent requests as a Bearer Token.

### Social Requests
The following API endpoints require authentication:

- (GET) `{{url}}/api/social/users/?search=am`: Search for users in the social network
- (POST) `{{url}}/api/social/friend-requests/send/`: Send a friend request to a user (pass the receiver ID in the request)
- (GET) `{{url}}/api/social/friend-requests/pending/`: List pending friend requests
- (PATCH) `{{url}}/api/social/friend-requests/<id>/accept/`: Accept a friend request with ID `<id>`
- (PATCH) `{{url}}/api/social/friend-requests/<id>/reject/`: Reject a friend request with ID `<id>`
- (GET) `{{url}}/api/social/friends/`: List your friends

Note: In the above URLs, `{{url}}` should be replaced with the URL of the running server (e.g. `http://127.0.0.1:8000`).

That's it! You should now be able to use the API to manage your social network.
