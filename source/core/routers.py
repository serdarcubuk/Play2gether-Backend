from source.app.auth.views import auth_router
from source.app.chat.views import chat_router
from source.app.games.views import games_router
from source.app.profiles.views import profiles_router
from source.app.rooms.views import rooms_router
from source.app.users.views import users_router
from source.core.middlewares import CustomAPIRouter

api_router = CustomAPIRouter()

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(games_router)
api_router.include_router(profiles_router)
api_router.include_router(rooms_router)
api_router.include_router(chat_router)
