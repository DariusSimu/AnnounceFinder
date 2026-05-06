from werkzeug.security import generate_password_hash, check_password_hash
from Backend.database import db
from Backend.models_db import User, Favorite, PasswordResetToken
from email.mime.text import MIMEText
import smtplib
import re
import os

try:
    from config import GMAIL_ADDRESS as _GMAIL, GMAIL_PASSWORD as _GMAIL_PASS
except ImportError:
    _GMAIL      = ''
    _GMAIL_PASS = ''

GMAIL_ADDRESS  = os.environ.get('GMAIL_ADDRESS',  _GMAIL)
GMAIL_PASSWORD = os.environ.get('GMAIL_PASSWORD', _GMAIL_PASS)

def is_valid_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) is not None

def register_user(email, password):
    if not is_valid_email(email):
        return None, 'Invalid email address'
    if len(password) < 6:
        return None, 'Password must be at least 6 characters long'
    if User.query.filter_by(email=email).first():
        return None, 'Email already registered'
    user = User(email=email, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    return user, None

def login_user(email, password):
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return None, 'Invalid email or password'
    return user, None

def add_favorite(user_id, data):
    if Favorite.query.filter_by(user_id=user_id, listing_id=data['listing_id']).first():
        return False, 'Already in favorites'
    fav = Favorite(
        user_id    = user_id,
        listing_id = data['listing_id'],
        title      = data['title'],
        platform   = data['platform'],
        price      = data['price'],
        url        = data['url'],
        condition  = data.get('condition', 'NONE'),
        image      = data['image']
    )
    db.session.add(fav)
    db.session.commit()
    return True, None

def remove_favorite(user_id, listing_id):
    fav = Favorite.query.filter_by(user_id=user_id, listing_id=listing_id).first()
    if not fav:
        return False, 'Not in favorites'
    db.session.delete(fav)
    db.session.commit()
    return True, None

def get_favorites(user_id):
    favs = Favorite.query.filter_by(user_id=user_id).order_by(Favorite.id.desc()).all()
    return [{
        'listing_id': f.listing_id,
        'title':      f.title,
        'platform':   f.platform,
        'price':      f.price,
        'url':        f.url,
        'condition':  f.condition,
        'image':      f.image
    } for f in favs]

def send_reset_email(to_email, token, base_url):
    reset_link = f"{base_url}/reset/{token}"
    body = f"""
    You requested a password reset for your AnnounceFinder account.
    
    Click the link below to reset your password (valid for 1 hour):
    {reset_link}
    
    If you did not request this, ignore this email.
    """
    msg = MIMEText(body)
    msg['Subject'] = 'AnnounceFinder — Password Reset'
    msg['From']    = GMAIL_ADDRESS
    msg['To']      = to_email

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
            smtp.sendmail(GMAIL_ADDRESS, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def request_password_reset(email, base_url):
    user = User.query.filter_by(email=email).first()
    if not user:
        return True  # don't reveal if email exists
    token = PasswordResetToken.generate(user.id)
    send_reset_email(email, token, base_url)
    return True

def reset_password(token, new_password):
    reset = PasswordResetToken.query.filter_by(token=token).first()
    if not reset:
        return False, 'Invalid or expired reset link'
    if reset.is_expired():
        db.session.delete(reset)
        db.session.commit()
        return False, 'Reset link has expired'
    if len(new_password) < 6:
        return False, 'Password must be at least 6 characters'
    user = User.query.get(reset.user_id)
    user.password_hash = generate_password_hash(new_password)
    db.session.delete(reset)
    db.session.commit()
    return True, None