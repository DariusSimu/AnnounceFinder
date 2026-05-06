from flask import Flask, request, jsonify, send_from_directory
from flask_login import LoginManager, login_user, logout_user, current_user
from Backend.main_crawler import search_all
from Backend.database import db
from Backend.models_db import User
from Backend.services import register_user, login_user as login_user_service, add_favorite, remove_favorite, get_favorites, request_password_reset, reset_password
import os

app = Flask(__name__)
database_url = os.environ.get('DATABASE_URL', 'sqlite:///announcefinder.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

try:
    from config import SECRET_KEY as _SECRET_KEY
except ImportError:
    _SECRET_KEY = ''

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', _SECRET_KEY)


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

@app.route('/reset.js')
def reset_js():
    return send_from_directory('Frontend', 'reset.js')

@app.route('/forgot.js')
def forgot_js():
    return send_from_directory('Frontend', 'forgot.js')

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

@app.route('/forgot-password')
def forgot_page():
    return send_from_directory('Frontend', 'ForgotPage.html')

@app.route('/reset/<token>')
def reset_page(token):
    return send_from_directory('Frontend', 'ResetPage.html')

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
        return jsonify({'logged_in': True, 'email': current_user.email})
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

# ------------- Password Reset --------------
@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    data  = request.get_json()
    email = data.get('email', '').strip()
    base_url = request.host_url.rstrip('/')
    request_password_reset(email, base_url)
    return jsonify({'success': True})

@app.route('/reset/<token>', methods=['POST'])
def reset_password_route(token):
    try:
        data     = request.get_json()
        password = data.get('password', '')
        success, error = reset_password(token, password)
        if not success:
            return jsonify({'error': error}), 400
        return jsonify({'success': True})
    except Exception as e:
        print(f"Reset error: {e}")
        return jsonify({'error': 'Something went wrong'}), 500
    
# ------------- Exchange Rates --------------
@app.route('/exchange-rates')
def exchange_rates():
    import requests as req
    try:
        res  = req.get('https://api.frankfurter.app/latest?from=EUR&to=RON,GBP', timeout=5)
        return jsonify(res.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)