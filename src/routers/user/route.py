from .static.route import static_router
from .link_twitter.route import link_twitter_router
from .tweet_task.route import tweet_task_router
from .tg_task.route import tg_task_router
from .wallet.route import wallet_router
from .task_browser.route import browse_tasks_router

user_routers = [
    static_router,
    browse_tasks_router,
    link_twitter_router,
    tweet_task_router,
    tg_task_router,
    wallet_router
]