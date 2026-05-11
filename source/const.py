"""
Questo file contiene solo costanti da esportare
per il funzionamento di altri script/moduli.
"""

from enum import Enum
from pathlib import Path

# Flag globale
# Se True: esegue gli script offline
# facendo scraping da file HTML che simulano Kiwi
# anziché da web
__TEST__ = True

# USERNAME verrà letto da file .env
# USERNAME: str = 'mcontini'

# Per gli script nella root
# const.py --parent--> source --parent--> root 
ROOT = Path(__file__).parent.parent.resolve()

# File di log
LOG_FILE = ROOT / "app.log"

RIASSEGNAZIONI_DIR: Path = ROOT / "Riassegnazioni"
UTENZE_DIR: Path = ROOT / "Utenze"
LAVORAZIONI_DIR: Path = ROOT / "Lavorazioni"

"""Cartella in cui vengono salvate le estrazioni CSV"""
ESTRAZIONI_DIR: Path = ROOT / "Estrazioni"

HOME_KIWI_DIR: Path = ROOT / "HomeKiwi"
class HomeKiwiOutput(Enum):
    """Collezione di percorsi in cui salvare snapshot della dashboard in vari formati"""
    HTML_DIR = HOME_KIWI_DIR / "htmlTbls"
    CSV_DIR  = HOME_KIWI_DIR / "csvTbls"
    JSON_DIR = HOME_KIWI_DIR / "jsonTbls"

MOCK_DIR: Path = ROOT / "html"

LOGIN: str = 'https://login.facile.it/'

REALM: str     = 'ad-domain'
CLIENT_ID: str = 'kiwi-prod'
SCOPE: str     = 'email+profile+groups'
STATE: str     = '1719005146'

AUTH_URL: str   = LOGIN + f"realms/{REALM}/protocol/openid-connect/auth?response_type=code&client_id={CLIENT_ID}&scope={SCOPE}&state={STATE}"

KIWI: str  = 'https://kiwi.facile.it/'
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
