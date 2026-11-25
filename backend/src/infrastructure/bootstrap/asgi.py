from src.infrastructure.bootstrap.app import create_app
from src.infrastructure.logging.config import configure_logging

configure_logging()

app = create_app()
