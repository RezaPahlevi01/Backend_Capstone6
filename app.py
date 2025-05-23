from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt
import smtplib
from email.message import EmailMessage
import base64
import uuid
from datetime import datetime, timedelta
from flask import render_template

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb+srv://akhmadretzasyahpahlevi:HAHAHA3333@cluster0.snjfd.mongodb.net/")
db = client["kepsten6"]
users = db["users"]

@app.route('/')
def home():
    return "Hello from Flask deployed with Vercel CLI!"

def send_verification_email(email, token):
    verify_link = f"https://swingprobackend.vercel.app/verify-email/{token}"

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
        <h2 style="color: #4CAF50;">Verifikasi Email Anda</h2>
        <p>Hai,</p>
        <p>Terima kasih telah mendaftar. Klik tombol di bawah untuk memverifikasi email Anda:</p>
        <p style="text-align: center;">
            <a href="{verify_link}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verifikasi Email</a>
        </p>
        <p>Link ini berlaku selama 1 jam.</p>
        <hr />
        <p style="font-size: 12px; color: #888;">Jika Anda tidak merasa mendaftar, abaikan email ini.</p>
        </div>
    </body>
    </html>
    """


    msg = EmailMessage()
    msg['Subject'] = 'Verifikasi Email Anda'
    msg['From'] = 'akhmadretzasyahpahlevi@gmail.com'
    msg['To'] = email
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(html_content)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login('akhmadretzasyahpahlevi@gmail.com', 'yvss eivd eteq idmj')
            smtp.send_message(msg)
            print("Email verifikasi berhasil dikirim ke:", email)
    except Exception as e:
        print("Gagal mengirim email:", e)


@app.route('/verify-email/<token>')
def verify_email(token):
    user = users_collection.find_one({"verification_token": token})

    if not user:
        return render_template('verification_result.html', success=False)

    if user.get("is_verified"):
        return render_template('verification_result.html', success=True)

    users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"is_verified": True}, "$unset": {"verification_token": ""}}
    )

    return render_template('verification_result.html', success=True)


@app.route('/resend-verification', methods=['POST'])
def resend_verification():
    data = request.get_json()
    email = data.get('email')

    user = users.find_one({'email': email})
    if not user:
        return jsonify({'error': 'User tidak ditemukan'}), 404

    if user.get('is_verified', False):
        return jsonify({'message': 'Email sudah diverifikasi'}), 200

    # Hapus token lama jika ada
    db.email_verifications.delete_many({'email': email})

    token = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(hours=1)
    db.email_verifications.insert_one({
        'email': email,
        'token': token,
        'expires_at': expires_at
    })

    send_verification_email(email, token)

    return jsonify({'message': 'Email verifikasi telah dikirim ulang'}), 200


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = users.find_one({'email': email})
    if user:
        if not user.get('is_verified', False):
            return jsonify({'error': 'Email belum terverifikasi. Cek email Anda.'}), 403

        if bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return jsonify({'message': 'Login berhasil'}), 200
        else:
            return jsonify({'error': 'Password salah'}), 401


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
        'password': hashed,
        'is_verified': False
    })

    token = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(hours=1)
    db.email_verifications.insert_one({
        'email': email,
        'token': token,
        'expires_at': expires_at
    })

    # Kirim email verifikasi
    send_verification_email(email, token)


    print("User registered:", email)  # Debug
    return jsonify({'message': 'Registration successful'}), 201


if __name__ == '__main__':
    app.run()
