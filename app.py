from flask import Flask, request, jsonify
from database import db
from models.user import User
from flask_login import LoginManager, login_user, logout_user, login_required, current_user



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your_secret_key'
login_manager = LoginManager()

db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username and password:
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return jsonify({
                'message': 'Login successful',
                'status': 'success'
            }), 200

    return jsonify({
        'message': 'Invalid credentials',
        'status': 'error'
    }), 400

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({
        'message': 'Logout successful',
        'status': 'success'
    }), 200

@app.route('/user', methods=['POST'])
def create_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if username and password:
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            'message': 'User created successfully',
            'status': 'success'
        }), 201

    return jsonify({
        'message': 'Username and password are required',
        'status': 'error'
    }), 400


@app.route('/user/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify({
            'id': user.id,
            'username': user.username
        }), 200
    return jsonify({
        'message': 'User not found',
        'status': 'error'
    }), 404

@app.route('/user/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    data = request.json
    user = User.query.get(user_id)

    if user:
        password = data.get('password')

        if password:
            user.password = password

        db.session.commit()
        return jsonify({
            'message': 'User updated successfully',
            'status': 'success'
        }), 200

    return jsonify({
        'message': 'User not found',
        'status': 'error'
    }), 404

@app.route('/user/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    user = User.query.get(user_id)

    if current_user.id == user_id:
        return jsonify({
            'message': 'You cannot delete your own account',
            'status': 'error'
        }), 403

    if user:
        db.session.delete(user)
        db.session.commit()
        return '', 204

    return jsonify({
        'message': 'User not found',
        'status': 'error'
    }), 404

if __name__ == '__main__':
    app.run(debug=True)
