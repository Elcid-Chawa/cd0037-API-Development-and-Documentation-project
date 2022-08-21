import os
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    # Function to formart db Objects to json objects
    def formatted_objects(db_object):
        return [obj.format() for obj in db_object]

    # Strip questions by page numbers
    def strip_pages(page, questions):
        start = (page -1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        return questions[start:end]

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add("Acces-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Allow-Control-Allow-Headers", "GET, POST, PATCH, DELETE, OPTIONS")
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories", methods=["GET"])
    def get_categories():
        categories = Category.query.all()
        format_categories = formatted_objects(categories)
        return jsonify({
            "success": True,
            "categories": {
                cat["id"]:cat["type"] for cat in format_categories
            }
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route("/questions", methods=["GET"])
    def get_questions():
        pages = request.args.get("page", 1, type=int)
        questions = Question.query.all()
        format_questions = formatted_objects(questions)
        categories = formatted_objects(Category.query.all())
        stripped_questions = strip_pages(pages, format_questions)

        if len(stripped_questions) == 0:
            abort(404)
        return jsonify({
            "success": True,
            "questions": stripped_questions,
            "categories": {
                            cat["id"]:cat["type"] for cat in categories
                        },
            "currentCategory": None,
            "totalQuestions": len(format_questions)
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:q_id>", methods=["DELETE"])
    def delete_question(q_id):
        try:
            question = Question.query.get(q_id)
            
            question.delete()

            return jsonify({
                "success": True,
                "message": f"Question {q_id} has been deleted"
            })

        except:
            abort(404)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=["POST"])
    def add_question():
        body = request.get_json()
        try:
            question = body["question"]
            answer = body["answer"]
            category = body["category"]
            difficulty = body["difficulty"]
            newQuestion = Question(question=question, answer=answer, 
                                   category=category, difficulty=difficulty)

            newQuestion.insert()

            return jsonify({
                "success": True,
                "message": "Added new Question",
                "total_questions": len(Question.query.all())
            })
        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/search", methods=["POST"])
    def search_question():
        searchTerm = request.get_json()

        try:
            search_term = searchTerm["searchTerm"]
            question = Question.query.filter(
                Question.question.ilike(f"%{search_term}%")
            ). all()

            if question == None:
                abort(404)
            
            return jsonify({
                "success": True,
                "questions": formatted_objects(question)
            })
        except:
            abort(500)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:cid>/questions", methods=["GET"])
    def get_categroy_questions(cid):
        try:
            category = Category.query.get(cid)
            formated_cat = category.format()
            category_questions = Question.query.filter(
                                        Question.category == formated_cat["id"]
                                        ).all()
            if category_questions is None:
                abort(404)

            questions = formatted_objects(category_questions)

            return jsonify({
                "success": True,
                "questions": questions,
                "totalQuestions": len(questions),
                "currentCategory": formated_cat["type"]
            }), 200
        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route("/quizzes", methods=["POST"])
    def play():
        body = request.get_json()

        try:
            previous_question = body["previous_questions"]
            category = body["quiz_category"]
            questions = formatted_objects(Question.query.all()) 
            question_category = formatted_objects(
                                    Question.query
                                            .filter_by(category=category["id"])
                                            .all()
                                        )

            answered_quesions = Question.query.filter(
                    Question.id.in_((previous_question))
                    ).all()
            unanswered_quesions = Question.query.filter(
                    Question.id.notin_((previous_question))
                    ).all()

            unanswered_quesion_category = Question.query.filter(
                    Question.id.notin_((previous_question))
                    ).filter_by(category = category["id"]) \
                    .all()

            if (category["id"] == 0) and (previous_question == []):
                question = random.choice(questions)
            elif (category["id"] != 0) and (previous_question == []):
                question = random.choice(question_category)
            elif (previous_question != []) and (category["id"] == 0):
                question = random.choice(formatted_objects(unanswered_quesions))
            else:
                question = random.choice(formatted_objects(unanswered_quesion_category))

            return jsonify({
                "success": True,
                "question": question
            })
        except:
            abort(422)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Error: Resource not found"
        }), 404

    @app.errorhandler(405)
    def unallowed_method(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "Error: Method not allowed on the url"
        })

    @app.errorhandler(422)
    def unresponsive(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Error: Response not processed or unresponsive"
        })

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Error: Internal server error"
        })

    return app

