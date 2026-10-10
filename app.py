from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SECRET_KEY'] = 'maxfiy-kalit-soz-anonymus-blog'

db = SQLAlchemy(app)


# --- MODELLAR ---
class Post(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(200), nullable=False)
  content = db.Column(db.Text, nullable=False)
  date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Visitor(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  ip_address = db.Column(db.String(100))
  visit_time = db.Column(db.DateTime, default=datetime.utcnow)


# Bazani avtomatik yaratish (kontekst bilan)
with app.app_context():
  try:
    db.create_all()
  except Exception as e:
    print(f'Baza yaratishda xato: {e}')


# --- MEHMONLARNI KUZATISH ---
@app.before_request
def track_visitor():
  try:
    ip = request.remote_addr or '127.0.0.1'
    visitor = Visitor(ip_address=ip)
    db.session.add(visitor)
    db.session.commit()
  except Exception:
    db.session.rollback()


# --- SAHIFALAR (ROUTES) ---

# Asosiy sahifa
@app.route('/')
def index():
  try:
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    visitor_count = Visitor.query.count()
  except Exception:
    posts = []
    visitor_count = 0
  return render_template('index.html', posts=posts, visitor_count=visitor_count)


# Admin panel (Post qo'shish va ro'yxatni ko'rish)
@app.route('/admin', methods=['GET', 'POST'])
def admin():
  if request.method == 'POST':
    try:
      title = request.form.get('title')
      content = request.form.get('content')
      if title and content:
        new_post = Post(title=title, content=content)
        db.session.add(new_post)
        db.session.commit()
        flash("Yangi post muvaffaqiyatli qo'shildi!", 'success')
        return redirect(url_for('admin'))
      else:
        flash("Sarlavha va matn bo'sh bo'lmasligi kerak!", 'danger')
    except Exception as e:
      db.session.rollback()
      flash(f'Xatolik yuz berdi: {e}', 'danger')

  try:
    posts = Post.query.order_by(Post.date_posted.desc()).all()
  except Exception:
    posts = []

  return render_template('admin.html', posts=posts)


# Postni o'chirish
@app.route('/admin/delete/<int:id>')
def delete_post(id):
  try:
    post = Post.query.get_or_404(id)
    db.session.delete(post)
    db.session.commit()
    flash("Post o'chirildi!", 'info')
  except Exception as e:
    db.session.rollback()
    flash(f"O'chirishda xatolik: {e}", 'danger')
  return redirect(url_for('admin'))


if __name__ == '__main__':
  app.run(debug=True)
