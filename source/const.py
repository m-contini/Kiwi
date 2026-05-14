"""
Costanti di configurazione globale.

Definisce i percorsi del filesystem, gli endpoint URL del gestionale Kiwi e i parametri
per l'autenticazione, necessari per il funzionamento dell'intera suite.
"""

from enum import Enum
from pathlib import Path
from typing import Final

# Per gli script nella root
# const.py --parent--> source --parent--> root 
ROOT: Final[Path] = Path(__file__).parent.parent.resolve()

# File di log
LOG_FILE: Final[Path] = ROOT / "app.log"

RIASSEGNAZIONI_DIR: Final[Path] = ROOT / "Riassegnazioni"
UTENZE_DIR: Final[Path] = ROOT / "Utenze"
LAVORAZIONI_DIR: Final[Path] = ROOT / "Lavorazioni"

"""Cartella in cui vengono salvate le estrazioni CSV"""
ESTRAZIONI_DIR: Final[Path] = ROOT / "Estrazioni"

HOME_KIWI_DIR: Final[Path] = ROOT / "HomeKiwi"
class HomeKiwiOutput(Enum):
    """Collezione di percorsi in cui salvare snapshot della dashboard in vari formati"""
    HTML_DIR = HOME_KIWI_DIR / "htmlTbls"
    CSV_DIR  = HOME_KIWI_DIR / "csvTbls"
    JSON_DIR = HOME_KIWI_DIR / "jsonTbls"

MOCK_DIR: Final[Path] = ROOT / "html"

LOGIN: Final[str] = 'https://login.facile.it/'

REALM: Final[str]     = 'ad-domain'
CLIENT_ID: Final[str] = 'kiwi-prod'
SCOPE: Final[str]     = 'email+profile+groups'
STATE: Final[str]     = '1719005146'

AUTH_URL: Final[str]   = LOGIN + f"realms/{REALM}/protocol/openid-connect/auth?response_type=code&client_id={CLIENT_ID}&scope={SCOPE}&state={STATE}"

KIWI: Final[str]  = 'https://kiwi.facile.it/'
class Endpoints(Enum):
    """Collezione di endpoint disponibili per recupero automatico dati e informazioni"""
    LOGIN        = KIWI + "login"
    ADMIN        = KIWI + "mutui/admin"
    RICERCA      = KIWI + "ricerca"
    RIASSEGNAZ   = KIWI + "mutui/admin/pratiche/riassegna"
    USERLIST     = KIWI + "user/list"
    UPDATE       = KIWI + "mutui/admin" + "/pratica/gestione"
    LAVORAZ_CONS = KIWI + "mutui/admin" + "/visualizza/lavorazioneConsulenti"
    ESTRAZIONI   = KIWI + "mutui/esporta/estrazioni"
    DOWNLOAD     = KIWI + "mutui/esporta/estrazioni" + "/download"
