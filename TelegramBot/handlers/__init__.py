from . import start
from . import catalog
from . import faq

def setup_handlers(dp):
    start.register_handlers(dp)
    catalog.register_handlers(dp)
    faq.register_handlers(dp)