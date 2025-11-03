// UAV Authentication System - Frontend JavaScript
// Handles authentication, session management, and UI interactions

const API_BASE_URL = window.location.origin;

// Auth utility functions
const auth = {
    // Get token from localStorage
    getToken() {
        return localStorage.getItem('authToken');
    },

    // Get username from localStorage
    getUsername() {
        return localStorage.getItem('username');
    },

    // Set auth data in localStorage
    setAuth(token, username) {
        localStorage.setItem('authToken', token);
        localStorage.setItem('username', username);
    },

    // Clear auth data from localStorage
    clearAuth() {
        localStorage.removeItem('authToken');
        localStorage.removeItem('username');
    },

    // Check if user is authenticated
    isAuthenticated() {
        return !!this.getToken();
    }
};

// UI utility functions
const ui = {
    // Show loading spinner
    showLoading(button) {
        button.disabled = true;
        const originalText = button.textContent;
        button.dataset.originalText = originalText;
        button.innerHTML = '<span class="spinner"></span>' + originalText;
    },

    // Hide loading spinner
    hideLoading(button) {
        button.disabled = false;
        button.textContent = button.dataset.originalText;
    },

    // Show message
    showMessage(elementId, message, isError = false) {
        const messageEl = document.getElementById(elementId);
        if (messageEl) {
            messageEl.textContent = message;
            messageEl.className = 'message show ' + (isError ? 'message-error' : 'message-success');
        }
    },

    // Hide message
    hideMessage(elementId) {
        const messageEl = document.getElementById(elementId);
        if (messageEl) {
            messageEl.className = 'message';
        }
    }
};

// API functions
const api = {
    // Register new user
    async register(username, password) {
        const response = await fetch(`${API_BASE_URL}/api/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        return await response.json();
    },

    // Login user
    async login(username, password) {
        const response = await fetch(`${API_BASE_URL}/api/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        return await response.json();
    },

    // Logout user
    async logout(token) {
        const response = await fetch(`${API_BASE_URL}/api/logout`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token })
        });
        return await response.json();
    },

    // Validate session
    async validate(token) {
        const response = await fetch(`${API_BASE_URL}/api/validate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ token })
        });
        return await response.json();
    }
};

// Authentication guard - redirect to login if not authenticated
function requireAuth() {
    if (!auth.isAuthenticated()) {
        window.location.href = '/login.html';
        return false;
    }
    return true;
}

// Prevent access to auth pages if already authenticated
function preventAuthPageAccess() {
    if (auth.isAuthenticated()) {
        window.location.href = '/audit_platform.html';
        return false;
    }
    return true;
}

// Initialize navbar with username and logout button
function initNavbar() {
    const username = auth.getUsername();
    const userNameEl = document.getElementById('userName');

    if (userNameEl && username) {
        userNameEl.textContent = username;
    }
}

// Handle logout
async function handleLogout(event) {
    // Prevent default if called from event
    if (event) {
        event.preventDefault();
    }
    
    const token = auth.getToken();
    const logoutBtn = document.getElementById('logoutBtn');

    try {
        if (logoutBtn) {
            ui.showLoading(logoutBtn);
        }
        
        // Call logout API
        const result = await api.logout(token);
        
        // Clear auth data
        auth.clearAuth();
        
        // Redirect to login
        window.location.href = '/login.html';
    } catch (error) {
        console.error('Logout error:', error);
        // Clear auth data even on error
        auth.clearAuth();
        window.location.href = '/login.html';
    }
}

// Handle login form submission
async function handleLogin(event) {
    event.preventDefault();

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const submitBtn = event.target.querySelector('button[type="submit"]');

    ui.hideMessage('message');

    // Validation
    if (!username || !password) {
        ui.showMessage('message', 'Please enter username and password', true);
        return;
    }

    try {
        ui.showLoading(submitBtn);

        const result = await api.login(username, password);

        if (result.success) {
            // Save auth data
            auth.setAuth(result.token, result.username);
            
            // Show success message briefly
            ui.showMessage('message', 'Login successful! Redirecting...', false);
            
            // Redirect to audit platform
            setTimeout(() => {
                window.location.href = '/audit_platform.html';
            }, 500);
        } else {
            ui.showMessage('message', result.message, true);
            ui.hideLoading(submitBtn);
        }
    } catch (error) {
        console.error('Login error:', error);
        ui.showMessage('message', 'Network error. Please try again.', true);
        ui.hideLoading(submitBtn);
    }
}

// Handle registration form submission
async function handleRegister(event) {
    event.preventDefault();

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const submitBtn = event.target.querySelector('button[type="submit"]');

    ui.hideMessage('message');

    // Validation
    if (!username || !password || !confirmPassword) {
        ui.showMessage('message', 'Please fill in all fields', true);
        return;
    }

    if (username.length < 3) {
        ui.showMessage('message', 'Username must be at least 3 characters', true);
        return;
    }

    if (password.length < 6) {
        ui.showMessage('message', 'Password must be at least 6 characters', true);
        return;
    }

    if (password !== confirmPassword) {
        ui.showMessage('message', 'Passwords do not match', true);
        return;
    }

    try {
        ui.showLoading(submitBtn);

        const result = await api.register(username, password);

        if (result.success) {
            ui.showMessage('message', 'Registration successful! Redirecting to login...', false);
            
            // Redirect to login page
            setTimeout(() => {
                window.location.href = '/login.html';
            }, 1500);
        } else {
            ui.showMessage('message', result.message, true);
            ui.hideLoading(submitBtn);
        }
    } catch (error) {
        console.error('Registration error:', error);
        ui.showMessage('message', 'Network error. Please try again.', true);
        ui.hideLoading(submitBtn);
    }
}

// Validate session on page load for authenticated pages
async function validateSession() {
    const token = auth.getToken();
    
    if (!token) {
        window.location.href = '/login.html';
        return;
    }

    try {
        const result = await api.validate(token);
        
        if (!result.success) {
            // Session invalid or expired
            auth.clearAuth();
            window.location.href = '/login.html';
        }
    } catch (error) {
        console.error('Session validation error:', error);
        auth.clearAuth();
        window.location.href = '/login.html';
    }
}
