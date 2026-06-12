from app import db
from datetime import datetime

word_category = db.Table(
    "word_category",
    db.Column("word_id", db.Integer, db.ForeignKey("word.id")),
    db.Column("category_id", db.Integer, db.ForeignKey("category.id"))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    profile = db.relationship("Profile", back_populates="user", uselist=False)
    words = db.relationship("Word", back_populates="user")


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bio = db.Column(db.String(300), default="")
    avatar = db.Column(db.String(200), default="")

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True)
    user = db.relationship("User", back_populates="profile")


class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    english = db.Column(db.String(100), nullable=False)
    russian = db.Column(db.String(100), nullable=False)
    example_sentence = db.Column(db.String(300))
    is_learned = db.Column(db.Boolean, default=False)
    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", back_populates="words")

    categories = db.relationship(
        "Category",
        secondary=word_category,
        back_populates="words"
    )

    comments = db.relationship("Comment", back_populates="word")


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    words = db.relationship(
        "Word",
        secondary=word_category,
        back_populates="categories"
    )


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    word_id = db.Column(db.Integer, db.ForeignKey("word.id"))
    word = db.relationship("Word", back_populates="comments")