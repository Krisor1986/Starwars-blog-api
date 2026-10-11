# Star Wars Blog API

[English](README.md) | [Español](README.es.md)

Ejercicio de API REST de 4Geeks Academy, desarrollado con Python 3.13, Flask, SQLAlchemy, Flask-Migrate y Flask Admin.

Repositorio: [Krisor1986/Starwars-blog-api](https://github.com/Krisor1986/Starwars-blog-api).

## Ejecutar localmente

```sh
pipenv --python 3.13
pipenv install
cp .env.example .env
pipenv run upgrade
pipenv run seed
pipenv run start
```

Abre http://localhost:3001. La API utiliza el puerto 3001 para que el blog React pueda mantener el 3000. SQLite se guarda en `src/instance/starwars.db` y queda excluido de Git. Mantén `.env` local y establece `FLASK_APP_KEY` como secreto de desarrollo. No se necesita instalar MySQL ni PostgreSQL.

Las migraciones incluidas crean las siete tablas y permiten almacenar hashes de contraseñas. Las actualizaciones conservan los registros locales existentes. Después de futuros cambios de columnas, ejecuta `pipenv run migrate` y luego `pipenv run upgrade`.

## Crear datos en Flask Admin

Abre http://localhost:3001/admin/ y crea:

1. Un planeta, por ejemplo Tatooine.
2. Un personaje, por ejemplo Luke Skywalker, seleccionando Tatooine en Homeworld.
3. Un usuario con email, contraseña y estado activo.

El Admin almacena hashes de las contraseñas creadas o modificadas mediante su formulario. Las respuestas de la API excluyen las contraseñas. Las relaciones muestran nombres de planetas y personajes y emails de usuarios. Los formularios de usuarios, planetas y personajes no incluyen campos de favoritos; utiliza la API para practicar su creación y eliminación.

Este ejercicio no tiene login ni autenticación. El Admin está pensado para el ejercicio local, no para publicarlo en producción.

## Usuario actual

Las rutas de favoritos utilizan `CURRENT_USER_ID` de `.env` (por defecto `1`). Para seleccionar otro usuario existente en Postman, envía el encabezado `X-User-ID`. Es una convención del ejercicio, no autenticación. Si el usuario no existe, la API responde 404; un ID inválido devuelve 400.

## Endpoints

| Método | Ruta | Respuesta correcta |
| --- | --- | --- |
| GET | `/people` | 200: lista de personajes |
| GET | `/people/<people_id>` | 200: detalles del personaje |
| GET | `/planets` | 200: lista de planetas |
| GET | `/planets/<planet_id>` | 200: detalles del planeta |
| GET | `/vehicles` | 200: lista de vehículos |
| GET | `/vehicles/<vehicle_id>` | 200: detalles del vehículo |
| POST | `/favorite/vehicle/<vehicle_id>` | 201: favorito añadido |
| DELETE | `/favorite/vehicle/<vehicle_id>` | 200: favorito eliminado |
| GET | `/users` | 200: usuarios sin contraseñas |
| GET | `/users/favorites` | 200: favoritos del usuario seleccionado |
| POST | `/favorite/planet/<planet_id>` | 201: favorito añadido |
| POST | `/favorite/people/<people_id>` | 201: favorito añadido |
| DELETE | `/favorite/planet/<planet_id>` | 200: favorito eliminado |
| DELETE | `/favorite/people/<people_id>` | 200: favorito eliminado |

Los recursos o favoritos inexistentes devuelven 404; los favoritos duplicados devuelven 409. La eliminación de favoritos se limita al usuario seleccionado. Los errores de la API se devuelven en JSON.

Ejemplo de respuesta de favoritos:

```json
{"user_id": 1, "planets": [], "people": [], "vehicles": []}
```

Los favoritos contienen los recursos serializados, con sus IDs y nombres. Las respuestas proceden del banco local. `pipenv run seed` importa la instantánea incluida con 10 personajes, 10 planetas y 10 vehículos descargados de SWAPI.tech, correspondientes a la primera página del blog React. Los endpoints CRUD de planetas y personajes son opcionales y no se implementan. La integración con React y el login corresponden a ejercicios separados.

## Datos importados y futura integración con React

`data/starwars.json` contiene una instantánea descargada de la API real de SWAPI.tech, con su fuente y fecha de descarga. Incluye los mismos primeros 10 elementos de cada categoría que el blog React. Las naves clasificadas como vehículos por SWAPI permanecen en `/vehicles`; no se incluye un catálogo separado de starships.

`pipenv run seed` puede repetirse sin duplicar registros. Actualiza los campos importados, relaciona registros existentes por ID de SWAPI o nombre y conserva IDs locales, usuarios y favoritos. Reutiliza Luke y Tatooine creados manualmente. Para actualizar la instantánea desde la API real, ejecuta `pipenv run download_data` y después `pipenv run seed`.

Las respuestas incluyen el `id` local, el `swapi_id` separado, la URL de imagen de `breatheco-de/swapi-images` y un objeto `properties` con los detalles importados. Las URL de recursos relacionados se resuelven a nombres durante la descarga. Las imágenes utilizan el ID de SWAPI, nunca el ID local. Las rutas de API y favoritos utilizan IDs locales.

Stewjon, el planeta natal de Obi-Wan, queda fuera de los primeros 10 planetas. Su nombre se conserva en sus propiedades sin añadir otro planeta a la lista. La API queda preparada para la futura integración; no se ha modificado el proyecto React.

## Postman y verificación

Importa `postman/Starwars-blog-api.postman_collection.json`. Ajusta `base_url`, `user_id`, `planet_id` y `people_id` y `vehicle_id` según tus registros locales. Ejecuta las peticiones en orden para consultar datos, añadir favoritos y eliminarlos. Añadir nuevamente un favorito existente devuelve 409 en lugar de 201.

```sh
pipenv run python -m unittest discover -s tests -v
pipenv run flask db check
pipenv run python -m pip check
```

Los tests inician un servidor HTTP real con una base de datos SQLite temporal, aplican las migraciones, crean registros mediante Flask Admin y verifican consultas, hashes de contraseñas, favoritos, duplicados, aislamiento entre usuarios y errores. No simulan respuestas de API ni modifican la base de datos de desarrollo.

## Modelos y diagrama

`User`, `Planet`, `Character`, `Vehicle`, `FavoritePlanet`, `FavoriteCharacter` y `FavoriteVehicle` definen el modelo. Un planeta tiene muchos personajes. Cada tabla de favoritos relaciona usuarios y recursos mediante una clave primaria compuesta que impide duplicados.

```sh
pipenv run diagram
```

La generación del diagrama requiere además el ejecutable nativo `dot` de Graphviz. El Mac de desarrollo tiene Graphviz 16.1.0 instalado localmente y enlazado al entorno virtual; otros ordenadores necesitan su propia instalación.

![Diagrama de la base de datos](diagram.png)

## GitHub

`origin` apunta a `https://github.com/Krisor1986/Starwars-blog-api.git`. Haz commit y push desde la carpeta de este proyecto. El autor Git configurado en el ordenador de desarrollo es `Krisor1986`, con `148481002+Krisor1986@users.noreply.github.com`. Esa configuración global no se guarda en los archivos del repositorio.

## Créditos

Basado en [4GeeksAcademy/flask-rest-hello](https://github.com/4GeeksAcademy/flask-rest-hello) y el ejercicio completado de modelado de Star Wars. Requisitos: [Star Wars Blog API](https://github.com/breatheco-de/exercise-starwars-blog-api).
