# UAV Authentication System

A secure web-based authentication system for UAV (Unmanned Aerial Vehicle) ground control stations. This system provides user registration, login, session management, and a protected audit platform dashboard.

## Features

- **User Registration**: New users can create accounts with username and password
- **Secure Login**: Authentication with session token management
- **Protected Routes**: Automatic redirection to login page for unauthenticated users
- **Navbar with User Info**: Display logged-in username in the navigation bar
- **Logout Functionality**: Secure session invalidation and redirect to login
- **Session Validation**: Token-based authentication with expiration (24 hours)
- **Responsive Design**: Mobile-friendly interface with modern UI
- **Loading Indicators**: Visual feedback during API calls
- **Error Handling**: Clear error messages for better user experience

## Architecture

### Backend (Python/Flask)
- **GCS_LeaderNode.py**: Main Flask application with REST API endpoints
- **auth_db.py**: Database management for users and sessions (SQLite)

### Frontend (HTML/CSS/JavaScript)
- **login.html**: User login page
- **register.html**: New user registration page
- **audit_platform.html**: Protected main dashboard page
- **app.js**: Frontend authentication logic and API calls
- **styles.css**: Responsive styling for all pages

## API Endpoints

### POST /api/register
Register a new user
- **Request**: `{ "username": "string", "password": "string" }`
- **Response**: `{ "success": boolean, "message": "string" }`

### POST /api/login
Authenticate user and create session
- **Request**: `{ "username": "string", "password": "string" }`
- **Response**: `{ "success": boolean, "message": "string", "token": "string", "username": "string" }`

### POST /api/logout
Logout user and invalidate session
- **Request**: `{ "token": "string" }`
- **Response**: `{ "success": boolean, "message": "string" }`

### POST /api/validate
Validate session token
- **Request**: `{ "token": "string" }`
- **Response**: `{ "success": boolean, "username": "string" }`

### POST /api/cleanup
Remove expired sessions (maintenance endpoint)
- **Response**: `{ "success": boolean, "message": "string" }`

## Installation

1. **Clone the repository**
   ```bash
   cd uav-auth-system
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python GCS_LeaderNode.py
   ```

4. **Access the application**
   Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

### First Time Setup
1. Navigate to `http://localhost:5000` (redirects to login page)
2. Click "Register here" to create a new account
3. Enter a username (minimum 3 characters) and password (minimum 6 characters)
4. Click "Create Account"
5. You'll be redirected to the login page

### Login
1. Enter your username and password
2. Click "Sign In"
3. Upon successful authentication, you'll be redirected to the audit platform dashboard

### Using the Platform
- Your username is displayed in the top-right corner of the navbar
- Navigate between different sections using the navbar links
- Click "Logout" to end your session and return to the login page

### Security Features
- Passwords are hashed using SHA-256 before storage
- Session tokens are generated using cryptographically secure random functions
- Sessions expire after 24 hours
- Tokens are validated on each request to protected pages
- Expired sessions are automatically cleaned up

## Development

### Project Structure
```
uav-auth-system/
├── GCS_LeaderNode.py      # Flask backend API
├── auth_db.py             # Database management
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── static/               # Frontend files
    ├── login.html        # Login page
    ├── register.html     # Registration page
    ├── audit_platform.html # Main dashboard
    ├── app.js           # Frontend JavaScript
    └── styles.css       # Styling
```

### Database Schema

**users table**
- `id`: INTEGER PRIMARY KEY
- `username`: TEXT UNIQUE NOT NULL
- `password_hash`: TEXT NOT NULL
- `created_at`: TIMESTAMP

**sessions table**
- `id`: INTEGER PRIMARY KEY
- `user_id`: INTEGER (foreign key to users.id)
- `token`: TEXT UNIQUE NOT NULL
- `created_at`: TIMESTAMP
- `expires_at`: TIMESTAMP

## Testing

### Manual Testing Scenarios

1. **Registration Flow**
   - Try registering with short username (< 3 chars) - should show error
   - Try registering with short password (< 6 chars) - should show error
   - Try mismatched passwords - should show error
   - Register successfully with valid credentials

2. **Login Flow**
   - Try logging in with non-existent username - should show error
   - Try logging in with wrong password - should show error
   - Login successfully with valid credentials
   - Verify redirect to audit platform

3. **Session Management**
   - Verify username appears in navbar after login
   - Try accessing audit platform without login - should redirect to login
   - Try accessing login page when already logged in - should redirect to audit platform
   - Click logout and verify redirect to login page

4. **Multiple Users**
   - Register and login with multiple different users
   - Verify each user sees their own username in navbar

## Security Considerations

### Current Implementation
- **Password Hashing**: Passwords are hashed using SHA-256 before storage
- **Session Tokens**: Cryptographically secure random tokens (32 bytes, URL-safe)
- **Session Expiration**: Automatic cleanup of expired sessions (24 hours)
- **Input Validation**: Both client-side and server-side validation
- **Error Messages**: Generic error messages to prevent user enumeration
- **CORS**: Configured for secure cross-origin requests

### Important Security Notes

⚠️ **This is a development/educational implementation. For production use, consider the following improvements:**

1. **Password Hashing**: 
   - Current: SHA-256 (vulnerable to rainbow table attacks)
   - Recommended: Use `bcrypt`, `scrypt`, or `argon2` with salt
   - Example: `pip install bcrypt` and use `bcrypt.hashpw()`

2. **Token Storage**:
   - Current: localStorage (vulnerable to XSS attacks)
   - Recommended: Use httpOnly cookies for storing tokens
   - Alternative: Use sessionStorage for slightly better security

3. **Debug Mode**:
   - Current: Flask runs with `debug=True` for development
   - Production: Set `debug=False` and use a production WSGI server like Gunicorn

4. **HTTPS**:
   - Always use HTTPS in production to encrypt data in transit
   - Obtain SSL/TLS certificates (Let's Encrypt is free)

5. **Additional Security Measures**:
   - Implement rate limiting to prevent brute force attacks
   - Add CSRF protection for form submissions
   - Use environment variables for sensitive configuration
   - Implement password complexity requirements
   - Add account lockout after failed login attempts
   - Enable security headers (CSP, HSTS, X-Frame-Options)

## Future Enhancements

- Role-based access control (RBAC)
- Password reset functionality
- Two-factor authentication (2FA)
- Remember me option
- User profile management
- Activity logging and audit trails
- Integration with LDAP/Active Directory
- Rate limiting for API endpoints
- HTTPS/TLS encryption

## License

This project is provided as-is for educational and development purposes.

## Author

Muntasir Mamun
