import jwt
import bcrypt
import html
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# ========== Base Configuration ==========
app.config['SECRET_KEY'] = 'your-jwt-secret-key-2024-work1'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ========== Database Model (ORM prevents SQL Injection natively) ==========
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            # XSS Protection: escape HTML special characters in output
            "username": html.escape(self.username)
        }

# Initialize database tables
with app.app_context():
    db.create_all()

# ========== JWT Authentication Middleware ==========
def token_required(f):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing authentication token"}), 401
        
        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(payload['user_id'])
            if not current_user:
                return jsonify({"error": "User does not exist"}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except Exception:
            return jsonify({"error": "Invalid token"}), 401
        
        return f(current_user, *args, **kwargs)
    
    wrapper.__name__ = f.__name__
    return wrapper

# ========== Endpoint 1: User Registration ==========
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Username and password cannot be empty"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400
    
    # Password hashing: bcrypt with salt, never store plaintext passwords
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    new_user = User(username=username, password_hash=password_hash.decode('utf-8'))
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "Registration successful"}), 201

# ========== Endpoint 2: Login Authentication (issues JWT) ==========
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username).first()
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
        return jsonify({"error": "Invalid username or password"}), 401
    
    # Issue JWT token, valid for 2 hours
    token = jwt.encode(
        {
            "user_id": user.id,
            "exp": datetime.utcnow() + timedelta(hours=2)
        },
        app.config['SECRET_KEY'],
        algorithm="HS256"
    )
    
    return jsonify({
        "token": token,
        "username": html.escape(user.username)
    })

# ========== Endpoint 3: Protected Data Endpoint ==========
@app.route('/api/data', methods=['GET'])
@token_required
def get_user_list(current_user):
    users = User.query.all()
    return jsonify({
        "current_user": current_user.to_dict(),
        "user_list": [u.to_dict() for u in users]
    })

@app.route('/api/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify({
        "msg": "success",
        "profile": current_user.to_dict()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)


