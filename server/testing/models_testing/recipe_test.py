import pytest
from sqlalchemy.exc import IntegrityError

from app import app
from models import db, Recipe, User

class TestRecipe:
    '''Recipe in models.py'''

    def test_has_attributes(self):
        '''has attributes title, instructions, and minutes_to_complete.'''

        with app.app_context():

            Recipe.query.delete()
            User.query.delete()  # Also delete users to avoid foreign key issues
            db.session.commit()

            # Create a user first
            user = User(
                username="ChefJohn",
                image_url="https://example.com/chefjohn.jpg",
                bio="I love cooking delicious meals."
            )
            user.password_hash = "supersecretpassword"

            db.session.add(user)
            db.session.commit()

            # Now create a recipe associated with the user
            recipe = Recipe(
                title="Delicious Shed Ham",
                instructions="""Or kind rest bred with am shed then. In""" + \
                    """ raptures building an bringing be. Elderly is detract""" + \
                    """ tedious assured private so to visited. Do travelling""" + \
                    """ companions contrasted it. Mistress strongly remember""" + \
                    """ up to. Ham him compass you proceed calling detract.""" + \
                    """ Better of always missed we person mr. September""" + \
                    """ smallness northward situation few her certainty""" + \
                    """ something.""",
                minutes_to_complete=60,
                user_id=user.id  # Assign the recipe to the created user
            )

            db.session.add(recipe)
            db.session.commit()

            new_recipe = Recipe.query.filter(Recipe.title == "Delicious Shed Ham").first()

            assert new_recipe.title == "Delicious Shed Ham"
            assert new_recipe.instructions == """Or kind rest bred with am shed then. In""" + \
                """ raptures building an bringing be. Elderly is detract""" + \
                """ tedious assured private so to visited. Do travelling""" + \
                """ companions contrasted it. Mistress strongly remember""" + \
                """ up to. Ham him compass you proceed calling detract.""" + \
                """ Better of always missed we person mr. September""" + \
                """ smallness northward situation few her certainty""" + \
                """ something."""
            assert new_recipe.minutes_to_complete == 60
            assert new_recipe.user_id == user.id  # Check that recipe is associated with the user

    def test_requires_title(self):
        '''requires each record to have a title.'''

        with app.app_context():

            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            # Create a user
            user = User(
                username="ChefJohn",
                image_url="https://example.com/chefjohn.jpg",
                bio="I love cooking delicious meals."
            )
            user.password_hash = "supersecretpassword"

            db.session.add(user)
            db.session.commit()

            # Try creating a recipe without a title
            recipe = Recipe(user_id=user.id)  # No title provided
            
            with pytest.raises(IntegrityError):
                db.session.add(recipe)
                db.session.commit()

    def test_requires_50_plus_char_instructions(self):
        with app.app_context():

            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            # Create a user
            user = User(
                username="ChefJohn",
                image_url="https://example.com/chefjohn.jpg",
                bio="I love cooking delicious meals."
            )
            user.password_hash = "supersecretpassword"

            db.session.add(user)
            db.session.commit()

            # Try creating a recipe with too short instructions
            with pytest.raises( (IntegrityError, ValueError) ):
                recipe = Recipe(
                    title="Generic Ham",
                    instructions="idk lol",  # Instructions too short
                    user_id=user.id
                )
                db.session.add(recipe)
                db.session.commit()
