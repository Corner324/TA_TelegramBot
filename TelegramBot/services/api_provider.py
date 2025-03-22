from infrastructure.http_client import HttpClient
from repositories.catalog_repository import CatalogRepository
from repositories.faq_repository import FAQRepository

http_client = HttpClient()
catalog_repo = CatalogRepository(http_client)
faq_repo = FAQRepository(http_client)


class ApiProvider:
    def __init__(self):
        self.catalog = catalog_repo
        self.faq = faq_repo


api_provider = ApiProvider()
