from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://buildablog:pass@localhost:8889/buildablog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'qwiou0942309r9dif'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30))
    body = db.Column(db.String(280))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/', methods=['GET','POST'])
def index():
    return redirect('/blog')

@app.route('/blog')
def blog():
    posts = Blog.query.all()
    if request.method == 'GET':
        if request.args:
            post = Blog.query.filter_by(id=request.args.get('id'))
            return render_template("post.html", posts=post)
    return render_template("mainpage.html", posts=posts)

@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']

        if title.strip() == '' or body.strip() == '':
            flash('please enter text within the fields')
            return redirect('/newpost')    
        new_post = Blog(title, body)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/blog?id=' + str(new_post.id))

    return render_template("newpost.html")

app.run()