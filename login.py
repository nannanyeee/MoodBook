from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image

# ---------- Flask 설정 ----------
app = Flask(__name__)
app.secret_key = 'secretkey123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ---------- DB 모델 ----------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class BookCover(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))
    ocr_text = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# ---------- 로그인 매니저 ----------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------- 라우트 ----------
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('upload'))
    return redirect(url_for('login'))

# 회원가입
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('이미 존재하는 사용자입니다.')
            return redirect(url_for('register'))
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('회원가입 성공! 로그인하세요.')
        return redirect(url_for('login'))
    return render_template('register.html')

# 로그인
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            flash('로그인 성공!')
            return redirect(url_for('upload'))
        else:
            flash('아이디 또는 비밀번호가 틀렸습니다.')
    return render_template('login.html')

# 로그아웃
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('로그아웃되었습니다.')
    return redirect(url_for('login'))

# 업로드 페이지
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('파일이 없습니다!')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('파일 이름이 없습니다.')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(filepath)

            # ---------- OCR ----------
            text = pytesseract.image_to_string(Image.open(filepath), lang='kor+eng')

            # ---------- DB 저장 ----------
            new_cover = BookCover(filename=filename, ocr_text=text, user_id=current_user.id)
            db.session.add(new_cover)
            db.session.commit()
            return render_template('result.html', image_file=filename, ocr_text=text)
    return render_template('upload.html')

# OCR 결과 JSON 출력 (사용자별)
@app.route('/data')
@login_required
def data():
    covers = BookCover.query.filter_by(user_id=current_user.id).all()
    result = [{"filename": c.filename, "ocr_text": c.ocr_text} for c in covers]
    return jsonify(result)

# ---------- 앱 실행 ----------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5001, debug=True)