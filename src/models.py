from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)

    favorite_planets: Mapped[list["FavoritePlanet"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    favorite_characters: Mapped[list["FavoriteCharacter"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }


class Planet(db.Model):
    __tablename__ = "planet"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    climate: Mapped[str | None] = mapped_column(String(100))
    terrain: Mapped[str | None] = mapped_column(String(100))
    population: Mapped[str | None] = mapped_column(String(30))

    characters: Mapped[list["Character"]] = relationship(back_populates="homeworld")
    favorites: Mapped[list["FavoritePlanet"]] = relationship(
        back_populates="planet",
        cascade="all, delete-orphan",
    )


class Character(db.Model):
    __tablename__ = "character"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    gender: Mapped[str | None] = mapped_column(String(30))
    height: Mapped[str | None] = mapped_column(String(30))
    mass: Mapped[str | None] = mapped_column(String(30))
    birth_year: Mapped[str | None] = mapped_column(String(30))

    planet_id: Mapped[int | None] = mapped_column(ForeignKey("planet.id"))

    homeworld: Mapped["Planet | None"] = relationship(back_populates="characters")
    favorites: Mapped[list["FavoriteCharacter"]] = relationship(
        back_populates="character",
        cascade="all, delete-orphan",
    )


class FavoritePlanet(db.Model):
    __tablename__ = "favorite_planet"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    planet_id: Mapped[int] = mapped_column(ForeignKey("planet.id"), primary_key=True)

    user: Mapped["User"] = relationship(back_populates="favorite_planets")
    planet: Mapped["Planet"] = relationship(back_populates="favorites")


class FavoriteCharacter(db.Model):
    __tablename__ = "favorite_character"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    character_id: Mapped[int] = mapped_column(
        ForeignKey("character.id"), primary_key=True
    )

    user: Mapped["User"] = relationship(back_populates="favorite_characters")
    character: Mapped["Character"] = relationship(back_populates="favorites")
