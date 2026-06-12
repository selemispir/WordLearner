from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import User, Profile, Word, Category, Comment

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    user = User(
        username="demo",
        email="demo@example.com",
        password_hash=generate_password_hash("123456")
    )

    db.session.add(user)
    db.session.commit()

    profile = Profile(
        bio="Demo user for testing WordLearner.",
        avatar="",
        user_id=user.id
    )

    food = Category(name="Food")
    animals = Category(name="Animals")
    travel = Category(name="Travel")

    db.session.add_all([profile, food, animals, travel])
    db.session.commit()

    word1 = Word(
        english="apple",
        russian="яблоко",
        example_sentence="I eat an apple every day.",
        user_id=user.id
    )
    word1.categories.append(food)

    word2 = Word(
        english="cat",
        russian="кот",
        example_sentence="The cat is sleeping.",
        user_id=user.id
    )
    word2.categories.append(animals)

    word3 = Word(
        english="ticket",
        russian="билет",
        example_sentence="I bought a train ticket.",
        user_id=user.id
    )
    word3.categories.append(travel)

    db.session.add_all([word1, word2, word3])
    db.session.commit()

    comment = Comment(
        text="This is a useful word.",
        word_id=word1.id
    )

    db.session.add(comment)
    db.session.commit()

    print("Database seeded successfully.")
    print("Login email: demo@example.com")
    print("Password: 123456")