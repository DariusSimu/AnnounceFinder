from flask import Flask, request, jsonify, send_from_directory
from flask_login import LoginManager, login_user, logout_user, current_user
from Backend.main_crawler import search_all
from Backend.database import db
from Backend.models_db import User
from Backend.services import register_user, login_user as login_user_service, add_favorite, remove_favorite, get_favorites
from config import SECRET_KEY, ENCRYPTION_KEY
from Backend.encryption import decrypt
import os

app = Flask(__name__)
database_url = os.environ.get('DATABASE_URL', 'sqlite:///announcefinder.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', SECRET_KEY)
app.config['ENCRYPTION_KEY']  = os.environ.get('ENCRYPTION_KEY', ENCRYPTION_KEY)


db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

# --------------- JavaScript -------------------
@app.route('/main.js')
def main_js():
    return send_from_directory('Frontend', 'main.js')

@app.route('/account.js')
def account_js():
    return send_from_directory('Frontend', 'account.js')

@app.route('/login.js')
def login_js():
    return send_from_directory('Frontend', 'login.js')

@app.route('/filter.js')
def filter_js():
    return send_from_directory('Frontend', 'filter.js')

# --------------- Pages -------------------
@app.route('/')
def index():
    return send_from_directory('Frontend', 'MainPage.html')

@app.route('/login')
def login_page():
    return send_from_directory('Frontend', 'LoginPage.html')

@app.route('/favorites')
def favorites_page():
    return send_from_directory('Frontend', 'AccountPage.html')

@app.route('/Style.css')
def styles():
    return send_from_directory('Frontend', 'Style.css')

# --------------- Search -------------------
@app.route('/search')
def search():
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 10))
    if not query:
        return jsonify([])
    results = search_all(query, limit)
    return jsonify([r.__dict__ for r in results])

# -------------- Authentication --------------
@app.route('/register', methods=['POST'])
def register():
    data           = request.get_json()
    user, error    = register_user(data.get('email', '').strip(), data.get('password', ''))
    if error:
        return jsonify({'error': error}), 400
    login_user(user)
    return jsonify({'success': True})

@app.route('/login', methods=['POST'])
def login():
    data           = request.get_json()
    user, error    = login_user_service(data.get('email', '').strip(), data.get('password', ''))
    if error:
        return jsonify({'error': error}), 401
    login_user(user)
    return jsonify({'success': True})

@app.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({'success': True})

@app.route('/me')
def me():
    if current_user.is_authenticated:
        return jsonify({'logged_in': True, 'email': decrypt(current_user.email)})
    return jsonify({'logged_in': False})

# ------------- Favorites --------------
@app.route('/favorites/add', methods=['POST'])
def fav_add():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Not logged in'}), 401
    success, error = add_favorite(current_user.id, request.get_json())
    if error:
        return jsonify({'error': error}), 400
    return jsonify({'success': True})

@app.route('/favorites/remove', methods=['POST'])
def fav_remove():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Not logged in'}), 401
    success, error = remove_favorite(current_user.id, request.get_json()['listing_id'])
    if error:
        return jsonify({'error': error}), 404
    return jsonify({'success': True})

@app.route('/favorites/get')
def fav_get():
    if not current_user.is_authenticated:
        return jsonify({'error': 'Not logged in'}), 401
    return jsonify(get_favorites(current_user.id))

if __name__ == '__main__':
    app.run(debug=True)