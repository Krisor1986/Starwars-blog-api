# Star Wars Data Modeling

[English](README.md) | [Español](README.es.md)

Database modeling exercise for 4Geeks Academy, using Python 3.13, SQLAlchemy and Flask-SQLAlchemy. The deliverables are the models in `src/models.py` and the generated `diagram.png`.

Project repository: [Krisor1986/Starwars-data-modeling](https://github.com/Krisor1986/Starwars-data-modeling).

## Models

| Model | Purpose |
| --- | --- |
| User | Stores email, password and active status. Passwords must be hashed before storage in a future login implementation; serialization excludes the password. |
| Planet | Stores name, climate, terrain and population. |
| Character | Stores name, gender, height, mass, birth year and optional homeworld. |
| FavoritePlanet | Connects a user to a favorite planet. |
| FavoriteCharacter | Connects a user to a favorite character. |

A planet can be the homeworld of many characters. Users and planets have a many-to-many relationship through FavoritePlanet; users and characters have the same relationship through FavoriteCharacter. Composite primary keys prevent duplicate favorites for the same user and resource. Deleting a user or favorite resource through the ORM also removes its associated favorite records.

Some Star Wars properties are stored as strings to support values such as `unknown`. Optional fields may be null.

## Setup and diagram

Install Python 3.13 and Pipenv, then run:

```sh
pipenv --python 3.13
pipenv install
pipenv run diagram
```

Graphviz's native `dot` executable must be available to the virtual environment. The Python `graphviz` package alone does not install it. Check it with:

```sh
pipenv run dot -V
pipenv run python -m pip check
```

On the development Mac, Graphviz 16.1.0 was built from its official source with the native macOS renderer, installed under `~/.local/opt/graphviz-16.1.0`, and linked into this project's virtual environment. That installation is local and is not included in the repository; another computer needs its own Graphviz installation.

The diagram command runs `src/generate_diagram.py`, reads SQLAlchemy metadata and creates `diagram.png` in the project root. It does not require a running database, a .env file, MySQL or PostgreSQL. Regenerate it after changing the models.

![Database diagram](diagram.png)

## Scope

This exercise defines the data structure and relationships. It does not implement login, API endpoints, SWAPI imports or integration with the React blog. Flask API scaffolding and migrations are inherited from the template; the original migration does not represent all five current models.

## GitHub destination and authorship

`origin` points to this project's repository:

```text
https://github.com/Krisor1986/Starwars-data-modeling.git
```

`upstream` points to the school's original template. Use `origin` when uploading your exercise. The local folder name is not a GitHub address and does not determine commit authorship.

This project's local Git identity is `Krisor1986` with the account's noreply address `148481002+Krisor1986@users.noreply.github.com`, avoiding the Mac's automatically generated email. These settings apply to future commits in this repository only.

## Credits

Based on [4GeeksAcademy/flask-rest-hello](https://github.com/4GeeksAcademy/flask-rest-hello). Requirements: [Star Wars Data Modeling](https://github.com/breatheco-de/exercise-starwars-data-modeling/blob/master/README.md). Diagram rendering: [Graphviz](https://graphviz.org/).
