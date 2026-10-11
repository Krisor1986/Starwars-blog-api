import os

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.orm import configure_mappers
from werkzeug.security import generate_password_hash

from models import (
    Character,
    FavoriteCharacter,
    FavoritePlanet,
    FavoriteVehicle,
    Planet,
    User,
    Vehicle,
    db,
)


class UserAdmin(ModelView):
    form_excluded_columns = (
        "favorite_planets",
        "favorite_characters",
        "favorite_vehicles",
    )
    column_exclude_list = ("password",)
    column_details_exclude_list = ("password",)
    column_export_exclude_list = ("password",)

    def on_model_change(self, form, model, is_created):
        if is_created or not model.password.startswith(("scrypt:", "pbkdf2:")):
            model.password = generate_password_hash(model.password)


class PlanetAdmin(ModelView):
    form_excluded_columns = ("characters", "favorites", "properties")


class CharacterAdmin(ModelView):
    form_excluded_columns = ("favorites", "properties")


def setup_admin(app):
    configure_mappers()
    app.secret_key = os.environ.get("FLASK_APP_KEY", "local-development-key")

    admin = Admin(
        app,
        name="Star Wars Admin",
        template_mode="bootstrap3",
    )

    admin.add_view(UserAdmin(User, db.session))
    admin.add_view(PlanetAdmin(Planet, db.session))
    admin.add_view(CharacterAdmin(Character, db.session))
    admin.add_view(ModelView(FavoritePlanet, db.session))
    admin.add_view(ModelView(FavoriteCharacter, db.session))
    admin.add_view(CharacterAdmin(Vehicle, db.session))
    admin.add_view(ModelView(FavoriteVehicle, db.session))
