from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify
import sqlite3
import os
import jwt
import datetime
import RPi.GPIO as GPIO
from time import sleep


app = Flask(__name__)
app.secret_key = 'supersecretkey'  
SECRET_KEY = 'your_jwt_secret_key'

db_path = os.path.join(os.path.dirname(__file__), "Database", "poggi.db")

def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def create_users_table():
    with get_db_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')
        conn.commit()

create_users_table()

# Classe AlphaBot
class AlphaBot:
    def __init__(self, in1=12, in2=13, ena=6, in3=20, in4=21, enb=26):
        self.IN1 = in1
        self.IN2 = in2
        self.IN3 = in3
        self.IN4 = in4
        self.ENA = ena
        self.ENB = enb

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.IN1, GPIO.OUT)
        GPIO.setup(self.IN2, GPIO.OUT)
        GPIO.setup(self.IN3, GPIO.OUT)
        GPIO.setup(self.IN4, GPIO.OUT)
        GPIO.setup(self.ENA, GPIO.OUT)
        GPIO.setup(self.ENB, GPIO.OUT)

        self.PWMA = GPIO.PWM(self.ENA, 500)
        self.PWMB = GPIO.PWM(self.ENB, 500)
        self.PWMA.start(50)
        self.PWMB.start(50)

    def setMotor(self, left, right):
        if right >= 0:
            GPIO.output(self.IN1, GPIO.HIGH)
            GPIO.output(self.IN2, GPIO.LOW)
            self.PWMA.ChangeDutyCycle(right)
        else:
            GPIO.output(self.IN1, GPIO.LOW)
            GPIO.output(self.IN2, GPIO.HIGH)
            self.PWMA.ChangeDutyCycle(-right)
        
        if left >= 0:
            GPIO.output(self.IN3, GPIO.HIGH)
            GPIO.output(self.IN4, GPIO.LOW)
            self.PWMB.ChangeDutyCycle(left)
        else:
            GPIO.output(self.IN3, GPIO.LOW)
            GPIO.output(self.IN4, GPIO.HIGH)
            self.PWMB.ChangeDutyCycle(-left)

    def stop(self):
        self.setMotor(0, 0)

# Istanza del robot
robot = AlphaBot()
robot.stop()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['e-mail']
        password = request.form['password']
        
        with get_db_connection() as conn:
            user = conn.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password)).fetchone()
            
            if user:
                token = jwt.encode({'user_id': user['id'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(days=30)}, SECRET_KEY, algorithm='HS256')
                resp = make_response(redirect(url_for('controller')))
                resp.set_cookie('token', token, max_age=60*60*24*30, httponly=True)
                return resp
            else:
                return "Errore: credenziali non valide", 401
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['e-mail']
        password = request.form['password']
        
        with get_db_connection() as conn:
            try:
                conn.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
                conn.commit()
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                return "Errore: Email già registrata", 400
    
    return render_template('register.html')

def decode_token(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@app.route('/controller')
def controller():
    token = request.cookies.get('token')
    if token:
        decoded_token = decode_token(token)
        if decoded_token:
            return render_template('controller.html')
    return redirect(url_for('login'))

@app.route('/command', methods=['POST'])
def command():
    data = request.get_json()
    if not data or 'command' not in data:
        return jsonify({"error": "Comando non valido"}), 400
    
    command = data['command']
    if command == 'forward':
        robot.setMotor(-50, 50)
    elif command == 'backward':
        robot.setMotor(50, -50)
    elif command == 'left':
        robot.setMotor(-30, -30)
    elif command == 'right':
        robot.setMotor(30, 30) 
    elif command == 'stop':
        robot.stop()
    else:
        return jsonify({"error": "Comando sconosciuto"}), 400
    
    return jsonify({"success": True, "command": command})

@app.route('/logout', methods=['POST'])
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.delete_cookie('token')
    return resp

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        GPIO.cleanup()