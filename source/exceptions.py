"""
Questo file contiene le classi di eccezioni personalizzate
utilizzate all'interno dei moduli in `source`.
"""

from typing import final

class KiwiException(Exception):
    """Classe base per tutte le eccezioni del progetto Kiwi."""
    pass

@final
class NoCredentials(KiwiException):
    """Eccezione sollevata se la lettura credenziali da `.env` fallisce."""
    pass

@final
class NoCookies(KiwiException):
    """Eccezione sollevata se non esiste cookie di sessione `PHPSESSID`."""
    pass

@final
class NoLoginPage(KiwiException):
    """Eccezione sollevata quando è impossibile connettersi all'endpoint di autenticazione."""
    pass

@final
class NoActionUrl(KiwiException):
    """Eccezione sollevata quando è impossibile recuperare l'URL di `action` dal form di login."""
    pass

@final
class FetchError(KiwiException):
    """Eccezione sollevata quando si verifica un errore nel recupero della Home di Kiwi."""
    pass

@final
class NoSession(KiwiException):
    """Eccezione sollevata quando una routine non riesce a stabilire una connessione autenticata."""
    pass
