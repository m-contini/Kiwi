import logging
from .const import (
    LOG_FILE,
    ROOT,
    ESTRAZIONI_DIR,
    HomeKiwiOutput,
    Endpoints,
)
from .kiwi import Auth
from .objects import (
    User,
    Utenze,
    Lavorazioni,
    KiwiTable,
    Riassegnazione,
    Riassegnazioni,
    SearchForm
)
from .types import (
    Agenda,
    Retrocessione,
    Estrazione,
)
from .exceptions import (
    NoSession
)

def setup_logging(level: int = logging.INFO) -> None:
    """Configurazione centralizzata del logging per l'intera suite."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
        ]
    )

__all__ = [
    "LOG_FILE",
    "ROOT",

    "ESTRAZIONI_DIR",
    "HomeKiwiOutput",

    "Endpoints",

    "Auth",

    "User",
    "Utenze",
    "Lavorazioni",
    "KiwiTable",

    "Riassegnazione",
    "Riassegnazioni",
    "Agenda",
    "Retrocessione",
    "Estrazione",
    "SearchForm",

    "NoSession",
    "setup_logging",
]
