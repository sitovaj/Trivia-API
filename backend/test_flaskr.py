import os
import unittest
import json
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
        self.database_path = "postgres://{}:{}@{}/{}".format('student', 'student','localhost:5432', self.database_name)

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
    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        print(res)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))                

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        print(res)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_404_request_category_beyond_valid_id(self):
        res = self.client().get('/categories/999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_get_questions_by_categories(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        print(res)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))   

    def test_404_fail_get_questions_by_categories(self):
        res = self.client().get('/categories/9/questions')
        data = json.loads(res.data)
        print(res)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

        
    def test_get_questions_search_with_results(self):
        res = self.client().post('/questions', json={'searchTerm': 'title'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 2)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['categories']))     

    def test_get_questions_search_without_results(self):
        res = self.client().post('/questions', json={'searchTerm': 'applejacks'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 0)
        self.assertTrue(len(str(data['total_questions'])),0)
        self.assertTrue(len(data['categories']))   

        self.new_book = {
            'title': 'Anansi Boys',
            'author': 'Neil Gaiman',
            'rating': 5
        }

    def test_create_new_question(self):
        res = self.client().post('/questions', json={
            'question': 'Name scientist that presented gravitation term',
            'answer': 'Newton',
            'difficulty': '2',
            'category': '1'
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)


    def test_405_if_question_creation_not_allowed(self):
        res = self.client().post('/questions/45', json={
            'question': 'Name scientist that presented gravitation term',
            'answer': 'Newton',
            'difficulty': 'Test',
            'category': '1'
        })
        data = json.loads(res.data)
       
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method not allowed')

    def test_422_if_new_question_has_wrong_category(self):
        res = self.client().post('/questions', json={
            'question': 'Name scientist that presented gravitation term',
            'answer': 'TEST422',
            'difficulty': '2',
            'category': '9999'
        })
        data = json.loads(res.data)
       
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Entity, check your request')

    def test_delete_question(self):
        self.client().post('/questions', json={
            'question': 'Name scientist that presented gravitation term',
            'answer': 'TEST',
            'difficulty': '2',
            'category': '1'
        })
        new_question_id = Question.query.order_by(Question.id.desc()).first().id

        res = self.client().delete('/questions/'+ str(new_question_id))
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], new_question_id)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))   

    def test_400_fail_delete_book_doesnt_exist(self):
        res = self.client().delete('/questions/791512')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad request, server couldnt understand it')

    def test_quiz_get_Science_question(self): 
        category_id = 1
        res = self.client().post('/quizzes', json={
            'quiz_category':  {
                # 'type': 'Science', #doesn't matter what is the type
                'id': category_id
            },
            'previous_questions': [20, 21] #can be id of any category questions
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['question']))
        self.assertEqual(data['question']['category'], category_id)
        requested_question = Question.query.get(data['question']['id'])
        self.assertEqual(data['question']['category'], requested_question.category)

    def test_quiz_get_question_of_Any_category(self): 
        category_id = 0
        res = self.client().post('/quizzes', json={
            'quiz_category':  {
                'id': category_id
            },
            'previous_questions': [20, 21]
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['question']))
        self.assertNotEqual(data['question']['category'], category_id)
        requested_question = Question.query.get(data['question']['id'])
        self.assertEqual(data['question']['category'], requested_question.category)

    def test_quiz_no_more_Science_questions_left(self): 
        category_id = 2
        res = self.client().post('/quizzes', json={
            'quiz_category':  {
                'id': category_id
            },
            'previous_questions': [16, 17, 18, 19] 
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question'], None)

    def test_404_play_quiz_not_enough_info(self): 
        category_id = 1
        res = self.client().post('/quizzes', json={
            'quiz_category':  {
                'id': category_id
            }
            # ,
            # 'previous_questions': [20, 21] #forfot to put previous_question
        })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_422_play_quiz_wrong_request(self): 
        category_id = 1
        res = self.client().post('/quizzes'
        #, json={ #forgot to add json at all
        #     'quiz_category':  {
        #         'id': category_id
        #     }
        #     ,
        #     'previous_questions taka': [20, 21] 
        # }
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Entity, check your request')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()