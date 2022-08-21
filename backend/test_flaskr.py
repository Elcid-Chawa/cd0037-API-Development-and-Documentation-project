import os
import unittest
import json
from urllib import response
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.DB_HOST = os.getenv('DB_HOST', '127.0.0.1:5432')
        self.DB_USER = os.getenv('DB_USER', 'postgres')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
        self.database_name = os.getenv('DB_NAME', 'trivia_test')
        self.database_path = "postgresql://{}:{}@{}/{}".format(self.DB_USER, self.DB_PASSWORD, self.DB_HOST, self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)\

    def test_get_categories_error(self):
        res = self.client().get("/categories/1")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["success"], False)

    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertIsNotNone(data["categories"])

    def test_get_questions_error(self):
        res = self.client().get("/questions/1")
        data = json.loads(res.data)
        self.assertEqual(data["error"], 405)
        self.assertEqual(data["success"], False)

    def test_delete_question(self):
        res = self.client().delete("/questions/10")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["message"], "Question 11 has been deleted")

    def test_error_delete_question(self):
        res = self.client().delete("/questions/100")
        data = json.loads(res.data)
        self.assertEqual(data["error"], 404)
        self.assertFalse(data["success"])

    def test_add_question(self):
        res = self.client().post("/questions", json=({
                        "question": "Who was the President of USA in 2019",
                        "answer": "Donald Trump",
                        "difficulty":"2",
                        "category":"4"
                    }))
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])

    def test_error_add_question_unresponsive(self):
        res = self.client().post("/questions", json=({
                        "questions": "Who was the President of USA in 2019",
                        "answer": "Donald Trump",
                        "difficulty":"2",
                        "category":"4"
                    }))
        data = json.loads(res.data)
        
        self.assertEqual(data["error"], 422)
        self.assertFalse(data["success"])

    def test_search_question(self):
        res = self.client().post("/search", json=({"searchTerm":"How"}))

        data = json.loads(res.data)
        self.assertEquals(res.status_code, 200)
        self.assertTrue(data["success"])

    def test_search_question(self):
        res = self.client().post("/search", json=({"searchterm":"How"}))

        data = json.loads(res.data)
        self.assertEqual(data["error"], 500)
        self.assertFalse(data["success"])

    def test_get_categroy_questions(self):
        res = self.client().get("/categories/4/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIsNotNone(data["questions"])

    def test_get_categroy_questions_error(self):
        res = self.client().get("/categories/7/questions")
        data = json.loads(res.data)
        self.assertEqual(data["error"], 422)
        self.assertFalse(data["success"])

    def test_play(self):
        res = self.client().post("/quizzes", json=({
            "previous_questions": [2,3,4],
            "quiz_category": {"id": 4, "type":"History"}
        }))

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])

    def test_play_error(self):
        res = self.client().post("/quizzes", json=({
            "previous_questions": [2,3,4],
            "quiz_category": []
        }))

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(data["success"])
        self.assertEqual(data["error"], 422)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()