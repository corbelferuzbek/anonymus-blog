import datetime
import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'super-secret-key-12345')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'adminsecretpassword')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Visitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50), nullable=True)
    visited_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

with app.app_context():
    db.create_all()

def track_visitor():
    try:
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        new_visitor = Visitor(ip_address=ip)
        db.session.add(new_visitor)
        db.session.commit()
    except:
        db.session.rollback()

def get_stats():
    now = datetime.datetime.utcnow()
    today_start = datetime.datetime(now.year, now.month, now.day)
    week_start = now - datetime.timedelta(days=7)
    month_start = now - datetime.timedelta(days=30)
    year_start = now - datetime.timedelta(days=365)

    return {
        'daily': Visitor.query.filter(Visitor.visited_at >= today_start).count(),
        'weekly': Visitor.query.filter(Visitor.visited_at >= week_start).count(),
        'monthly': Visitor.query.filter(Visitor.visited_at >= month_start).count(),
        'yearly': Visitor.query.filter(Visitor.visited_at >= year_start).count()
    }

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
def index():
    track_visitor()
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    track_visitor()
    post = Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        flash('Parol noto‘g‘ri!', 'danger')
    return render_template('login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    stats = get_stats()
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('admin.html', stats=stats, posts=posts)

@app.route('/admin/post/new', methods=['POST'])
@admin_required
def create_post():
    title = request.form.get('title')
    image_url = request.form.get('image_url')
    content = request.form.get('content')
    if title and content:
        db.session.add(Post(title=title, image_url=image_url, content=content))
        db.session.commit()
        flash('Post muvaffaqiyatli qo‘shildi!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/post/delete/<int:post_id>', methods=['POST'])
@admin_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post o‘chirildi!', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-light sticky-top mb-4">
        <div class="container">
            <a class="navbar-brand fw-bold text-primary" href="/"><i class="fa-solid fa-feather-pointed me-2"></i>Anonim Blog</a>
            <div>
                {% if session.get('is_admin') %}
                    <a href="/admin" class="btn btn-dark btn-custom btn-sm me-2"><i class="fa-solid fa-gauge me-1"></i> Admin Panel</a>
                    <a href="/admin/logout" class="btn btn-outline-danger btn-custom btn-sm"><i class="fa-solid fa-right-from-bracket me-1"></i> Chiqish</a>
                {% else %}
                    <a href="/admin" class="btn btn-outline-primary btn-custom btn-sm"><i class="fa-solid fa-lock me-1"></i> Admin Kirish</a>
                {% endif %}
            </div>
        </div>
    </nav>

    <div class="container pb-5">
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for cat, msg in messages %}
              <div class="alert alert-{{ 'danger' if cat == 'danger' else 'success' }} alert-dismissible fade show" role="alert">
                  {{ msg }}
                  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
              </div>
            {% endfor %}
          {% endif %}
        {% endwith %}
        
        {{ content | safe }}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

INDEX_HTML = """
<div class="row align-items-center mb-5">
    <div class="col-lg-8 mx-auto text-center">
        <h1 class="display-5 fw-bold text-dark">Qiziqarli Maqolalar Va Yangiliklar</h1>
        <p class="text-muted lead">To'liq anonim va qulay o'qish muhiti.</p>
    </div>
</div>

<div class="row">
    {% for post in posts %}
    <div class="col-md-6 col-lg-4 mb-4">
        <div class="card h-100 shadow-sm overflow-hidden">
            {% if post.image_url %}
            <img src="{{ post.image_url }}" class="card-img-top" style="height: 200px; object-fit: cover;" alt="Rasm">
            {% else %}
            <div class="bg-secondary text-white d-flex align-items-center justify-content-center" style="height: 200px;">
                <i class="fa-solid fa-image fa-3x opacity-50"></i>
            </div>
            {% endif %}
            <div class="card-body d-flex flex-column">
                <h5 class="card-title fw-bold text-dark">{{ post.title }}</h5>
                <p class="text-muted small mb-2"><i class="fa-regular fa-clock me-1"></i>{{ post.created_at.strftime('%Y-%m-%d %H:%M') }}</p>
                <p class="card-text text-secondary flex-grow-1">{{ post.content[:100] }}...</p>
                <a href="/post/{{ post.id }}" class="btn btn-primary btn-custom w-100 mt-3">Batafsil <i class="fa-solid fa-arrow-right ms-1"></i></a>
            </div>
        </div>
    </div>
    {% else %}
    <div class="col-12 text-center py-5">
        <i class="fa-solid fa-folder-open fa-3x text-muted mb-3"></i>
        <h5 class="text-muted">Hozircha postlar mavjud emas.</h5>
    </div>
    {% endfor %}
</div>
"""

DETAIL_HTML = """
<div class="row justify-content-center">
    <div class="col-lg-8">
        <div class="card shadow-lg p-4 p-md-5 bg-white">
            <h1 class="fw-bold text-dark mb-3">{{ post.title }}</h1>
            <p class="text-muted mb-4"><i class="fa-regular fa-clock me-1"></i>{{ post.created_at.strftime('%Y-%m-%d %H:%M') }}</p>
            
            {% if post.image_url %}
            <div class="mb-4 text-center">
                <img src="{{ post.image_url }}" class="img-fluid rounded shadow" style="max-height: 450px; width: 100%; object-fit: cover;" alt="Post rasmi">
            </div>
            {% endif %}

            <div class="content-body text-secondary fs-6 lh-lg" style="white-space: pre-line; word-break: break-word;">
                {{ post.content | safe }}
            </div>

            <hr class="my-4">
            <a href="/" class="btn btn-outline-secondary btn-custom"><i class="fa-solid fa-arrow-left me-2"></i>Orqaga qaytish</a>
        </div>
    </div>
</div>
"""

