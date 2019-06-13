from flask import Flask, request, redirect, render_template, session, flash
from flask_login import current_user, login_user, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from models import User, Blog
from app import app, db
from forms import LoginForm, RegistrationForm
from werkzeug.urls import url_parse


@app.route('/')
@app.route('/index')
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
@login_required
def newpost():
    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']

        if title.strip() == '' or body.strip() == '':
            flash('please enter text within the fields')
            return redirect('/newpost')    
        new_post = Blog(title, body, owner= current_user)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/blog?id=' + str(new_post.id))

    return render_template("newpost.html")



@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/index')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect('/login')
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = '/index'
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash('Successfully logged out')
    return redirect('/index')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/index')
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        login_user(user)
        return redirect('/newpost')
    return render_template('signup.html', title='Register', form=form)



if __name__ == '__main__':
    app.run()