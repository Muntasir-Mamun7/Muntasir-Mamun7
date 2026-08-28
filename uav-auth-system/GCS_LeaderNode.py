"""
GCS Leader Node - Backend API for UAV Authentication System
Provides REST API endpoints for user authentication
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from auth_db import AuthDB

app = Flask(__name__, static_folder='static')
CORS(app)

# Initialize database
db = AuthDB('uav_auth.db')

@app.route('/')
def index():
    """Serve the login page by default"""
    return send_from_directory('static', 'login.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('static', path)

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        if len(username) < 3:
            return jsonify({
                'success': False,
                'message': 'Username must be at least 3 characters'
            }), 400
        
        if len(password) < 6:
            return jsonify({
                'success': False,
                'message': 'Password must be at least 6 characters'
            }), 400
        
        # Register user
        success, result = db.register_user(username, password)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Registration successful'
            }), 201
        else:
            # Only expose specific known error messages, nothing else
            if result == "Username already exists":
                error_message = "Username already exists"
            else:
                error_message = "Registration failed. Please try again."
            return jsonify({
                'success': False,
                'message': error_message
            }), 400
            
    except Exception as e:
        # Log the error internally but don't expose stack trace to user
        print(f'Registration error: {str(e)}')  # Log for debugging
        return jsonify({
            'success': False,
            'message': 'An error occurred during registration. Please try again.'
        }), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Authenticate user and create session"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        # Authenticate user
        success, result = db.authenticate_user(username, password)
        
        if success:
            # Create session
            user_id = result['id']
            username = result['username']
            token = db.create_session(user_id)
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'token': token,
                'username': username
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result
            }), 401
            
    except Exception as e:
        # Log the error internally but don't expose stack trace to user
        print(f'Login error: {str(e)}')  # Log for debugging
        return jsonify({
            'success': False,
            'message': 'An error occurred during login. Please try again.'
        }), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout user and invalidate session"""
    try:
        data = request.get_json()
        token = data.get('token', '')
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Token is required'
            }), 400
        
        # Invalidate session
        db.invalidate_session(token)
        
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        }), 200
            
    except Exception as e:
        # Log the error internally but don't expose stack trace to user
        print(f'Logout error: {str(e)}')  # Log for debugging
        return jsonify({
            'success': False,
            'message': 'An error occurred during logout. Please try again.'
        }), 500

@app.route('/api/validate', methods=['POST'])
def validate():
    """Validate session token"""
    try:
        data = request.get_json()
        token = data.get('token', '')
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'Token is required'
            }), 400
        
        # Validate session
        success, result = db.validate_session(token)
        
        if success:
            return jsonify({
                'success': True,
                'username': result['username']
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result
            }), 401
            
    except Exception as e:
        # Log the error internally but don't expose stack trace to user
        print(f'Validation error: {str(e)}')  # Log for debugging
        return jsonify({
            'success': False,
            'message': 'An error occurred during validation. Please try again.'
        }), 500

@app.route('/api/cleanup', methods=['POST'])
def cleanup():
    """Cleanup expired sessions (admin endpoint)"""
    try:
        db.cleanup_expired_sessions()
        return jsonify({
            'success': True,
            'message': 'Cleanup completed'
        }), 200
    except Exception as e:
        # Log the error internally but don't expose stack trace to user
        print(f'Cleanup error: {str(e)}')  # Log for debugging
        return jsonify({
            'success': False,
            'message': 'An error occurred during cleanup. Please try again.'
        }), 500

if __name__ == '__main__':
    # Ensure static directory exists
    os.makedirs('static', exist_ok=True)
    
    # Run the Flask server
    # NOTE: debug=True is for development only. In production:
    # 1. Set debug=False
    # 2. Use a production WSGI server like Gunicorn or uWSGI
    # 3. Enable HTTPS with SSL/TLS certificates
    app.run(host='0.0.0.0', port=5000, debug=True)
