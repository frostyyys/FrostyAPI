from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import hashlib
import base64
import uuid
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Utility functions
def custom_transform(text):
    transformed = ''.join(chr((ord(char) + 12) % 256) for char in text[::-1])
    return transformed

def shift12_encode(text):
    shifted = []
    for char in text:
        if 'a' <= char <= 'z':
            shifted.append(chr((ord(char) - ord('a') + 12) % 26 + ord('a')))
        elif 'A' <= char <= 'Z':
            shifted.append(chr((ord(char) - ord('A') + 12) % 26 + ord('A')))
        else:
            shifted.append(char)
    return ''.join(shifted)

def frost_hash(text):
    reversed_salt = text[::-1]
    salt_length = str(len(reversed_salt))
    salted_text = text + reversed_salt + salt_length
    transformed_text = custom_transform(salted_text)
    sha256_hash = hashlib.sha256(transformed_text.encode()).hexdigest()
    base64_encoded = base64.b64encode(sha256_hash[:16].encode()).decode().rstrip('=')
    shift12_hash = shift12_encode(base64_encoded)
    combined_hash = (sha256_hash[16:] + shift12_hash)[:32]
    return combined_hash

admin_hashed_password = "479acbd8c4004c518ed87652902287fe"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    license_id = db.Column(db.Integer, db.ForeignKey('license.id'), nullable=True)
    license = db.relationship('License', backref=db.backref('users', lazy=True))
    banned = db.Column(db.Boolean, default=False)
    ban_reason = db.Column(db.String(255), nullable=True)
    last_login_ip = db.Column(db.String(15), nullable=True)
    last_login_time = db.Column(db.DateTime, nullable=True)
    
    @property
    def rank(self):
        return self.license.rank if self.license else None


