from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import requests
import json

# Flask App Konfiguration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'bf8a9c2d4e1f6a3b7c5e8d9f0a2b4c6d8e1f3a5b7c9e2d4f6a8b0c3e5f7a9b2d4'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///beispiel.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

# Database Setup
db = SQLAlchemy(app)

# Erstelle Upload-Ordner falls nicht vorhanden
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Forms mit Flask-WTF
class RegistrationForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Passwort', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Registrieren')

class LoginForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    submit = SubmitField('Anmelden')

class PostForm(FlaskForm):
    title = StringField('Titel', validators=[DataRequired(), Length(max=100)])
    content = TextAreaField('Inhalt', validators=[DataRequired()])
    submit = SubmitField('Post erstellen')

class FileUploadForm(FlaskForm):
    file = FileField('Datei hochladen', validators=[FileAllowed(['jpg', 'png', 'pdf', 'txt'])])
    submit = SubmitField('Hochladen')

# Routen
@app.route('/')
def home():
    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()
    return render_template('home.html', posts=posts)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Prüfe ob User bereits existiert
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Benutzername bereits vergeben!', 'error')
            return render_template('register.html', form=form)
        
        # Neuen User erstellen
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash('Registrierung erfolgreich!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id
            flash('Anmeldung erfolgreich!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Ungültiger Benutzername oder Passwort.', 'error')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Du wurdest abgemeldet.', 'success')
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Bitte zuerst anmelden!', 'error')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    user_posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
    return render_template('dashboard.html', user=user, posts=user_posts)

@app.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if 'user_id' not in session:
        flash('Bitte melde dich an, um einen Post zu erstellen.', 'error')
        return redirect(url_for('login'))
    
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, user_id=session['user_id'])
        db.session.add(post)
        db.session.commit()
        flash('Post erfolgreich erstellt!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', form=form)

@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if 'user_id' not in session:
        flash('Bitte melde dich an, um eine Datei hochzuladen.', 'error')
        return redirect(url_for('login'))
        
    form = FileUploadForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash('Datei erfolgreich hochgeladen!', 'success')
        return redirect(url_for('home'))
    return render_template('upload_file.html', form=form)

# API Endpunkt
@app.route('/api/posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    posts_list = [{'id': post.id, 'title': post.title, 'content': post.content, 'user_id': post.user_id} for post in posts]
    return jsonify(posts_list)

@app.route('/api/user/<int:user_id>')
def api_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at.isoformat()
    })

@app.route('/api/weather')
def api_weather():
    """Beispiel für externe API Integration"""
    city = request.args.get('city', 'Berlin')
    # Hier würdest du einen echten API-Key verwenden
    # api_key = 'dein-openweathermap-api-key'
    # url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    
    # Für Demo-Zwecke: Mock-Daten
    mock_weather = {
        'city': city,
        'temperature': 22,
        'description': 'Sonnig',
        'humidity': 45
    }
    return jsonify(mock_weather)

@app.route('/api/search')
def search():
    query = request.args.get('q', '')
    if query:
        posts = Post.query.filter(Post.title.contains(query) | Post.content.contains(query)).all()
        results = []
        for post in posts:
            user = User.query.get(post.user_id)
            results.append({
                'id': post.id,
                'title': post.title,
                'content': post.content[:100] + '...' if len(post.content) > 100 else post.content,
                'author': user.username
            })
        return jsonify(results)
    return jsonify([])

# Claude/LLM Integration Beispiel
@app.route('/ask_claude', methods=['POST'])
def ask_claude():
    data = request.get_json()
    prompt = data.get('prompt')
    
    # Hier würdest du den Request an eine LLM API senden
    # Beispiel mit einem Dummy-Response
    response_data = {
        "completion": f"Das ist eine Dummy-Antwort von Claude auf deine Frage: '{prompt}'"
    }
    
    # In einer echten Anwendung:
    # api_url = "https://api.anthropic.com/v1/complete"
    # headers = { ... }
    # payload = { ... "prompt": f"\n\nHuman: {prompt}\n\nAssistant:" ... }
    # response = requests.post(api_url, headers=headers, json=payload)
    # response_data = response.json()

    return jsonify(response_data)

@app.cli.command("init-db")
def init_db_command():
    """Erstellt die Datenbanktabellen."""
    with app.app_context():
        db.create_all()
    print("Datenbank initialisiert.")

# Hilfsfunktionen für Templates
@app.context_processor
def utility_processor():
    def format_datetime(value):
        return value.strftime('%d.%m.%Y %H:%M')
    return dict(format_datetime=format_datetime)

# Error Handler
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)