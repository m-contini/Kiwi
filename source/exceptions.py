"""
Questo file contiene le classi di eccezioni personalizzate
utilizzate all'interno del modulo `core`.
"""

class BaseException(Exception):
    def __init__(self, msg: str) -> None:
        super().__init__()
        self.msg: str = msg

    def __str__(self) -> str:
        return self.msg

class NoCredentials(BaseException):
    """Eccezione sollevata se la lettura credenziali da `.env` fallisce."""
    def __init__(self, msg: str) -> None:
        super().__init__(msg)

class NoCookies(BaseException):
    """Eccezione sollevata se non esiste cookie di sessione `PHPSESSID`."""
    def __init__(self, msg: str) -> None:
        super().__init__(msg)

class NoLoginPage(BaseException):
    """Eccezione sollevata quando è impossibile connettersi all'endpoint di autenticazione."""
    def __init__(self, msg: str) -> None:
        super().__init__(msg)

class NoActionUrl(BaseException):
    """Eccezione sollevata quando è impossibile recuperare l'URL di `action` dal form di login."""
    def __init__(self, msg: str) -> None:
        super().__init__(msg)

class FetchError(BaseException):
    """Eccezione sollevata quando si verifica un errore nel recupero della Home di Kiwi."""
    def __init__(self, msg: str) -> None:
        super().__init__(msg)

class NoSession(BaseException):
    """Eccezione sollevata quando una routine non riesce a stabilire una connessione autenticata."""
    def __init__(self, msg: str) -> None:
        super().__init__(msg)
