from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb+srv://akhmadretzasyahpahlevi:HAHAHA3333@cluster0.snjfd.mongodb.net/")
db = client["kepsten6"]
users = db["users"]

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = users.find_one({'email': email})
    if user:
        if bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'error': 'Password salah'}), 401
    else:
        return jsonify({'error': 'User tidak ditemukan'}), 404

# Contoh endpoint register (optional)
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    print("Received data:", data)  # Debug

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if users.find_one({'email': email}):
        return jsonify({'error': 'Email already exists'}), 409

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users.insert_one({
        'name': name,
        'email': email,
        'password': hashed
    })

    print("User registered:", email)  # Debug
    return jsonify({'message': 'Registration successful'}), 201


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
