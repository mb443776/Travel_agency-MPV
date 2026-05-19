import os, sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'travel-agency-secret-2024')

DB_PATH = os.path.join(os.path.dirname(__file__), 'travel_agency.db')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()

    schema_path = os.path.join(os.path.dirname(__file__), 'sql', 'travel_schema.sql')
    with open(schema_path, 'r', encoding='utf-8') as f:
        db.executescript(f.read())
    db.commit()

def seed_db():
    db = get_db()
    seed_path = os.path.join(os.path.dirname(__file__), 'sql', 'travel_seed.sql')
    with open(seed_path, 'r', encoding='utf-8') as f:
        db.executescript(f.read())
    
    def ensure_user(email, login, password, full_name, phone, is_admin=0):
        cur = db.execute('SELECT id FROM users WHERE email=?', (email,))
        if not cur.fetchone():
            db.execute('''INSERT INTO users(email, login, password_hash, full_name, phone, is_admin)
                          VALUES(?,?,?,?,?,?)''',
                        (email, login, generate_password_hash(password), full_name, phone, is_admin))
    
    ensure_user('tourist@mail.ru', 'traveler1', 'pass1234', 'Алексей Иванов', '+7-900-555-11-22', 0)
    ensure_user('manager@agency.ru', 'admin_travel', 'secure_admin', 'Менеджер Светлана', '+7-800-100-20-30', 1)
    db.commit()

def ensure_db():
    if not os.path.exists(DB_PATH):
        init_db()
        seed_db()

def log_activity(user_id, action):
    db = get_db()
    # Логирование действий в таблицу activity_log
    db.execute('INSERT INTO activity_log(user_id, action, ip, user_agent) VALUES(?,?,?,?)',
               (user_id, action, request.remote_addr, request.headers.get('User-Agent', '')))
    db.commit()

@app.route('/')
def index():
    ensure_db()
    return render_template('index.html', title='Мир Путешествий - Главная')

@app.route('/register', methods=['GET', 'POST'])
def register():
    ensure_db()
    if request.method == 'POST':
        login = request.form.get('login', '').strip()
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not (login and full_name and phone and email and password):
            return render_template('register.html', error='Все поля обязательны для заполнения')
        
        if len(password) < 8:
            return render_template('register.html', error='Пароль слишком короткий (мин. 8 знаков)')

        db = get_db()
        cur = db.execute('SELECT 1 FROM users WHERE login=? OR email=?', (login, email))
        if cur.fetchone():
            return render_template('register.html', error='Такой логин или почта уже используются')

       
        db.execute('''INSERT INTO users(email, login, password_hash, full_name, phone, is_admin)
                      VALUES(?,?,?,?,?,0)''',
                   (email, login, generate_password_hash(password), full_name, phone))
        db.commit()

        user_data = db.execute('SELECT id FROM users WHERE email=?', (email,)).fetchone()
        user_id = user_data['id']
        
        log_activity(user_id, 'user_registration')
        
        session['user_id'] = user_id
        session['is_admin'] = 0
        return redirect(url_for('personal_cabinet'))
        
    return render_template('register.html')