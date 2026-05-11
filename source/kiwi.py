"""
Questo script contiene metodi di `login`, che prendono in input
`username` dal file `.env` e `password` tramite prompt all'utente,
e restituiscono:

- Una classe `Auth` con metodo `login`, sessione HTTP (requests) autenticata a Kiwi.
- Una classe `Scraper`, ereditata dalla precedente, per lo scraping della pagina home di Kiwi.

La procedura di login avviene interamente tramite scraping.

Questa sessione è obbligatoria per eseguire gli altri script che interrogano Kiwi
(es. riassegnazioni, estrazioni, utenze, ecc...)
"""

import logging
from pathlib import Path
from typing import Optional
from requests.exceptions import RequestException
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
from requests import Session, Response

# Eccezioni generiche
from .exceptions import (
    NoCookies, NoCredentials, NoLoginPage, NoActionUrl,
    FetchError, NoSession
)

# Costanti
from .const import (
    KIWI,
    Endpoints,
    AUTH_URL,
    MOCK_DIR,
)

class Scraper:

    def __init__(self, _mock_file: Optional[Path]) -> None:

        self._mock_file = MOCK_DIR / (_mock_file.stem + '.html') if _mock_file is not None else None

        self.username: str = self.read_secrets('.env')
        self.session: Session = Session()
        self.php_session_id = None
        
    def _handle_mock(self) -> Optional[Response]:
        """Helper per restituire una risposta fittizia se in modalità test."""
        if self._mock_file and self._mock_file.is_file():
            resp = Response()
            resp.status_code = 200
            resp._content = self._mock_file.read_bytes()
            return resp
        return None

    def read_secrets(self, env_name: str = '.env') -> str:
        """Legge le credenziali (username e password) dal file .env.
        Se in modalità test, cerca il file `.env.example`.
        """
        if self._mock_file is not None:
            env_name += '.example'

        load_dotenv(env_name)
        user = os.getenv('USERNAME', '')
        password = os.getenv('PASSWORD', '')

        logging.info(f"Username: '{user}'")
        logging.debug(f"Password: '{'*'*len(password)}'\n")

        if not user or not password:
            raise NoCredentials('Impossibile leggere credenziali. Controllare `.env`')

        return user

    def get_dashboard_snapshot(self) -> Response:
        """Esegue l'intera procedura di login tramite scraping per ottenere l'HTML della Home."""

        if resp := self._handle_mock():
            return resp

        self.php_session_id: str = self._get_php_session_id()
        if not self.php_session_id:
            raise NoCookies("Impossibile ottenere il PHPSESSID.")

        login_page: Response = self._get_auth_page()

        html_content: str = login_page.text

        action_url: Optional[str] = self._extract_form_action(html_content)
        if action_url is None:
            raise NoActionUrl("Impossibile estrarre l'URL di action dal form di login.")

        home_kiwi: Response = self._post_login_form(action_url)

        return home_kiwi

    def _get_php_session_id(self) -> str:
        """Richiesta HEAD al solo scopo di ottenere cookies"""

        url = Endpoints.LOGIN.value
        try:
            response = self.session.head(url, allow_redirects=True)
            response.raise_for_status()
            cookies = self.session.cookies.get_dict()
            return cookies.get('PHPSESSID', '')
        except RequestException:
            raise

    def _get_auth_page(self) -> Response:
        """ Effettua una richiesta GET alla pagina di autenticazione """
        try:
            # Non serve passare il cookie manualmente se è già nella sessione
            response = self.session.get(AUTH_URL)
            response.raise_for_status()
            return response
        except RequestException as e:
            raise NoLoginPage(f"Errore durante il recupero della pagina di auth: {e}")

    @staticmethod
    def _extract_form_action(html_content: str) -> Optional[str]:
        """ Analizza l'HTML e estrai l'attributo action dal form di login """

        soup = BeautifulSoup(html_content, 'html.parser')
        form = soup.find('form', {'id': 'kc-form-login'})

        if not form:
            raise NoActionUrl("Form di login non trovato nell'HTML.")

        action = form.get('action')
        if isinstance(action, str):
            return action
        return

    def _post_login_form(self, action_url: str) -> Response:
        """ Invia una richiesta POST al form di login """

        # Prendi la password dall'ambiente invece che da input() per permettere automazione
        data = {
            'username': self.username,
            'password': os.getenv('PASSWORD'),
            'credentialId': ''
        }
        # Il Content-Type viene gestito automaticamente da requests se passi un dict a data
        # I cookie Keycloak vengono gestiti automaticamente dalla sessione

        try:
            response = self.session.post(action_url, data=data, allow_redirects=False)
            response.raise_for_status()
            return response
        except RequestException as e:
            raise FetchError(f"Errore durante l'invio del form di login: {e}")

class Auth(Scraper):
    """Oggetto che trasporta sessione autenticata. Fondamentale utilizzo in ogni script che si connette ad un endpoint di Kiwi."""
    def __init__(self, _mock_file: Optional[Path]) -> None:
        super().__init__(_mock_file)

    def login(self) -> Optional[Session]:
        """Restituisce sessione autenticata a Kiwi, oltre che settarla nell'attributo di classe"""

        try:
            home_kiwi: Response = self.get_dashboard_snapshot()
            if self._mock_file:
                return self.session
        except Exception as e:
            raise NoSession((f'Autenticazione fallita | [{e.__class__.__name__}] | {str(e)}'))

        url = Endpoints.ADMIN.value
        if home_kiwi.url == KIWI:
            try:
                response: Response = self.session.get(url)
                response.raise_for_status()
            except RequestException as e:
                logging.error(f"Errore nel raggiungere la pagina finale: {e}")
                raise

        logging.info("Autenticazione avvenuta con successo.")

        return self.session

    def get_request(self, url: str) -> Response:
        """Esegue richiesta HTTP GET ad un endpoint di Kiwi e restituisce la risposta"""

        if resp := self._handle_mock():
            return resp

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        }
        try:
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            logging.info(f"GET {url} - OK")
            return response
        except RequestException:
            raise

    def post_request(self, url: str, data: dict[str, str]) -> Response:
        """Esegue richiesta HTTP POST ad un endpoint di Kiwi e restituisce la risposta"""

        if resp := self._handle_mock():
            return resp

        try:
            response = self.session.post(url, data=data)
            response.raise_for_status()
            logging.info(f"POST {url} - OK")
            return response
        except RequestException:
            raise
