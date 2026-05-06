function switchTab(tab) {
    document.getElementById('form-login').style.display    = tab === 'login'    ? 'block' : 'none';
    document.getElementById('form-register').style.display = tab === 'register' ? 'block' : 'none';
    document.getElementById('tab-login').classList.toggle('active',    tab === 'login');
    document.getElementById('tab-register').classList.toggle('active', tab === 'register');
    clearMessage();
}

function showMessage(msg, isError = true) {
    const el      = document.getElementById('auth-message');
    el.textContent = msg;
    el.className   = 'auth-message ' + (isError ? 'auth-error' : 'auth-success');
}

function clearMessage() {
    const el      = document.getElementById('auth-message');
    el.textContent = '';
    el.className   = 'auth-message';
}

function isValidEmail(email) {
    return /^[\w\.-]+@[\w\.-]+\.\w+$/.test(email);
}

async function handleLogin() {
    const email    = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value;

    if (!isValidEmail(email)) { showMessage('Please enter a valid email address.'); return; }
    if (!password)             { showMessage('Please enter your password.');         return; }

    const res  = await fetch('/login', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ email, password })
    });
    const data = await res.json();

    if (data.success) {
        window.location.href = '/';
    } else {
        showMessage(data.error);
    }
}

async function handleRegister() {
    const email    = document.getElementById('register-email').value.trim();
    const password = document.getElementById('register-password').value;
    const confirm  = document.getElementById('register-confirm').value;

    if (!isValidEmail(email))  { showMessage('Please enter a valid email address.');      return; }
    if (password.length < 6)   { showMessage('Password must be at least 6 characters.'); return; }
    if (password !== confirm)  { showMessage('Passwords do not match.');                  return; }

    const res  = await fetch('/register', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ email, password })
    });
    const data = await res.json();

    if (data.success) {
        showMessage('Account created! Redirecting...', false);
        setTimeout(() => window.location.href = '/', 1000);
    } else {
        showMessage(data.error);
    }
}

async function handleForgotPassword() {
    const email = document.getElementById('login-email').value.trim();
    if (!email) { showMessage('Enter your email first.'); return; }
    
    await fetch('/forgot-password', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ email })
    });
    showMessage('If that email exists, a reset link has been sent.', false);
}

document.addEventListener('keydown', e => {
    if (e.key !== 'Enter') return;
    const activeTab = document.getElementById('tab-login').classList.contains('active');
    if (activeTab) handleLogin();
    else handleRegister();
});