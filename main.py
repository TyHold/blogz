from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import check_pw_hash, make_pw_hash, make_salt

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:pass@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'qwiou0942309r9dif'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30))
    body = db.Column(db.String(280))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username= db.Column(db.String(25), unique=True)
    password = db.Column(db.String(1000))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route('/', methods=['GET','POST'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/blog')
def blog():
    posts = Blog.query.all()
    if request.args.get("id"):
        posts = Blog.query.filter_by(id=request.args.get('id'))
        return render_template("post.html", posts=posts)
    if request.args.get('owner_id'):
        posts = Blog.query.filter_by(owner_id=request.args.get("owner_id"))
        return render_template("bloglist.html", posts=posts)
    return render_template("bloglist.html", posts=posts)
@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']

        if title.strip() == '' or body.strip() == '':
            flash('please enter text within the fields')
            return redirect('/newpost')    
        new_post = Blog(title, body, logged_in_user())
        db.session.add(new_post)
        db.session.commit()
        return redirect('/blog?id=' + str(new_post.id))

    return render_template("newpost.html")

def logged_in_user():
    owner = User.query.filter_by(username=session['user']).first()
    return owner

endpoints_without_login = ['login', 'register', 'blog', 'index']

@app.before_request
def require_login():
    if not ('user' in session or request.endpoint in endpoints_without_login):
        return redirect("/login")    

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = User.query.filter_by(username=username)
        if users.count() == 1:
            user = users.first()
            if password == user.password:
                session['user'] = user.username
                flash('welcome back, ' + user.username)
                return redirect("/")
        flash('bad username or password')
        return redirect("/login")

@app.route("/logout")
def logout():
    del session['user']
    return redirect("/login")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        
        username_db_count = User.query.filter_by(username=username).count()
        if username_db_count > 0:
            flash('yikes! "' + username + '" is already taken and password reminders are not implemented')
            return redirect('/register')
        if password != verify:
            flash('passwords did not match')
            return redirect('/register')
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        session['user'] = user.username
        return redirect("/")
    else:
        return render_template('signup.html')



if __name__ == '__main__':
    app.run()