from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.String(200), nullable=False)
    comments = db.relationship('Comment', backref='thread', lazy=True)

    def __repr__(self):
        return f"User('{self.id}', {self.title}', '{self.author}', '{self.date}', '{self.content}')"

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.String(200), nullable=False)
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'), nullable=False)

    def __repr__(self):
        return f"Comment('{self.id}', '{self.author}', '{self.date}', '{self.content}')"

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        thread_title = request.form['title']
        thread_author = request.form['author']
        thread_content = request.form['content']
        
        new_thread = Thread(title=thread_title,author=thread_author,content=thread_content)

        try:
            db.session.add(new_thread)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your thread'

    else:
        threads = Thread.query.order_by(Thread.date).all()
        return render_template('index.html', threads=threads)

@app.route('/thread/<int:id>', methods=['POST', 'GET'])
def thread(id):
    thread = Thread.query.get_or_404(id)

    if request.method == 'POST':
        comment_author = request.form['author']
        comment_content = request.form['content']
        
        new_comment = Comment(author=comment_author,content=comment_content,thread_id=id)
        thread.comments.append(new_comment)

        try:
            db.session.commit()
            return redirect(f"/thread/{id}")
        except:
            return 'There was an issue adding your comment'

    else:
        return render_template('thread.html', thread=thread)

if __name__ == "__main__":
    app.run(debug=True, host="192.168.0.140", port=80)
