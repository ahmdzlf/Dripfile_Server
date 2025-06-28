import os
import time
import uuid
from flask import Flask, render_template, request, send_from_directory, redirect, session, url_for, flash
import mysql.connector
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/app/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx'}

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

# 🔁 Koneksi global ke database (untuk operasi utama)
for _ in range(10):
    try:
        db = mysql.connector.connect(
            host=os.environ.get('DB_HOST'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            database=os.environ.get('DB_NAME')
        )
        cursor = db.cursor(dictionary=True)
        break
    except:
        print("Waiting for MySQL...")
        time.sleep(3)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 🔐 Logging akses pakai koneksi baru
def log_user_access():
    session_id = session.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id

    ip = request.remote_addr
    user_agent = request.user_agent.string

    try:
        conn = mysql.connector.connect(
            host=os.environ.get('DB_HOST'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            database=os.environ.get('DB_NAME')
        )
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            INSERT INTO access_logs (session_id, ip, user_agent, last_access)
            VALUES (%s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE last_access = NOW()
        """, (session_id, ip, user_agent))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("❌ Gagal log akses:", e)

@app.route('/', methods=['GET', 'POST'])
def index():
    log_user_access()
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect('/')
        file = request.files['file']
        if file.filename == '':
            return redirect('/')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            name, ext = os.path.splitext(filename)
            ext = ext.replace('.', '')
            size = os.path.getsize(filepath)
            size_str = f"{round(size/1024, 2)}.kb" if size < 1024*1024 else f"{round(size/1024/1024, 2)}.mb"

            cursor.execute("INSERT INTO files (name, extension, size) VALUES (%s, %s, %s)", (filename, ext, size_str))
            db.commit()
            flash('File berhasil diupload!', 'success')
            return redirect('/')

    cursor.execute("SELECT * FROM files ORDER BY upload_date DESC")
    files = cursor.fetchall()
    return render_template('index.html', files=files)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM admins WHERE username = %s AND password = SHA2(%s, 256)", (username, password))
        admin = cursor.fetchone()
        if admin:
            session['admin'] = True
            return redirect('/admin')
        else:
            return render_template('login.html', error="Username atau password salah")
    return render_template('login.html', error=None)

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin'):
        return redirect('/login')
    cursor.execute("SELECT * FROM access_logs ORDER BY last_access DESC")
    logs = cursor.fetchall()
    return render_template('admin_dashboard.html', logs=logs)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/delete_log/<session_id>', methods=['POST'])
def delete_log(session_id):
    if not session.get('admin'):
        return redirect('/login')
    cursor.execute("DELETE FROM access_logs WHERE session_id = %s", (session_id,))
    db.commit()
    return redirect('/admin')

@app.route('/delete_all_logs', methods=['POST'])
def delete_all_logs():
    if not session.get('admin'):
        return redirect('/login')
    cursor.execute("DELETE FROM access_logs")
    db.commit()
    return redirect('/admin')

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host='0.0.0.0', port=5000, debug=True)
import os
import time
import uuid
from flask import Flask, render_template, request, send_from_directory, redirect, session, url_for, flash
import mysql.connector
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/app/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'docx'}

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def log_user_access():
    session_id = session.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id

    ip = request.remote_addr
    user_agent = request.user_agent.string

    try:
        conn = mysql.connector.connect(
            host=os.environ.get('DB_HOST'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD'),
            database=os.environ.get('DB_NAME')
        )
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            INSERT INTO access_logs (session_id, ip, user_agent, last_access)
            VALUES (%s, %s, %s, NOW())
            ON DUPLICATE KEY UPDATE last_access = NOW()
        """, (session_id, ip, user_agent))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("\u274c Gagal log akses:", e)

@app.route('/', methods=['GET', 'POST'])
def index():
    log_user_access()
    conn = mysql.connector.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME')
    )
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect('/')
        file = request.files['file']
        if file.filename == '':
            return redirect('/')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            name, ext = os.path.splitext(filename)
            ext = ext.replace('.', '')
            size = os.path.getsize(filepath)
            size_str = f"{round(size/1024, 2)}.kb" if size < 1024*1024 else f"{round(size/1024/1024, 2)}.mb"

            cursor.execute("INSERT INTO files (name, extension, size) VALUES (%s, %s, %s)", (filename, ext, size_str))
            conn.commit()
            flash('File berhasil diupload!', 'success')
            return redirect('/')

    cursor.execute("SELECT * FROM files ORDER BY upload_date DESC")
    files = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', files=files)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    conn = mysql.connector.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME')
    )
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM admins WHERE username = %s AND password = SHA2(%s, 256)", (username, password))
        admin = cursor.fetchone()
        if admin:
            session['admin'] = True
            cursor.close()
            conn.close()
            return redirect('/admin')
        else:
            cursor.close()
            conn.close()
            return render_template('login.html', error="Username atau password salah")
    cursor.close()
    conn.close()
    return render_template('login.html', error=None)

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin'):
        return redirect('/login')

    conn = mysql.connector.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME')
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM access_logs ORDER BY last_access DESC")
    logs = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin_dashboard.html', logs=logs)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/delete_log/<session_id>', methods=['POST'])
def delete_log(session_id):
    if not session.get('admin'):
        return redirect('/login')

    conn = mysql.connector.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME')
    )
    cursor = conn.cursor()
    cursor.execute("DELETE FROM access_logs WHERE session_id = %s", (session_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/admin')

@app.route('/delete_all_logs', methods=['POST'])
def delete_all_logs():
    if not session.get('admin'):
        return redirect('/login')

    conn = mysql.connector.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database=os.environ.get('DB_NAME')
    )
    cursor = conn.cursor()
    cursor.execute("DELETE FROM access_logs")
    conn.commit()
    cursor.close()
    conn.close()
    return redirect('/admin')

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(host='0.0.0.0', port=5000, debug=True)

