"""Blogly application."""

import datetime

from flask import Flask, redirect, render_template, request, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True


connect_db(app)

# Use once to setup the database using the models
def run_db_createall():
    with app.app_context():
        db.create_all()


app.config['SECRET_KEY'] = "Secret Secret Secret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)


@app.route("/")
def root_route():
    """ Homepage"""
    return redirect("/users")

# Users Route

@app.route("/users")
def users_route():
    """  List of Users"""
    users = User.query.order_by(User.last_name).all()

    return render_template("home.html", users = users)

@app.route("/users/new", methods=["GET"])
def create_user_form():
    """ Create a new User"""

    return render_template("new_user.html")


@app.route("/users/new", methods=["POST"])
def create_user_db():
    """ Create a new User"""
    new_user = User(
        first_name = request.form['first_name'],
        last_name = request.form['last_name'],
        image_url = request.form['image_url'] or '/static/img/default.jpg')

    db.session.add(new_user)
    db.session.commit()

    return redirect("/users")


@app.route("/users/<int:user_id>")
def show_user_details(user_id):

    user = User.query.get_or_404(user_id)

    user_posts = Post.query.filter(Post.user_id == user.id)

    return render_template("user_detail.html", user=user, posts=user_posts)


@app.route("/users/<int:user_id>/edit", methods=["GET"])
def edit_user_details_form(user_id):
    
    user = User.query.get_or_404(user_id)

    return render_template("user_detail_edit_form.html", user=user)


@app.route("/users/<int:user_id>/edit", methods=["POST"])
def edit_user_details(user_id):

    user = User.query.get_or_404(user_id)
    user.first_name = request.form["first_name"]
    user.last_name = request.form["last_name"]
    user.image_url = request.form['image_url'] or '/static/img/default.jpg'

    db.session.add(user)
    db.session.commit()

    return redirect(f"/users/{user.id}")

@app.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    
    user = User.query.get_or_404(user_id)
    
    db.session.delete(user)
    db.session.commit()

    return redirect("/users")


# Posts Route

@app.route("/users/<int:user_id>/posts/new")
def new_post_show_form(user_id):
    """ Displays the form to submit a post"""
    curr_user = User.query.get_or_404(user_id)
    return render_template("new_post_form.html", user=curr_user)


@app.route("/users/<int:user_id>/posts/new", methods=["POST"])
def new_post_handle(user_id):
    """ Handles the new post """

    new_post = Post(
        title = request.form["title"],
        content = request.form["content"],
        user_id = user_id
    )

    db.session.add(new_post)
    db.session.commit()

    flash("New Post Created")
    return redirect(f"/users/{user_id}")

@app.route("/posts/<int:post_id>")
def get_post(post_id):
    """ Shows more details about the selected post"""

    curr_post = Post.query.get_or_404(post_id)
    post_user = User.query.get_or_404(curr_post.user_id)

    return render_template("post.html", post = curr_post, user = post_user)


@app.route("/posts/<int:post_id>/edit")
def edit_post_form(post_id):
    post_edit = Post.query.get_or_404(post_id)

    return render_template("edit_post.html", post = post_edit)


@app.route("/posts/<int:post_id>/edit", methods=["POST"])
def edit_post_submit(post_id):

    curr_post = Post.query.get_or_404(post_id)
    curr_post.title = request.form["title"]
    curr_post.content = request.form["content"]
    curr_post.created_at = datetime.datetime.now()

    db.session.add(curr_post)
    db.session.commit()

    return redirect("/posts/{{curr_post.id}}")



@app.route("/posts/<int:post_id>/delete")
def delete_post(post_id):

    curr_post = Post.query.get_or_404(post_id)

    db.session.delete(curr_post)
    db.session.commit()

    flash("Post Deleted")

    return redirect(f"/users/{curr_post.user_id}")