class License(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(36), unique=True, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    rank = db.Column(db.String(50), nullable=False)

# Existing routes
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    license_key = data.get('license_key')

    if not username or not password or not license_key:
        return jsonify({"error": "Username, password, and license key are required"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User already exists"}), 400

    license = License.query.filter_by(key=license_key, is_used=False).first()
    if not license:
        return jsonify({"error": "Invalid or already used license key"}), 400

    password_hash = frost_hash(password)

    new_user = User(username=username, password_hash=password_hash, license_id=license.id)
    db.session.add(new_user)

    license.is_used = True
    db.session.commit()

    return jsonify({"message": "User registered successfully!", "rank": license.rank})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"error": "Incorrect login information"}), 401

    if user.banned:
        return jsonify({"error": f"User is banned: {user.ban_reason}"}), 403

    provided_hash = frost_hash(password)

    if provided_hash == user.password_hash:
        user.last_login_ip = request.remote_addr
        user.last_login_time = datetime.now()
        db.session.commit()
        return jsonify({
            "message": "Login successful",
            "rank": user.rank  # Include the user's rank in the response
        })
    else:
        return jsonify({"error": "Incorrect login information"}), 401

# New Route: Delete License
@app.route('/delete_license', methods=['POST'])
def delete_license():
    data = request.json
    admin_password = data.get('admin_password')
    license_key = data.get('license_key')

    if frost_hash(admin_password) != admin_hashed_password:
        return jsonify({'message': 'Unauthorized'}), 403

    license = License.query.filter_by(key=license_key).first()
    if not license:
        return jsonify({'message': 'License not found'}), 404

    db.session.delete(license)
    db.session.commit()
    return jsonify({'message': f'License {license_key} deleted successfully'}), 200

# New Route: Delete User
@app.route('/delete_user', methods=['POST'])
def delete_user():
    data = request.json
    admin_password = data.get('admin_password')
    username = data.get('username')

    if frost_hash(admin_password) != admin_hashed_password:
        return jsonify({'message': 'Unauthorized'}), 403

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': f'User {username} deleted successfully'}), 200

# New Route: Change Password
@app.route('/change_password', methods=['POST'])
def change_password():
    data = request.json
    admin_password = data.get('admin_password')
    username = data.get('username')
    new_password = data.get('new_password')

    if frost_hash(admin_password) != admin_hashed_password:
        return jsonify({'message': 'Unauthorized'}), 403

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    new_password_hash = frost_hash(new_password)
    user.password_hash = new_password_hash
    db.session.commit()
    return jsonify({'message': f'Password for {username} updated successfully'}), 200

# New Route: Change Rank
@app.route('/change_rank', methods=['POST'])
def change_rank():
    data = request.json
    admin_password = data.get('admin_password')
    username = data.get('username')
    new_rank = data.get('new_rank')

    if frost_hash(admin_password) != admin_hashed_password:
        return jsonify({'message': 'Unauthorized'}), 403

    user = User.query.filter_by(username=username).first()
    if not user or not user.license:
        return jsonify({'message': 'User or license not found'}), 404

    user.license.rank = new_rank
    db.session.commit()
    return jsonify({'message': f'Rank for {username} changed to {new_rank} successfully'}), 200

# Route to view licenses
@app.route('/licenses', methods=['GET'])
def view_licenses():
    admin_password = request.args.get('admin_password')
    if frost_hash(admin_password) != admin_hashed_password:
        return jsonify({'message': 'Unauthorized'}), 403

    licenses = License.query.all()
    licenses_data = [{'key': lic.key, 'is_used': lic.is_used, 'rank': lic.rank} for lic in licenses]
    return jsonify({'licenses': licenses_data}), 200

# Route to view users
@app.route('/users', methods=['GET'])
def view_users():
    admin_password = request.args.get('admin_password')

    if frost_hash(admin_password) != admin_hashed_password:
        return jsonify({'message': 'Unauthorized'}), 403

    users = User.query.all()
    users_data = [
        {
            'username': user.username,
            'license_used': user.license.key if user.license else None,
            'rank': user.rank,  # Include rank here
            'banned': user.banned,
            'ban_reason': user.ban_reason if user.banned else None,
            'last_login_ip': user.last_login_ip,
            'last_login_time': user.last_login_time
        }
        for user in users
    ]

    return jsonify({'users': users_data}), 200


# Route to ban a user
@app.route('/ban_user', methods=['GET'])
def ban_user():
    admin_password = request.args.get('admin_password')
    username = request.args.get('username')
    reason = request.args.get('reason')

    if frost_hash(admin_password) != admin_hashed_password:
        return jsonify({'message': 'Unauthorized'}), 403

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    user.banned = True
    user.ban_reason = reason
    db.session.commit()
    return jsonify({'message': f'User {username} has been banned for: {reason}'}), 200

# Route to unban a user
@app.route('/unban_user', methods=['GET'])
def unban_user():
    admin_password = request.args.get('admin_password')
    username = request.args.get('username')

    if frost_hash(admin_password) != admin_hashed_password:
        return jsonify({'message': 'Unauthorized'}), 403

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    user.banned = False
    user.ban_reason = None
    db.session.commit()
    return jsonify({'message': f'User {username} has been unbanned'}), 200

# Route to generate a license key
@app.route('/generate_license', methods=['POST'])
def generate_license():
    data = request.json
    admin_password = data.get('admin_password')
    rank = data.get('rank')

    if frost_hash(admin_password) != admin_hashed_password:
        return jsonify({'message': 'Unauthorized'}), 403

    license_key = str(uuid.uuid4())
    new_license = License(key=license_key, rank=rank)
    db.session.add(new_license)
    db.session.commit()

    return jsonify({'license_key': license_key, 'rank': rank}), 200

# Route to check license validity
@app.route('/check_license', methods=['GET'])
def check_license():
    admin_password = request.args.get('admin_password')
    license_key = request.args.get('license_key')

    if frost_hash(admin_password) != admin_hashed_password:
        return jsonify({'message': 'Unauthorized'}), 403

    license = License.query.filter_by(key=license_key).first()
    if not license:
        return jsonify({'message': 'License not found'}), 404

    return jsonify({'license_key': license.key, 'is_used': license.is_used, 'rank': license.rank}), 200

# Create all tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

