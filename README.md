# Play2Gether Backend API

### Requirements:

```
docker
```

### Run:

```
cp config/.env.example config/.env
docker compose up --build -d
```

### Migration:

```
docker exec api alembic revision --autogenerate -m "description"
docker exec api alembic upgrade head
```

### Docs:

```
OpenAPI: http://localhost:8000/docs
```

### Endpoints:

```http request
POST   /auth/token                 # token get
POST   /auth/refresh               # token refresh

POST   /users                      # user create
GET    /users                      # user get
PATCH  /users                      # user update
DELETE /users                      # user delete
GET    /users/admin                # user list (admin)

POST   /games                      # game add (admin)
GET    /games                      # game list
GET    /games/{game_id}            # game get
PATCH  /games/{game_id}            # game update (admin)
DELETE /games/{game_id}            # game delete (admin)

POST   /profiles                   # profile create
GET    /profiles                   # profile list
GET    /profiles/{profile_id}      # profile get
PATCH  /profiles/{profile_id}      # profile update
DELETE /profiles/{profile_id}      # profile delete

POST   /rooms                      # room create
GET    /rooms                      # room get
PATCH  /rooms                      # room update (owner)
DELETE /rooms                      # room left (owner delete)
GET    /rooms/list                 # room list
GET    /rooms/look/{room_id}       # room look
POST   /rooms/join/{room_id}       # room join
DELETE /rooms/kick/{room_id}       # room kick (owner)

GET    /                           # health check

WS     /chat                       # chat web socket
```

### Database Tables:

```json
{
  "Base (Abstract)": {
    "id": "int",
    "create_date": "datetime",
    "update_date": "datetime"
  },
  "User": {
    "username": "str",
    "password": "str",
    "email": "str",
    "first_name": "str",
    "last_name": "str",
    "active": "bool",
    "role": "enum(str)",
    "password_timestamp": "float"
  },
  "Game": {
    "game_name": "str",
    "game_description": "str",
    "game_ranks": "list(str)",
    "game_logo": "str"
  },
  "Profile": {
    "user_id": "fk(User)",
    "game_id": "fk(Game)",
    "user_nickname": "str",
    "user_rank": "str"
  },
  "Room": {
    "game_id": "fk(Game)",
    "owner_id": "fk(User)",
    "room_name": "str",
    "room_description": "str",
    "room_ranks": "list(str)",
    "room_size": "int"
  }
}
```
