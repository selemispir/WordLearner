from flask import render_template, redirect, url_for, flash, session, send_from_directory, request
from flask.views import MethodView
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, oauth
from app.forms import RegisterForm, LoginForm, WordForm, AccountForm, UploadForm, CategoryForm
from app.models import User, Profile, Word, Category

class AboutView(MethodView):
    def get(self):
        return render_template("about.html")


def init_routes(app):

    @app.route("/")
    def home():
        return render_template("index.html")

    app.add_url_rule("/about", view_func=AboutView.as_view("about"))

    @app.route("/register", methods=["GET", "POST"])
    def register():
        form = RegisterForm()

        if form.validate_on_submit():
            existing_user = User.query.filter(
                (User.email == form.email.data) | (User.username == form.username.data)
            ).first()

            if existing_user:
                flash("User with this email or username already exists.")
                return redirect(url_for("register"))

            user = User(
                username=form.username.data,
                email=form.email.data,
                password_hash=generate_password_hash(form.password.data)
            )

            db.session.add(user)
            db.session.commit()

            profile = Profile(user_id=user.id, bio="")
            db.session.add(profile)
            db.session.commit()

            flash("Registration successful. Please log in.")
            return redirect(url_for("login"))

        return render_template("register.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        form = LoginForm()

        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()

            if user and check_password_hash(user.password_hash, form.password.data):
                session["user_id"] = user.id
                session["username"] = user.username
                flash("Login successful.")
                return redirect(url_for("dashboard"))

            flash("Invalid email or password.")

        return render_template("login.html", form=form)
    

    @app.route("/login/github")
    def github_login():
        if not app.config.get("GITHUB_CLIENT_ID") and not os.getenv("GITHUB_CLIENT_ID"):
            flash("GitHub OAuth is not configured.")
            return redirect(url_for("login"))

        redirect_uri = url_for("github_callback", _external=True)
        return oauth.github.authorize_redirect(redirect_uri)


    @app.route("/auth/github/callback")
    def github_callback():
        token = oauth.github.authorize_access_token()
        user_info = oauth.github.get("user").json()

        username = user_info.get("login")
        email = user_info.get("email") or f"{username}@github.local"

        user = User.query.filter_by(email=email).first()

        if not user:
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash("oauth-user")
            )
            db.session.add(user)
            db.session.commit()

            profile = Profile(user_id=user.id, bio="GitHub OAuth user")
            db.session.add(profile)
            db.session.commit()

        session["user_id"] = user.id
        session["username"] = user.username

        flash("Logged in with GitHub.")
        return redirect(url_for("dashboard"))


    @app.route("/login/yandex")
    def yandex_login():
        if not app.config.get("YANDEX_CLIENT_ID") and not os.getenv("YANDEX_CLIENT_ID"):
            flash("Yandex OAuth is not configured.")
            return redirect(url_for("login"))

        redirect_uri = url_for("yandex_callback", _external=True)
        return oauth.yandex.authorize_redirect(redirect_uri)


    @app.route("/auth/yandex/callback")
    def yandex_callback():
        token = oauth.yandex.authorize_access_token()
        user_info = oauth.yandex.get("info").json()

        username = user_info.get("login")
        email = user_info.get("default_email") or f"{username}@yandex.local"

        user = User.query.filter_by(email=email).first()

        if not user:
            user = User(
                username=username,
                email=email,
                password_hash=generate_password_hash("oauth-user")
            )
            db.session.add(user)
            db.session.commit()

            profile = Profile(user_id=user.id, bio="Yandex OAuth user")
            db.session.add(profile)
            db.session.commit()

        session["user_id"] = user.id
        session["username"] = user.username

        flash("Logged in with Yandex.")
        return redirect(url_for("dashboard"))



    @app.route("/dashboard")
    def dashboard():
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))

        return render_template("dashboard.html")

    @app.route("/words")
    def words():
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))

        user_words = Word.query.filter_by(user_id=session["user_id"]).all()
        return render_template("words.html", words=user_words)

    @app.route("/words/add", methods=["GET", "POST"])
    def add_word():
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))

        form = WordForm()

        if form.validate_on_submit():
            word = Word(
                english=form.english.data,
                russian=form.russian.data,
                example_sentence=form.example_sentence.data,
                user_id=session["user_id"]
            )

            db.session.add(word)
            db.session.commit()

            flash("Word added successfully.")
            return redirect(url_for("words"))

        return render_template("word_form.html", form=form, title="Add Word")

    @app.route("/words/edit/<int:word_id>", methods=["GET", "POST"])
    def edit_word(word_id):
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))

        word = Word.query.filter_by(id=word_id, user_id=session["user_id"]).first_or_404()
        form = WordForm(obj=word)

        if form.validate_on_submit():
            word.english = form.english.data
            word.russian = form.russian.data
            word.example_sentence = form.example_sentence.data

            db.session.commit()

            flash("Word updated successfully.")
            return redirect(url_for("words"))

        return render_template("word_form.html", form=form, title="Edit Word")

    @app.route("/words/delete/<int:word_id>", methods=["POST"])
    def delete_word(word_id):
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))

        word = Word.query.filter_by(id=word_id, user_id=session["user_id"]).first_or_404()

        db.session.delete(word)
        db.session.commit()

        flash("Word deleted successfully.")
        return redirect(url_for("words"))

    @app.route("/categories")
    def categories():
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))

        all_categories = Category.query.all()
        return render_template("categories.html", categories=all_categories)

    @app.route("/categories/add", methods=["GET", "POST"])
    def add_category():
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))

        form = CategoryForm()

        if form.validate_on_submit():
            category = Category(name=form.name.data)
            db.session.add(category)
            db.session.commit()

            flash("Category added successfully.")
            return redirect(url_for("categories"))

        return render_template("category_form.html", form=form, title="Add Category")

    @app.route("/categories/edit/<int:category_id>", methods=["GET", "POST"])
    def edit_category(category_id):
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))

        category = Category.query.get_or_404(category_id)
        form = CategoryForm(obj=category)

        if form.validate_on_submit():
            category.name = form.name.data
            db.session.commit()

            flash("Category updated successfully.")
            return redirect(url_for("categories"))

        return render_template("category_form.html", form=form, title="Edit Category")

    @app.route("/categories/delete/<int:category_id>", methods=["POST"])
    def delete_category(category_id):
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))

        category = Category.query.get_or_404(category_id)

        db.session.delete(category)
        db.session.commit()

        flash("Category deleted successfully.")
        return redirect(url_for("categories"))

    @app.route("/account", methods=["GET", "POST"])
    def account():
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))

        user = User.query.get_or_404(session["user_id"])
        form = AccountForm(obj=user)

        if form.validate_on_submit():
            if not check_password_hash(user.password_hash, form.current_password.data):
                flash("Current password is incorrect.")
                return redirect(url_for("account"))

            user.username = form.username.data
            user.email = form.email.data

            if form.new_password.data:
                user.password_hash = generate_password_hash(form.new_password.data)

            db.session.commit()
            session["username"] = user.username

            flash("Account updated successfully.")
            return redirect(url_for("account"))

        return render_template("account.html", form=form)

    @app.route("/upload", methods=["GET", "POST"])
    def upload():
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))

        form = UploadForm()
        uploaded_files = os.listdir(app.config["UPLOAD_FOLDER"])

        if form.validate_on_submit():
            file = form.file.data

            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                file.save(filepath)

                flash("File uploaded successfully.")
                return redirect(url_for("upload"))

        return render_template("upload.html", form=form, files=uploaded_files)

    @app.route("/media/<filename>")
    def media_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)
    
    
    @app.route("/chat")
    def chat():
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))

        return render_template("chat.html", username=session.get("username"))

    
    @app.route("/logout")
    def logout():
        session.clear()
        flash("You have been logged out.")
        return redirect(url_for("home"))
    




