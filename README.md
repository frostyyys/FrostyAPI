## API Documentation

### Overview
This API allows users to register, log in, manage licenses, users, and administer various functionalities such as banning, unbanning, and changing user ranks. The system uses `frost_hash` for password security, and it stores information in a SQLite database.

### Authentication
All administrative actions (e.g., deleting users, generating licenses, banning/unbanning users) require an `admin_password`. The admin password must be hashed using the `frost_hash` method before sending it in the request.

### Base URL
```
http://localhost:5000
```

---

### Endpoints

#### User Management

##### **Register**
- **URL**: `/register`
- **Method**: `POST`
- **Description**: Registers a new user.
- **Request Body**:
  ```json
  {
      "username": "string",
      "password": "string",
      "license_key": "string"
  }
  ```
- **Responses**:
  - 200 OK: User registered successfully.
  - 400 Bad Request: Missing required fields or invalid license key.

##### **Login**
- **URL**: `/login`
- **Method**: `POST`
- **Description**: Logs in a user.
- **Request Body**:
  ```json
  {
      "username": "string",
      "password": "string"
  }
  ```
- **Responses**:
  - 200 OK: Login successful.
  - 401 Unauthorized: Incorrect login information.
  - 403 Forbidden: User is banned.

##### **Delete User**
- **URL**: `/delete_user`
- **Method**: `POST`
- **Description**: Deletes a user (admin only).
- **Request Body**:
  ```json
  {
      "admin_password": "string",
      "username": "string"
  }
  ```
- **Responses**:
  - 200 OK: User deleted successfully.
  - 403 Unauthorized: Admin password incorrect.
  - 404 Not Found: User not found.

##### **Change Password**
- **URL**: `/change_password`
- **Method**: `POST`
- **Description**: Changes the password of a user (admin only).
- **Request Body**:
  ```json
  {
      "admin_password": "string",
      "username": "string",
      "new_password": "string"
  }
  ```
- **Responses**:
  - 200 OK: Password updated successfully.
  - 403 Unauthorized: Admin password incorrect.
  - 404 Not Found: User not found.

##### **View Users**
- **URL**: `/users`
- **Method**: `GET`
- **Description**: Retrieves a list of users (admin only).
- **Query Parameters**:
  - `admin_password`: The admin password.
- **Responses**:
  - 200 OK: List of users.
  - 403 Unauthorized: Admin password incorrect.

##### **Ban User**
- **URL**: `/ban_user`
- **Method**: `GET`
- **Description**: Bans a user (admin only).
- **Query Parameters**:
  - `admin_password`: The admin password.
  - `username`: The username to ban.
  - `reason`: The reason for banning the user.
- **Responses**:
  - 200 OK: User banned successfully.
  - 403 Unauthorized: Admin password incorrect.
  - 404 Not Found: User not found.

##### **Unban User**
- **URL**: `/unban_user`
- **Method**: `GET`
- **Description**: Unbans a user (admin only).
- **Query Parameters**:
  - `admin_password`: The admin password.
  - `username`: The username to unban.
- **Responses**:
  - 200 OK: User unbanned successfully.
  - 403 Unauthorized: Admin password incorrect.
  - 404 Not Found: User not found.

---

#### License Management

##### **Generate License**
- **URL**: `/generate_license`
- **Method**: `POST`
- **Description**: Generates a new license key (admin only).
- **Request Body**:
  ```json
  {
      "admin_password": "string",
      "rank": "string"
  }
  ```
- **Responses**:
  - 200 OK: License generated successfully.
  - 403 Unauthorized: Admin password incorrect.

##### **Delete License**
- **URL**: `/delete_license`
- **Method**: `POST`
- **Description**: Deletes a license (admin only).
- **Request Body**:
  ```json
  {
      "admin_password": "string",
      "license_key": "string"
  }
  ```
- **Responses**:
  - 200 OK: License deleted successfully.
  - 403 Unauthorized: Admin password incorrect.
  - 404 Not Found: License not found.

##### **View Licenses**
- **URL**: `/licenses`
- **Method**: `GET`
- **Description**: Retrieves a list of licenses (admin only).
- **Query Parameters**:
  - `admin_password`: The admin password.
- **Responses**:
  - 200 OK: List of licenses.
  - 403 Unauthorized: Admin password incorrect.

##### **Check License**
- **URL**: `/check_license`
- **Method**: `GET`
- **Description**: Checks if a license key is valid (admin only).
- **Query Parameters**:
  - `admin_password`: The admin password.
  - `license_key`: The license key to check.
- **Responses**:
  - 200 OK: License information.
  - 403 Unauthorized: Admin password incorrect.
  - 404 Not Found: License not found.

---

#### User Rank Management

##### **Change Rank**
- **URL**: `/change_rank`
- **Method**: `POST`
- **Description**: Changes the rank of a user (admin only).
- **Request Body**:
  ```json
  {
      "admin_password": "string",
      "username": "string",
      "new_rank": "string"
  }
  ```
- **Responses**:
  - 200 OK: Rank updated successfully.
  - 403 Unauthorized: Admin password incorrect.
  - 404 Not Found: User or license not found.

---

### Error Responses

- **403 Unauthorized**: Admin password incorrect.
- **404 Not Found**: Resource not found (User, License).
- **400 Bad Request**: Missing or invalid request parameters.

---

### Notes

- All administrative routes require the `admin_password` hashed using the `frost_hash` function.
- The system uses a custom `frost_hash` algorithm for password security.
