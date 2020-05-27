import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)   #with request.args get dictionary, with get(key, default=None, type=None) Return the default value if the requested data doesn’t exist 
  start = (page - 1) * QUESTIONS_PER_PAGE #page is 1 (as default value), so start = 0
  end = start + QUESTIONS_PER_PAGE
  formatted_questions = [question.format() for question in selection] # all books formated in format described in model.py
  current_question = formatted_questions[start:end]

  return current_question

def list_categories():
  categories = {}
  for category in Category.query.all():
      categories[category.id] = category.type
  return categories

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
'''
  @app.route('/categories')
  def get_list_categories():
    return jsonify({
        'success': True,
        'categories': list_categories()
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  
  @app.route('/questions', methods=['GET', 'POST'])
  def get_list_questions():
    if request.method=='GET':
      selection = Question.query.order_by('id').all() #flask query for all books
      current_questions = paginate_questions(request, selection)

      if len(current_questions) == 0: 
          abort(404)  #to throw error when page doesn't have books to display on page

      return jsonify({
          'success': True,
          'questions': current_questions, 
          'total_questions': len(Question.query.all()),
          'current_category': None,
          'categories': list_categories()
      })

    if request.method=='POST':

      body = request.get_json() #get question information
      new_question_txt = body.get('question') #from request get necessary info on new book, if it's not given, then it'll be None
      new_answer = body.get('answer')
      new_category = body.get('category')
      new_difficulty = body.get('difficulty')
      search = body.get('searchTerm', None) #search for a question
      try:

        if search:
            selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
            current_questions = paginate_questions(request, selection)

            return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection.all()),
            'current_category': None,
            'categories': list_categories()
            })

        else: 
          new_question = Question(question=new_question_txt, answer=new_answer, category=new_category, difficulty=new_difficulty)
          new_question.insert()

        return jsonify ({
            'success': True
        })
      except:
        abort(422)

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
      try:
          question = Question.query.filter(Question.id == question_id).one_or_none() #find book by id
          if question is None:
              abort(404)        
          question.delete()
          selection = Question.query.order_by('id').all() #flask query for all books
          current_questions = paginate_questions(request, selection)

          return jsonify ({
              'success': True,
              'deleted': question_id,
              'questions': current_questions, #show only BOOKS_PER_SHELF (8) books per page
              'total_questions': len(Question.query.all()),
              'categories': list_categories()
          })
      except:
          abort(400)
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  
  # '/questions' method 'POST' - handled together with GET
  
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  # '/questions' method 'POST' - hadled together with GET
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
    selection = Question.query.filter(Question.category==str(category_id)).all() #flask query for all books
    current_questions = paginate_questions(request, selection)
    category = Category.query.filter(Category.id==category_id).one_or_none()
    if len(current_questions) == 0: 
        abort(404)  #to thow error when page doesn't have books to display on page

    return jsonify({
        'success': True,
        'questions': current_questions, 
        'total_questions': len(selection),
        'current_category': category.id,
        'categories': list_categories()
    })
  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_question_for_quiz():
    if request.data:
      body = request.get_json()
      if (('quiz_category' in body and 'id' in body['quiz_category']) 
      and 'previous_questions' in body):
        if body['quiz_category']['id']==0:
          questions_query = Question.query.filter(Question.id.notin_(body["previous_questions"])).all()
        else:
          questions_query = Question.query.filter_by(category=body['quiz_category']['id']
          ).filter(Question.id.notin_(body["previous_questions"])).all()
        length_of_available_question = len(questions_query)
        if length_of_available_question > 0:
          result = {
              "success": True,
              "question": Question.format(questions_query[random.randrange(0,length_of_available_question)])
          }
        else:
            result = {
                "success": True,
                "question": None
            }
        return jsonify(result)
      abort(404)
    abort(422)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          "success": False, 
          "error": 404,
          "message": "Not found"
          }), 404

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success": False, 
          "error": 400,
          "message": "Bad request, server couldnt understand it"
          }), 400

  @app.errorhandler(422)
  def unprocessable_entity(error):
      return jsonify({
          "success": False, 
          "error": 422,
          "message": "Unprocessable Entity, check your request"
          }), 422

  @app.errorhandler(405)
  def not_allowed(error):
      return jsonify({
          "success": False, 
          "error": 405,
          "message": "Method not allowed"
          }), 405

  @app.errorhandler(500)
  def not_allowed(error):
      return jsonify({
          "success": False, 
          "error": 500,
          "message": " Internal Server Error, check your request"
          }), 500

  return app

    