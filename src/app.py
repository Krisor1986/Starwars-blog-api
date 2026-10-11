"""REST API for the Star Wars blog exercise."""

import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException

from admin import setup_admin
from models import Character, FavoriteCharacter, FavoritePlanet, Planet, User, Vehicle, FavoriteVehicle, db
from utils import APIException
from seed import register_seed_command

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///starwars.db"
).replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["CURRENT_USER_ID"] = os.getenv("CURRENT_USER_ID", "1")

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)
register_seed_command(app)


@app.errorhandler(APIException)
def handle_api_error(error):
    return jsonify({"error": error.message}), error.status_code


@app.errorhandler(HTTPException)
def handle_http_error(error):
    if request.path.startswith("/admin"):
        return error
    return jsonify({"error": error.description}), error.code


def get_current_user():
    # User selection for this exercise; this does not authenticate the caller.
    user_id = request.headers.get("X-User-ID", str(app.config["CURRENT_USER_ID"]))
    if not user_id.isascii() or not user_id.isdecimal() or int(user_id) < 1:
        raise APIException("X-User-ID must be a positive integer", 400)
    user = db.session.get(User, int(user_id))
    if user is None:
        raise APIException("User not found. Create the user in Flask Admin.", 404)
    return user


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "name": "Star Wars Blog API",
        "admin": "/admin/",
        "resources": ["/people", "/planets", "/vehicles", "/users", "/users/favorites"],
    }), 200


@app.route("/people", methods=["GET"])
def get_people():
    people = db.session.execute(db.select(Character).order_by(Character.id)).scalars()
    return jsonify([person.serialize() for person in people]), 200


@app.route("/people/<int:people_id>", methods=["GET"])
def get_person(people_id):
    person = db.session.get(Character, people_id)
    if person is None:
        raise APIException("Character not found", 404)
    return jsonify(person.serialize()), 200


@app.route("/planets", methods=["GET"])
def get_planets():
    planets = db.session.execute(db.select(Planet).order_by(Planet.id)).scalars()
    return jsonify([planet.serialize() for planet in planets]), 200


@app.route("/planets/<int:planet_id>", methods=["GET"])
def get_planet(planet_id):
    planet = db.session.get(Planet, planet_id)
    if planet is None:
        raise APIException("Planet not found", 404)
    return jsonify(planet.serialize()), 200


@app.route("/users", methods=["GET"])
def get_users():
    users = db.session.execute(db.select(User).order_by(User.id)).scalars()
    return jsonify([user.serialize() for user in users]), 200


@app.route("/users/favorites", methods=["GET"])
def get_favorites():
    user = get_current_user()
    return jsonify({
        "user_id": user.id,
        "planets": [favorite.planet.serialize() for favorite in user.favorite_planets],
        "people": [favorite.character.serialize() for favorite in user.favorite_characters],
        "vehicles": [favorite.vehicle.serialize() for favorite in user.favorite_vehicles],
    }), 200


def manage_favorite(resource_model, favorite_model, resource_id, id_field):
    user = get_current_user()
    if db.session.get(resource_model, resource_id) is None:
        raise APIException("Resource not found", 404)

    keys = {"user_id": user.id, id_field: resource_id}
    favorite = db.session.get(favorite_model, keys)
    if request.method == "POST":
        if favorite is not None:
            raise APIException("Favorite already exists", 409)
        db.session.add(favorite_model(**keys))
        status, message = 201, "Favorite added"
    else:
        if favorite is None:
            raise APIException("Favorite not found", 404)
        db.session.delete(favorite)
        status, message = 200, "Favorite removed"

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise APIException("Favorite could not be saved", 409)
    return jsonify({"message": message, **keys}), status


@app.route("/favorite/planet/<int:planet_id>", methods=["POST", "DELETE"])
def manage_favorite_planet(planet_id):
    return manage_favorite(Planet, FavoritePlanet, planet_id, "planet_id")


@app.route("/favorite/people/<int:people_id>", methods=["POST", "DELETE"])
def manage_favorite_person(people_id):
    return manage_favorite(Character, FavoriteCharacter, people_id, "character_id")


@app.route("/vehicles", methods=["GET"])
def get_vehicles():
    vehicles = db.session.execute(db.select(Vehicle).order_by(Vehicle.id)).scalars()
    return jsonify([vehicle.serialize() for vehicle in vehicles]), 200


@app.route("/vehicles/<int:vehicle_id>", methods=["GET"])
def get_vehicle(vehicle_id):
    vehicle = db.session.get(Vehicle, vehicle_id)
    if vehicle is None:
        raise APIException("Vehicle not found", 404)
    return jsonify(vehicle.serialize()), 200


@app.route("/favorite/vehicle/<int:vehicle_id>", methods=["POST", "DELETE"])
def manage_favorite_vehicle(vehicle_id):
    return manage_favorite(Vehicle, FavoriteVehicle, vehicle_id, "vehicle_id")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "3001")), debug=False)
