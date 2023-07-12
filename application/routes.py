import os
import secrets
from PIL import Image
from application import app, bcrypt, db
from application.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, CommentForm
from application.models import User, Post, Comments
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required


@app.route('/')
@app.route('/home')
def home():
    """
    Function that routes to/back to Home page
    """
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=5, page=page)
    if current_user.is_authenticated:
        image_file = url_for('static', filename='pics/' + current_user.image_file)
        return render_template('home.html', posts=posts, image_file=image_file)
    return render_template('home.html', posts=posts)


@app.route('/about')
def about():
    """
    Function that routes to/back to About page
    """
    if current_user.is_authenticated:
        image_file = url_for('static', filename='pics/' + current_user.image_file)
        return render_template('about.html', title='About', image_file=image_file)
    return render_template('about.html', title='About')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Function that routes to/back to Register page
    """
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hash_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hash_pw)
        db.session.add(user)
        db.session.commit()
        flash('An account for {} has just been created'.format(
            form.username.data), 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Function that routes to/back to Login page
    """
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('You are now signed in!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('You do not have an account, register first', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    """
    Function that routes to/back to Login page from logging out
    """
    logout_user()
    return redirect(url_for('login'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename)
    pic_fn = random_hex + f_ext
    pic_path = os.path.join(app.root_path, 'static/pics', pic_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(pic_path)

    return pic_fn

@app.route('/account', methods=['GET','POST'])
@login_required
def account():
    """
    Function that routes to Account page
    """
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            pic = save_picture(form.picture.data)
            current_user.image_file = pic
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method =='GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='pics/' + current_user.image_file)
    return render_template('account.html', title='Account', form=form, image_file=image_file)

@app.route('/post/new', methods=['GET','POST'])
@login_required
def new_post():
    """
    Function that routes to a page where user can create new post
    """
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created','success')
        return redirect(url_for('home'))
    image_file = url_for('static', filename='pics/' + current_user.image_file)
    return render_template('create_post.html', title='New Post', form=form, legend='New Post', image_file=image_file)


@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def post(post_id):
    """
    Function that routes to a page where other users can comment on other users posts.
    """
    post = Post.query.get_or_404(post_id)
    post_num = int(post_id)
    form = CommentForm()
    # page = request.args.get('page', 1, type=int)
    comments = Comments.query.filter_by(post_id=post_num).order_by(Comments.date_posted.desc()).all()  # .paginate(per_page=3, page=page)
    image_file = url_for('static', filename='pics/' + current_user.image_file)
    if form.validate_on_submit():
        comment = Comments(content=form.content.data, user_id=current_user.id, post_id=post_num)
        db.session.add(comment)
        db.session.commit()
        flash('Your Comment has been added', 'success')
        return redirect(url_for('home'))
    return render_template('post.html', title=post.title, post=post, image_file=image_file, form=form, comments=comments)


@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    """
    Function that routes to a page where a user can update their own post.
    """
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('You Post has been updated', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post', form=form, post=post, legend='Update Post')

@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    """
    Function that routes a user to delete one uf their own posts.
    """
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)

    post_num = int(post_id)
    comments = Comments.query.filter_by(post_id=post_num).all()
    for comment in comments:
        comment = Comments.query.filter_by(post_id=post_num).first()
        db.session.delete(comment)
        db.session.commit()
    db.session.delete(post)
    db.session.commit()
    flash('You\'re Post has been deleted', 'success')
    return redirect(url_for('home'))


@app.route('/user/<string:username>')
def user_posts(username):
    """
    Function that routes to only one particular users posts
    """
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(per_page=5, page=page)
    image_file = url_for('static', filename='pics/' + current_user.image_file)
    return render_template('user_posts.html', posts=posts, user=user, image_file=image_file)
