function showMessage(msg, isError = true) {
    const el = document.getElementById('auth-message');
    el.textContent = msg;
    el.className = 'auth-message ' + (isError ? 'auth-error' : 'auth-success');
}

async function handleReset() {
    const password = document.getElementById('new-password').value;
    const confirm  = document.getElementById('confirm-password').value;
    const token    = window.location.pathname.split('/').pop();

    if (password.length < 6) { showMessage('Password must be at least 6 characters.'); return; }
    if (password !== confirm) { showMessage('Passwords do not match.'); return; }

    const res  = await fetch(`/reset/${token}`, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ password })
    });
    const data = await res.json();

    if (data.success) {
        showMessage('Password reset! Redirecting...', false);
        setTimeout(() => window.location.href = '/login', 1500);
    } else {
        showMessage(data.error);
    }
}