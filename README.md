# FrostyAuth API Documentation

## Base URL

All endpoints are available at `http://localhost:5000`.

## Authentication

For routes requiring admin access, provide the `admin_password` parameter as a POST body or query parameter. The password must be hashed using the `frost_hash` function.

## Endpoints

### User Management

#### Register User

- **Endpoint**: `/register`
- **Method**: POST
- **Description**: Registers a new user with a username, password, and license key.
- **Request Body**:
    ```json
    {
      "username": "string",
      "password": "string",
      "license_key": "string"
    }
    ```
- **Responses**:
  - **200 OK**:
    ```json
    {
      "message": "User registered successfully!",
      "rank": "string"
    }
    ```
  - **400 Bad Request**:
    ```json
    {
      "error": "Username, password, and license key are required"
    }
    ```
  - **401 Unauthorized**:
    ```json
    {
      "error": "Incorrect login information"
    }
    ```

#### Login

- **Endpoint**: `/login`
- **Method**: POST
- **Description**: Logs in a user, updating their last login details.
- **Request Body**:
    ```json
    {
      "username": "string",
      "password": "string"
    }
    ```
- **Responses**:
  - **200 OK**:
    ```json
    {
      "message": "Login successful",
      "last_login_ip": "string",
      "last_login_time": "ISO 8601 date-time string"
    }
    ```
  - **401 Unauthorized**:
    ```json
    {
      "error": "Incorrect login information"
    }
    ```
  - **403 Forbidden**:
    ```json
    {
      "error": "User is banned: reason"
    }
    ```

#### Delete User

- **Endpoint**: `/delete_user`
- **Method**: POST
- **Description**: Deletes a user.
- **Request Body**:
    ```json
    {
      "admin_password": "string",
      "username": "string"
    }
    ```
- **Responses**:
  - **200 OK**:
    ```json
    {
      "message": "User username deleted successfully"
    }
    ```
  - **403 Forbidden**:
    ```json
    {
      "message": "Unauthorized"
    }
    ```
  - **404 Not Found**:
    ```json
    {
      "message": "User not found"
    }
    ```

#### Change Password

- **Endpoint**: `/change_password`
- **Method**: POST
- **Description**: Changes a user's password.
- **Request Body**:
    ```json
    {
      "admin_password": "string",
      "username": "string",
      "new_password": "string"
    }
    ```
- **Responses**:
  - **200 OK**:
    ```json
    {
      "message": "Password for username updated successfully"
    }
    ```
  - **403 Forbidden**:
    ```json
    {
      "message": "Unauthorized"
    }
    ```
  - **404 Not Found**:
    ```json
    {
      "message": "User not found"
    }
    ```

#### Change Rank

- **Endpoint**: `/change_rank`
- **Method**: POST
- **Description**: Changes the rank of a user's license.
- **Request Body**:
    ```json
    {
      "admin_password": "string",
      "username": "string",
      "new_rank": "string"
    }
    ```
- **Responses**:
  - **200 OK**:
    ```json
    {
      "message": "Rank for username changed to new_rank successfully"
    }
    ```
  - **403 Forbidden**:
    ```json
    {
      "message": "Unauthorized"
    }
    ```
  - **404 Not Found**:
    ```json
    {
      "message": "User or license not found"
    }
    ```

### License Management

#### Generate License Key

- **Endpoint**: `/generate_license`
- **Method**: POST
- **Description**: Generates a new license key.
- **Request Body**:
    ```json
    {
      "admin_password": "string",
      "rank": "string"
    }
    ```
- **Responses**:
  - **200 OK**:
    ```json
    {
      "license_key": "string",
      "rank": "string"
    }
    ```
  - **403 Forbidden**:
    ```json
    {
      "message": "Unauthorized"
    }
    ```

#### Check License Validity

- **Endpoint**: `/check_license`
- **Method**: GET
- **Description**: Checks if a license key is valid.
- **Query Parameters**:
  - `admin_password`: Admin password (hashed).
  - `license_key`: License key to check.
- **Responses**:
  - **200 OK**:
    ```json
    {
      "license_key": "string",
      "is_used": true/false,
      "rank": "string"
    }
    ```
  - **403 Forbidden**:
    ```json
    {
      "message": "Unauthorized"
    }
    ```
  - **404 Not Found**:
    ```json
    {
      "message": "License not found"
    }
    ```

#### Delete License

- **Endpoint**: `/delete_license`
- **Method**: POST
- **Description**: Deletes a license key.
- **Request Body**:
    ```json
    {
      "admin_password": "string",
      "license_key": "string"
    }
    ```
- **Responses**:
  - **200 OK**:
    ```json
    {
      "message": "License license_key deleted successfully"
    }
    ```
  - **403 Forbidden**:
    ```json
    {
      "message": "Unauthorized"
    }
    ```
  - **404 Not Found**:
    ```json
    {
      "message": "License not found"
    }
    ```

### User and License Viewing

#### View All Users

- **Endpoint**: `/users`
- **Method**: GET
- **Description**: Retrieves a list of all users.
- **Query Parameters**:
  - `admin_password`: Admin password (hashed).
- **Responses**:
  - **200 OK**:
    ```json
    {
      "users": [
        {
          "username": "string",
          "license_used": "string",
          "banned": true/false,
          "ban_reason": "string",
          "last_login_ip": "string",
          "last_login_time": "ISO 8601 date-time string"
        }
      ]
    }
    ```
  - **403 Forbidden**:
    ```json
    {
      "message": "Unauthorized"
    }
    ```

#### View All Licenses

- **Endpoint**: `/licenses`
- **Method**: GET
- **Description**: Retrieves a list of all licenses.
- **Query Parameters**:
  - `admin_password`: Admin password (hashed).
- **Responses**:
  - **200 OK**:
    ```json
    {
      "licenses": [
        {
          "key": "string",
          "is_used": true/false,
          "rank": "string"
        }
      ]
    }
    ```
  - **403 Forbidden**:
    ```json
    {
      "message": "Unauthorized"
    }
    ```

### Ban and Unban Users

#### Ban User

- **Endpoint**: `/ban_user`
- **Method**: GET
- **Description**: Bans a user.
- **Query Parameters**:
  - `admin_password`: Admin password (hashed).
  - `username`: Username to ban.
  - `reason`: Reason for banning.
- **Responses**:
  - **200 OK**:
    ```json
    {
      "message": "User username has been banned for: reason"
    }
    ```
  - **403 Forbidden**:
    ```json
    {
      "message": "Unauthorized"
    }
    ```
  - **404 Not Found**:
    ```json
    {
      "message": "User not found"
    }
    ```

#### Unban User

- **Endpoint**: `/unban_user`
- **Method**: GET
- **Description**: Unbans a user.
- **Query Parameters**:
  - `admin_password`: Admin password (hashed).
  - `username`: Username to unban.
- **Responses**:
  - **200 OK**:
    ```json
    {
      "message": "User username has been unbanned"
    }
    ```
  - **403 Forbidden**:
    ```json
    {
      "message": "Unauthorized"
    }
    ```
  - **404 Not Found**:
    ```json
    {
      "message": "User not found"
    }
    ```

---
