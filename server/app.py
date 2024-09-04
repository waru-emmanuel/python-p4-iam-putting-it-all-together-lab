#!/usr/bin/env python3

from flask import request, session, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        image_url = data.get('image_url')
        bio = data.get('bio')

        if not username or not password:
            return {"errors": ["Username and password are required"]}, 422

        try:
            user = User(username=username, image_url=image_url, bio=bio)
            user.password_hash = password  # Hash the password
            db.session.add(user)
            db.session.commit()

            # Save the user's ID in the session
            session['user_id'] = user.id

            # Return a JSON response with the user's details
            return {
                "id": user.id,
                "username": user.username,
                "image_url": user.image_url,
                "bio": user.bio
            }, 201

        except IntegrityError:
            db.session.rollback()
            return {"errors": ["Username already taken"]}, 422
        
        except Exception as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 500



class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if user_id:
            user = db.session.get(User, user_id)  # Use session.get instead of query.get
            if user:
                return {
                    "id": user.id,
                    "username": user.username,
                    "image_url": user.image_url,
                    "bio": user.bio
                }, 200
        return {"errors": ["Not logged in"]}, 401

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return {"errors": ["Username and password are required"]}, 422

        user = User.query.filter_by(username=username).first()
        if user and user.authenticate(password):
            session['user_id'] = user.id
            return {
                "id": user.id,
                "username": user.username,
                "image_url": user.image_url,
                "bio": user.bio
            }, 200
        return {"errors": ["Invalid username or password"]}, 401

class Logout(Resource):
    def delete(self):
        if 'user_id' in session and session['user_id'] is not None:
            session.pop('user_id', None)
            return '', 204
        return {"errors": ["Not logged in"]}, 401

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {"errors": ["Unauthorized"]}, 401

        try:
            recipes = Recipe.query.filter_by(user_id=user_id).all()
            recipes_list = [{
                "id": recipe.id,
                "title": recipe.title,
                "instructions": recipe.instructions,
                "minutes_to_complete": recipe.minutes_to_complete,
                "user": {
                    "id": recipe.user.id,
                    "username": recipe.user.username,
                    "image_url": recipe.user.image_url,
                    "bio": recipe.user.bio
                }
            } for recipe in recipes]

            return recipes_list, 200
        except Exception as e:
            return {"errors": [str(e)]}, 500

    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return {"errors": ["Unauthorized"]}, 401

        data = request.get_json()
        title = data.get('title')
        instructions = data.get('instructions')
        minutes_to_complete = data.get('minutes_to_complete')

        if not title or not instructions or len(instructions) < 50:
            return {"errors": ["Title and instructions are required, and instructions must be at least 50 characters long"]}, 422

        user = User.query.get(user_id)
        if not user:
            return {"errors": ["User not found"]}, 404

        try:
            recipe = Recipe(title=title, instructions=instructions, minutes_to_complete=minutes_to_complete, user=user)
            db.session.add(recipe)
            db.session.commit()
            return {
                "id": recipe.id,
                "title": recipe.title,
                "instructions": recipe.instructions,
                "minutes_to_complete": recipe.minutes_to_complete,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "image_url": user.image_url,
                    "bio": user.bio
                }
            }, 201
        except IntegrityError:
            db.session.rollback()
            return {"errors": ["There was an issue saving your recipe."]}, 422


# Adding resources to the API
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
