from flask import Flask, request, jsonify, render_template, send_from_directory, session, redirect, url_for
from flask_mail import Mail, Message
from flask_session import Session
from neo4j import GraphDatabase
import random

app = Flask(__name__)
app.secret_key = 'bcbd652cfefee04c5cda3f4b38d866dd'  # Replace with your generated secret key

# Configuring Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Configuring Flask-Mail for Gmail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'quickinsightsolutions.ai@gmail.com'
app.config['MAIL_PASSWORD'] = 'bnkf jkmc gdko sory'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

# Neo4j connection details
neo4j_uri = "bolt://localhost:7687"
neo4j_user = "neo4j"
neo4j_password = "Password@24"

# Create a Neo4j driver instance
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

otp_store = {}

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(email, otp):
    subject = 'Quick Insight Solutions: One-Time Password (OTP) Verification'
    body = f"""
    Dear User,

    Your one-time password (OTP) for verification is: {otp}

    Please use this OTP to complete your verification process. 
    
    This OTP is valid for a limited time only.

    If you did not request this OTP, please ignore this email.

    Thank you,
    Quick Insight Solutions Team
    """

    msg = Message(subject, sender='quickinsightsolutions.ai@gmail.com', recipients=[email])
    msg.body = body
    mail.send(msg)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    otp = generate_otp()
    otp_store[email] = {'password': password, 'otp': otp}
    
    send_otp(email, otp)
    
    return jsonify({"success": True, "message": "OTP sent to email. Please verify to complete registration."})

@app.route('/verify_otp', methods=['POST'])
def verify_otp_route():
    data = request.get_json()
    email = data.get('email')
    otp = data.get('otp')
    
    if email in otp_store and otp_store[email]['otp'] == otp:  # Corrected comparison
        password = otp_store[email]['password']
        with driver.session() as session:
            session.run("CREATE (u:User {email: $email, password: $password})", email=email, password=password)
        del otp_store[email]
        return jsonify({"success": True, "message": "Registration completed successfully."})
    
    return jsonify({"success": False, "message": "Invalid OTP. Please try again."})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    success, message = authenticate_user(email, password)
    if success:
        session['user'] = email  # Store user email in session
    return jsonify({"success": success, "message": message})

def authenticate_user(email, password):
    with driver.session() as session:
        result = session.run("MATCH (u:User {email: $email, password: $password}) RETURN u", email=email, password=password)
        if result.single():
            return True, "Login successful"
        return False, "Invalid credentials"

@app.route('/dashboard.html')
def dashboard():
    if 'user' in session:
        return send_from_directory('templates', 'dashboard.html')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5003)
