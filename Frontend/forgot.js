function showMessage(msg, isError = true) {
    const el = document.getElementById('auth-message');
    el.textContent = msg;
    el.className = 'auth-message ' + (isError ? 'auth-error' : 'auth-success');
}

function isValidEmail(email) {
    return /^[\w\.-]+@[\w\.-]+\.\w+$/.test(email);
}

async function handleForgotPassword() {
    const email = document.getElementById('forgot-email').value.trim();
    if (!isValidEmail(email)) { showMessage('Please enter a valid email address.'); return; }

    await fetch('/forgot-password', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ email })
    });
    showMessage('If that email exists, a reset link has been sent.', false);
}

document.addEventListener('keydown', e => {
    if (e.key === 'Enter') handleForgotPassword();
});