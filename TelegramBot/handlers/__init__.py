from . import start
from . import catalog

# Импорты других обработчиков, когда они будут созданы
# from . import cart
# from . import faq


def setup_handlers(dp):
    start.register_handlers(dp)
    catalog.register_handlers(dp)
    # cart.register_handlers(dp)
    # faq.register_handlers(dp)
