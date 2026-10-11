# Star Wars Data Modeling

[English](README.md) | [Español](README.es.md)

Ejercicio de modelado de bases de datos de 4Geeks Academy, con Python 3.13, SQLAlchemy y Flask-SQLAlchemy. Los entregables son los modelos de `src/models.py` y el archivo generado `diagram.png`.

Repositorio del proyecto: [Krisor1986/Starwars-data-modeling](https://github.com/Krisor1986/Starwars-data-modeling).

## Modelos

| Modelo | Propósito |
| --- | --- |
| User | Guarda email, contraseña y estado activo. Las contraseñas deben almacenarse como hashes en una futura implementación de login; la serialización excluye la contraseña. |
| Planet | Guarda nombre, clima, terreno y población. |
| Character | Guarda nombre, género, altura, masa, año de nacimiento y planeta natal opcional. |
| FavoritePlanet | Relaciona un usuario con un planeta favorito. |
| FavoriteCharacter | Relaciona un usuario con un personaje favorito. |

Un planeta puede ser el planeta natal de muchos personajes. Usuarios y planetas tienen una relación muchos-a-muchos mediante FavoritePlanet; usuarios y personajes tienen la misma relación mediante FavoriteCharacter. Las claves primarias compuestas impiden favoritos duplicados para un mismo usuario y recurso. Al eliminar un usuario o recurso favorito mediante el ORM, también se eliminan sus registros de favoritos asociados.

Algunas propiedades de Star Wars se guardan como texto para admitir valores como `unknown`. Los campos opcionales pueden ser nulos.

## Instalación y diagrama

Instala Python 3.13 y Pipenv y ejecuta:

```sh
pipenv --python 3.13
pipenv install
pipenv run diagram
```

El ejecutable nativo `dot` de Graphviz debe estar disponible en el entorno virtual. El paquete Python `graphviz` no lo instala por sí solo. Compruébalo con:

```sh
pipenv run dot -V
pipenv run python -m pip check
```

En el Mac de desarrollo, Graphviz 16.1.0 se compiló desde su código oficial con el renderizador nativo de macOS, se instaló en `~/.local/opt/graphviz-16.1.0` y se enlazó al entorno virtual de este proyecto. Esa instalación es local y no se incluye en el repositorio; otro ordenador necesita su propia instalación de Graphviz.

El comando ejecuta `src/generate_diagram.py`, lee los metadatos de SQLAlchemy y crea `diagram.png` en la raíz del proyecto. No requiere una base de datos en ejecución, un archivo .env, MySQL ni PostgreSQL. Regenera el diagrama después de modificar los modelos.

![Diagrama de la base de datos](diagram.png)

## Alcance

Este ejercicio define la estructura de datos y sus relaciones. No implementa login, endpoints de API, importación de SWAPI ni integración con el blog React. La estructura de la API Flask y las migraciones proceden de la plantilla; la migración original no representa los cinco modelos actuales.

## Destino en GitHub y autoría

`origin` apunta al repositorio de este proyecto:

```text
https://github.com/Krisor1986/Starwars-data-modeling.git
```

`upstream` apunta a la plantilla original de la escuela. Utiliza `origin` al subir el ejercicio. El nombre de la carpeta local no es una dirección de GitHub ni determina la autoría de los commits.

La identidad Git local de este proyecto es `Krisor1986`, con la dirección noreply de la cuenta `148481002+Krisor1986@users.noreply.github.com`, evitando el email generado automáticamente por el Mac. Estos ajustes se aplican únicamente a futuros commits de este repositorio.

## Créditos

Basado en [4GeeksAcademy/flask-rest-hello](https://github.com/4GeeksAcademy/flask-rest-hello). Requisitos: [Star Wars Data Modeling](https://github.com/breatheco-de/exercise-starwars-data-modeling/blob/master/README.es.md). Renderizado del diagrama: [Graphviz](https://graphviz.org/).
