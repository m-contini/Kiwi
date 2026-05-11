"""
Questo file contiene le classi di eccezioni personalizzate
utilizzate all'interno dei moduli in `source`.
"""

class KiwiError(Exception):
    """Classe base per tutte le eccezioni del progetto Kiwi."""
    pass

class NoCredentials(KiwiError):
    """Eccezione sollevata se la lettura credenziali da `.env` fallisce."""
    pass

class NoCookies(KiwiError):
    """Eccezione sollevata se non esiste cookie di sessione `PHPSESSID`."""
    pass

class NoLoginPage(KiwiError):
    """Eccezione sollevata quando è impossibile connettersi all'endpoint di autenticazione."""
    pass

class NoActionUrl(KiwiError):
    """Eccezione sollevata quando è impossibile recuperare l'URL di `action` dal form di login."""
    pass

class FetchError(KiwiError):
    """Eccezione sollevata quando si verifica un errore nel recupero della Home di Kiwi."""
    pass

class NoSession(KiwiError):
    """Eccezione sollevata quando una routine non riesce a stabilire una connessione autenticata."""
    pass
