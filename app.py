from datetime import datetime
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SECRET_KEY'] = 'maxfiy-kalit-soz'  # Bu yerda xohlagan matnni yozishingiz mumkin
db = SQLAlchemy(app)


# Ma'lumotlar bazasi modellari
class Post(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(200), nullable=False)
  content = db.Column(db.Text, nullable=False)
  date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Visitor(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  ip_address = db.Column(db.String(100))
  visit_time = db.Column(db.DateTime, default=datetime.utcnow)


# Bazani yaratish
with app.app_context():
  db.create_all()


# Mehmonlarni kuzatish (Visitor tracking)
@app.before_request
def track_visitor():
  try:
    ip = request.remote_addr
    visitor = Visitor(ip_address=ip)
    db.session.add(visitor)
    db.session.commit()
  except Exception:
    pass  # Bazaga yozishda xatolik bo'lsa sayt to'xtab qolmasligi uchun


# Asosiy sahifa
@app.route('/')
def index():
  posts = Post.query.order_by(Post.date_posted.desc()).all()
  visitor_count = Visitor.query.count()
  return render_template('index.html', posts=posts, visitor_count=visitor_count)


# Admin panel (Post qo'shish va boshqarish)
@app.route('/admin', methods=['GET', 'POST'])
def admin():
  if request.method == 'POST':
    title = request.form.get('title')
    content = request.form.get('content')
    if title and content:
      new_post = Post(title=title, content=content)
      db.session.add(new_post)
      db.session.commit()
      flash("Yangi post muvaffaqiyatli qo'shildi!", 'success')
      return redirect(url_for('admin'))

  posts = Post.query.order_by(Post.date_posted.desc()).all()
  return render_template('admin.html', posts=posts)


# Postni o'chirish
@app.route('/admin/delete/<int:id>')
def delete_post(id):
  post = Post.query.get_or_404(id)
  db.session.delete(post)
  db.session.commit()
  flash("Post o'chirildi!", 'info')
  return redirect(url_for('admin'))


if __name__ == '__main__':
  app.run(debug=True)
