from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

def isAdmin(userIP):
    if userIP == "192.168.0.1" or userIP == "138.199.7.160":
        return True
    return False

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
    userIP = request.remote_addr
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
        return render_template('index.html', threads=threads, moderator=isAdmin(userIP))

@app.route('/delete/<int:id>', methods=['POST', 'GET'])
def delete(id):
    userIP = request.remote_addr
    
    if isAdmin(userIP) == False:
        return redirect('/')
    if request.method == 'POST':
        thread = Thread.query.get_or_404(id)
        try:
            for comment in thread.comments:
                db.session.delete(comment)
            db.session.delete(thread)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue deleting the thread'

    else:
        return redirect('/')

@app.route('/thread/<int:threadID>/comment/<int:commentID>/delete', methods=['POST', 'GET'])
def commentDelete(threadID,commentID):
    userIP = request.remote_addr

    if isAdmin(userIP) == False:
        return redirect('/')
    if request.method == 'POST':
        comment = Comment.query.get_or_404(commentID)
        try:
            db.session.delete(comment)
            db.session.commit()
            return redirect(f"/thread/{threadID}")
        except:
            return 'There was an issue deleting the comment'

    else:
        return redirect('/')

@app.route('/thread/<int:id>', methods=['POST', 'GET'])
def thread(id):
    userIP = request.remote_addr
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
        return render_template('thread.html', thread=thread, moderator=isAdmin(userIP))

if __name__ == "__main__":
    app.run(debug=True, host="192.168.0.140", port=80)
