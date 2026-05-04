from werkzeug.security import generate_password_hash, check_password_hash
from Backend.database import db
from Backend.models_db import User, Favorite
from Backend.encryption import encrypt, decrypt
import re

def is_valid_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) is not None

def register_user(email, password):
    if not is_valid_email(email):
        return None, 'Invalid email address'
    if len(password) < 6:
        return None, 'Password must be at least 6 characters long'
    if User.query.filter_by(email=encrypt(email)).first():
        return None, 'Email already registered'
    user = User(
        email         = encrypt(email),
        password_hash = generate_password_hash(password)
    )
    db.session.add(user)
    db.session.commit()
    return user, None

def login_user(email, password):
    user = User.query.filter_by(email=encrypt(email)).first()
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