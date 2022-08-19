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
        self.database_name = "trivia_test"
        self.database_path = "postgresql://postgres:postgres@{}/{}".format('localhost:5432', self.database_name)
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
        self.assertEqual(data["success"], True)

    def test_get_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertIsNotNone(data["categories"])
    
    def test_delete_question(self):
        res = self.client().delete("/questions/11")
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

    def test_get_categroy_questions(self):
        res = self.client().get("/categories/4/questions")
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertIsNotNone(data["questions"])

    def test_play(self):
        res = self.client().post("/quizzes", json=({
            "previous_questions": [2,3,4],
            "quiz_category": {"id": 4, "type":"History"}
        }))

        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()