LOGIN_HTML = """
<div class="row justify-content-center mt-5">
    <div class="col-md-4">
        <div class="card p-4 shadow-lg border-0">
            <div class="text-center mb-4">
                <div class="bg-primary text-white rounded-circle d-inline-flex align-items-center justify-content-center shadow" style="width: 60px; height: 60px;">
                    <i class="fa-solid fa-lock fa-lg"></i>
                </div>
                <h3 class="fw-bold mt-3">Admin Panel</h3>
            </div>
            <form method="POST">
                <div class="mb-3">
                    <label class="form-label text-muted small fw-bold">PAROL</label>
                    <input type="password" name="password" class="form-control form-control-lg bg-light" placeholder="Parolni kiriting" required>
                </div>
                <button type="submit" class="btn btn-primary btn-custom w-100 py-2 shadow-sm">Kirish</button>
            </form>
        </div>
    </div>
</div>
"""

ADMIN_HTML = """
<h2 class="fw-bold mb-4">Tashriflar Statistikasi</h2>
<div class="row text-center mb-5 g-3">
    <div class="col-md-3">
        <div class="stat-card bg-gradient bg-primary">
            <h6 class="text-uppercase small fw-bold opacity-75">Kunlik</h6>
            <h2 class="fw-bold mb-0">{{ stats.daily }}</h2>
        </div>
    </div>
    <div class="col-md-3">
        <div class="stat-card bg-gradient bg-success">
            <h6 class="text-uppercase small fw-bold opacity-75">Haftalik</h6>
            <h2 class="fw-bold mb-0">{{ stats.weekly }}</h2>
        </div>
    </div>
    <div class="col-md-3">
        <div class="stat-card bg-gradient bg-warning text-dark">
            <h6 class="text-uppercase small fw-bold opacity-75">Oylik</h6>
            <h2 class="fw-bold mb-0">{{ stats.monthly }}</h2>
        </div>
    </div>
    <div class="col-md-3">
        <div class="stat-card bg-gradient bg-info">
            <h6 class="text-uppercase small fw-bold opacity-75">Yillik</h6>
            <h2 class="fw-bold mb-0">{{ stats.yearly }}</h2>
        </div>
    </div>
</div>

<div class="card p-4 shadow-sm mb-5">
    <h4 class="fw-bold mb-4 text-primary"><i class="fa-solid fa-pen-to-square me-2"></i>Yangi Post Qo'shish</h4>
    <form action="/admin/post/new" method="POST">
        <div class="mb-3">
            <label class="form-label fw-bold small">Sarlavha</label>
            <input type="text" name="title" class="form-control" placeholder="Post sarlavhasini kiriting..." required>
        </div>
        <div class="mb-3">
            <label class="form-label fw-bold small">Rasm URL (ixtiyoriy)</label>
            <input type="url" name="image_url" class="form-control" placeholder="https://example.com/image.jpg">
        </div>
        <div class="mb-3">
            <label class="form-label fw-bold small">Matn (Ssilka qo'shish uchun: <code class="text-danger">&lt;a href="url" target="_blank"&gt;matn&lt;/a&gt;</code>)</label>
            <textarea name="content" class="form-control" rows="6" placeholder="Post matnini yozing..." required></textarea>
        </div>
        <button type="submit" class="btn btn-success btn-custom px-4"><i class="fa-solid fa-upload me-1"></i> Chop etish</button>
    </form>
</div>

<div class="card p-4 shadow-sm">
    <h4 class="fw-bold mb-4"><i class="fa-solid fa-list me-2"></i>Mavjud Postlar</h4>
    <div class="table-responsive">
        <table class="table table-hover align-middle">
            <thead class="table-light">
                <tr>
                    <th>Sarlavha</th>
                    <th>Sana</th>
                    <th class="text-end">Amal</th>
                </tr>
            </thead>
            <tbody>
                {% for post in posts %}
                <tr>
                    <td class="fw-semibold">{{ post.title }}</td>
                    <td class="text-muted small">{{ post.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
                    <td class="text-end">
                        <form action="/admin/post/delete/{{ post.id }}" method="POST" style="display:inline;">
                            <button type="submit" class="btn btn-outline-danger btn-sm" onclick="return confirm('Haqiqatan ham o‘chirmoqchimisiz?')"><i class="fa-solid fa-trash"></i></button>
                        </form>
                    </td>
                </tr>
                {% else %}
                <tr>
                    <td colspan="3" class="text-center text-muted py-3">Postlar topilmadi.</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
"""

# --- ROUTelar ---
@app.route('/')
def index():
    track_visitor()
    posts = Post.query.order_by(Post.created_at.desc()).all()
    body = render_template_string(INDEX_HTML, posts=posts)
    return render_template_string(LAYOUT, content=body)

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    track_visitor()
    post = Post.query.get_or_404(post_id)
    body = render_template_string(DETAIL_HTML, post=post)
    return render_template_string(LAYOUT, content=body)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        flash('Parol noto‘g‘ri!', 'danger')
    body = render_template_string(LOGIN_HTML)
    return render_template_string(LAYOUT, content=body)

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    stats = get_stats()
    posts = Post.query.order_by(Post.created_at.desc()).all()
    body = render_template_string(ADMIN_HTML, stats=stats, posts=posts)
    return render_template_string(LAYOUT, content=body)

@app.route('/admin/post/new', methods=['POST'])
@admin_required
def create_post():
    title = request.form.get('title')
    image_url = request.form.get('image_url')
    content = request.form.get('content')
    if title and content:
        db.session.add(Post(title=title, image_url=image_url, content=content))
        db.session.commit()
        flash('Post muvaffaqiyatli qo‘shildi!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/post/delete/<int:post_id>', methods=['POST'])
@admin_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post o‘chirildi!', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
