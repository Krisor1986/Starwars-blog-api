"""Exercise the real HTTP API with an isolated, migrated SQLite database."""

import json
import os
from pathlib import Path
import sys
import tempfile
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask_migrate import upgrade
from werkzeug.security import check_password_hash
from werkzeug.serving import make_server

ROOT = Path(__file__).resolve().parents[1]
DATABASE = tempfile.TemporaryDirectory(prefix="starwars-api-test-")
os.environ["DATABASE_URL"] = f"sqlite:///{DATABASE.name}/test.db"
os.environ["CURRENT_USER_ID"] = "1"
sys.path.insert(0, str(ROOT / "src"))

from app import app
from models import User, Vehicle, db


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with app.app_context():
            upgrade(directory=str(ROOT / "migrations"))
        cls.server = make_server("127.0.0.1", 0, app)
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        for index in (1, 2):
            status, _ = cls.call("POST", "/admin/user/new/", form={
                "email": f"user{index}@example.test", "password": "test-password",
                "is_active": "y",
            })
            if status != 200:
                raise AssertionError(f"User creation failed: {status}")
        cls.call("POST", "/admin/planet/new/", form={
            "name": "Tatooine", "climate": "arid", "terrain": "desert",
            "population": "200000",
        })
        cls.call("POST", "/admin/character/new/", form={
            "name": "Luke Skywalker", "gender": "male", "height": "172",
            "mass": "77", "birth_year": "19BBY", "homeworld": "1",
        })

        cls.call("POST", "/admin/vehicle/new/", form={
            "name": "Sand Crawler", "model": "Digger Crawler",
            "manufacturer": "Corellia Mining Corporation", "passengers": "30",
        })

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join()
        cls.server.server_close()
        with app.app_context():
            db.session.remove()
            db.engine.dispose()
        DATABASE.cleanup()

    @classmethod
    def call(cls, method, path, headers=None, form=None):
        data = urlencode(form).encode() if form is not None else None
        request = Request(cls.base_url + path, data=data, method=method, headers=headers or {})
        try:
            response = urlopen(request, timeout=10)
        except HTTPError as error:
            response = error
        with response:
            body = response.read().decode()
            if "application/json" in response.headers.get("Content-Type", ""):
                body = json.loads(body)
            return response.status, body

    def test_resource_lists_and_details(self):
        for resource, name in (("people", "Luke Skywalker"), ("planets", "Tatooine"), ("vehicles", "Sand Crawler")):
            status, items = self.call("GET", f"/{resource}")
            self.assertEqual(status, 200)
            self.assertEqual(items[0]["name"], name)
            status, item = self.call("GET", f"/{resource}/1")
            self.assertEqual(status, 200)
            self.assertEqual(item["name"], name)
            self.assertEqual(self.call("GET", f"/{resource}/999999")[0], 404)
        self.assertEqual(self.call("GET", "/people/1")[1]["homeworld"], "Tatooine")

    def test_users_and_password_hashes(self):
        status, users = self.call("GET", "/users")
        self.assertEqual(status, 200)
        self.assertEqual(len(users), 2)
        self.assertTrue(all("password" not in user for user in users))
        with app.app_context():
            self.assertTrue(check_password_hash(db.session.get(User, 1).password, "test-password"))

    def test_favorite_lifecycle_and_user_isolation(self):
        for kind, result_key in (("planet", "planets"), ("people", "people"), ("vehicle", "vehicles")):
            path = f"/favorite/{kind}/1"
            self.assertEqual(self.call("POST", path)[0], 201)
            self.assertEqual(self.call("POST", path)[0], 409)
            status, favorites = self.call("GET", "/users/favorites")
            self.assertEqual(status, 200)
            self.assertEqual(len(favorites[result_key]), 1)
            second_user = {"X-User-ID": "2"}
            self.assertEqual(self.call("GET", "/users/favorites", second_user)[1][result_key], [])
            self.assertEqual(self.call("DELETE", path, second_user)[0], 404)
            self.assertEqual(self.call("POST", path, second_user)[0], 201)
            self.assertEqual(self.call("DELETE", path)[0], 200)
            self.assertEqual(self.call("DELETE", path)[0], 404)
            self.assertEqual(len(self.call("GET", "/users/favorites", second_user)[1][result_key]), 1)
            self.assertEqual(self.call("DELETE", path, second_user)[0], 200)

    def test_invalid_user_and_missing_resources(self):
        for value in ("abc", "0", "-1", "1.5"):
            self.assertEqual(self.call("GET", "/users/favorites", {"X-User-ID": value})[0], 400)
        self.assertEqual(self.call("GET", "/users/favorites", {"X-User-ID": "999999"})[0], 404)
        for kind in ("people", "planet", "vehicle"):
            for method in ("POST", "DELETE"):
                self.assertEqual(self.call(method, f"/favorite/{kind}/999999")[0], 404)

    def test_seed_is_repeatable_and_preserves_local_records(self):
        runner = app.test_cli_runner()
        for _ in range(2):
            result = runner.invoke(args=["seed"])
            self.assertEqual(result.exit_code, 0, result.output)
        for category in ("people", "planets", "vehicles"):
            status, records = self.call("GET", f"/{category}")
            self.assertEqual(status, 200)
            self.assertEqual(len(records), 10)
            self.assertEqual(len({item["swapi_id"] for item in records}), 10)
            self.assertTrue(all(item["image_url"] for item in records))
        with app.app_context():
            vehicle = db.session.get(Vehicle, 1)
            self.assertEqual(vehicle.swapi_id, "4")
            self.assertTrue(vehicle.serialize()["image_url"].endswith("vehicles/4.jpg"))
        self.assertEqual(self.call("GET", "/people/1")[1]["homeworld"], "Tatooine")

    def test_json_routing_errors(self):
        self.assertEqual(self.call("GET", "/missing")[0], 404)
        status, body = self.call("POST", "/people")
        self.assertEqual(status, 405)
        self.assertIn("error", body)


if __name__ == "__main__":
    unittest.main()
