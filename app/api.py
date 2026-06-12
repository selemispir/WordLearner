from flask_restful import Resource, Api
from app.models import Word, User, Category


class WordListResource(Resource):
    def get(self):
        words = Word.query.all()

        return {
            "words": [
                {
                    "id": word.id,
                    "english": word.english,
                    "russian": word.russian,
                    "example_sentence": word.example_sentence,
                    "is_learned": word.is_learned,
                    "is_favorite": word.is_favorite
                }
                for word in words
            ]
        }


class WordDetailResource(Resource):
    def get(self, word_id):
        word = Word.query.get_or_404(word_id)

        return {
            "id": word.id,
            "english": word.english,
            "russian": word.russian,
            "example_sentence": word.example_sentence,
            "is_learned": word.is_learned,
            "is_favorite": word.is_favorite
        }


class UserResource(Resource):
    def get(self, user_id):
        user = User.query.get_or_404(user_id)

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "words_count": len(user.words)
        }


class CategoryListResource(Resource):
    def get(self):
        categories = Category.query.all()

        return {
            "categories": [
                {
                    "id": category.id,
                    "name": category.name
                }
                for category in categories
            ]
        }


def init_api(app):
    api = Api(app)

    api.add_resource(WordListResource, "/api/words")
    api.add_resource(WordDetailResource, "/api/words/<int:word_id>")
    api.add_resource(UserResource, "/api/user/<int:user_id>")
    api.add_resource(CategoryListResource, "/api/categories")