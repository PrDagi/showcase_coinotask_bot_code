from .admin.route import admin_route
from .user.route import user_routers


Routers = [
    *user_routers,
    admin_route
]
