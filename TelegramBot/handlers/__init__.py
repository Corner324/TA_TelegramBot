from . import start
from . import catalog
from . import faq
from . import cart

def setup_handlers(dp):
    start.register_handlers(dp)
    catalog.register_handlers(dp)
    faq.register_handlers(dp)
    cart.register_handlers(dp)