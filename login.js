// login.js

document.addEventListener('DOMContentLoaded', () => {
    // Check if already logged in
    if (localStorage.getItem('currentUser')) {
        window.location.href = 'index.html';
        return;
    }

    const authForm = document.getElementById('authForm');
    const toggleMode = document.getElementById('toggleMode');
    const toggleText = document.getElementById('toggleText');
    const nameGroup = document.getElementById('nameGroup');
    const authTitle = document.getElementById('authTitle');
    const submitBtn = document.getElementById('submitBtn');
    const alertBox = document.getElementById('alertBox');
    
    let isLoginMode = true;
    
    toggleMode.addEventListener('click', () => {
        isLoginMode = !isLoginMode;
        if (isLoginMode) {
            nameGroup.style.display = 'none';
            authTitle.textContent = 'Welcome Back';
            submitBtn.textContent = 'Sign In';
            toggleText.textContent = "Don't have an account?";
            toggleMode.textContent = 'Sign Up';
        } else {
            nameGroup.style.display = 'block';
            authTitle.textContent = 'Create Account';
            submitBtn.textContent = 'Sign Up';
            toggleText.textContent = 'Already have an account?';
            toggleMode.textContent = 'Sign In';
        }
        alertBox.className = 'alert';
    });

    authForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const name = document.getElementById('name').value;
        
        const endpoint = isLoginMode ? '/api/login' : '/api/signup';
        const payload = isLoginMode ? { email, password } : { email, password, name };
        
        try {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Please wait...';
            
            const response = await fetch(`http://127.0.0.1:5000${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                showAlert(data.error || 'Authentication failed', 'error');
            } else {
                showAlert(data.message, 'success');
                if (isLoginMode) {
                    localStorage.setItem('currentUser', JSON.stringify(data.user));
                    setTimeout(() => { window.location.href = 'index.html'; }, 800);
                } else {
                    // Switch to login mode after successful signup
                    setTimeout(() => {
                        isLoginMode = false;
                        toggleMode.click();
                        document.getElementById('password').value = '';
                    }, 1500);
                }
            }
        } catch (error) {
            showAlert('Could not connect to the server.', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = isLoginMode ? 'Sign In' : 'Sign Up';
        }
    });

    function showAlert(message, type) {
        alertBox.textContent = message;
        alertBox.className = `alert ${type}`;
    }
});
