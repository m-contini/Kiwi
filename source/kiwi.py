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

from pathlib import Path
from typing import Optional
from requests.exceptions import RequestException
from getpass import getpass
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

    def read_secrets(self, env_name: str = '.env') -> str:

        if self._mock_file is not None:
            env_name += '.example'

        load_dotenv(env_name)
        user = os.getenv('USERNAME', '')
        if not user:
            raise NoCredentials('Impossibile leggere username. Controllare `.env`')

        password = os.getenv('PASSWORD', '')
        if not password:
            raise NoCredentials('Impossibile leggere username. Controllare `.env`')
        print(f"Username: '{user}'")
        print(f"Password: '{'*'*len(password)}'\n")
        return user

    def get_dashboard_snapshot(self) -> Response:

        if self._mock_file is not None:
            resp = Response()
            if not self._mock_file.is_file():
                return resp
            with open(self._mock_file, 'r', encoding='utf-8') as f:
                resp._content = f.read().encode('utf-8')
            return resp

        self.php_session_id: str = self._get_php_session_id()
        if not self.php_session_id:
            raise NoCookies("Impossibile ottenere il PHPSESSID.")

        login_page: Optional[Response] = self._get_auth_page()
        if login_page is None:
            raise NoLoginPage("Impossibile ottenere la pagina di autenticazione.")

        html_content: str = login_page.text
        kc_cookies: dict[str, str] = login_page.cookies.get_dict()

        action_url: Optional[str] = self._extract_form_action(html_content)
        if action_url is None:
            raise NoActionUrl("Impossibile estrarre l'URL di action dal form di login.")

        home_kiwi: Optional[Response] = self._post_login_form(action_url, kc_cookies)
        if home_kiwi is None:
            raise FetchError("Richiesta alla Home Kiwi fallita: credenziali inserite errate.")

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

    def _get_auth_page(self) -> Optional[Response]:
        """ Effettua una richiesta GET alla pagina di autenticazione """
        try:
            headers = {'Cookie': f'PHPSESSID={self.php_session_id}'}
            response = self.session.get(AUTH_URL, headers=headers)
            response.raise_for_status()
            return response
        except RequestException:
            return

    @staticmethod
    def _extract_form_action(html_content: str) -> Optional[str]:
        """ Analizza l'HTML e estrai l'attributo action dal form di login """

        soup = BeautifulSoup(html_content, 'html.parser')
        form = soup.find('form', {'id': 'kc-form-login'})

        if not form:
            return

        action = form.get('action')
        if isinstance(action, str):
            return action

    def _post_login_form(self, action_url: str, cookies: dict[str, str]) -> Optional[Response]:
        """ Invia una richiesta POST al form di login """

        password = getpass('Inserisci la tua password: ')

        data = {
            'username': self.username,
            'password': password,
            'credentialId': ''
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': '; '.join([f"{name}={value}" for name, value in cookies.items()])
        }

        try:
            response = self.session.post(action_url, data=data, headers=headers, allow_redirects=False)
            response.raise_for_status()
            return response
        except RequestException:
            return

class Auth(Scraper):
    """Oggetto che trasporta sessione autenticata. Fondamentale utilizzo in ogni script che si connette ad un endpoint di Kiwi."""
    def __init__(self, _mock_file: Optional[Path]) -> None:
        super().__init__(_mock_file)

    def login(self) -> Optional[Session]:
        """Restituisce sessione autenticata a Kiwi, oltre che settarla nell'attributo di classe"""

        try:
            home_kiwi: Response = self.get_dashboard_snapshot()
        except Exception as e:
            raise NoSession((f'Autenticazione fallita | [{e.__class__.__name__}] | {str(e)}'))

        url = Endpoints.ADMIN.value
        if home_kiwi.url == KIWI:
            print("Login riuscito, reindirizzato alla homepage.")

            try:
                response: Response = self.session.get(url)
                response.raise_for_status()
            except RequestException as e:
                print(f"Errore nel raggiungere la pagina finale: {e}")
                return

        print(f"Pagina finale raggiunta: {url}")
        print("Login riuscito senza reindirizzamenti.")
        return self.session

    def get_request(self, url: str) -> Response:
        """Esegue richiesta HTTP GET ad un endpoint di Kiwi e restituisce la risposta"""

        if self._mock_file is not None:
            resp = Response()
            if not self._mock_file.is_file():
                return resp
            with open(self._mock_file, 'r', encoding='utf-8') as f:
                resp._content = f.read().encode('utf-8')
            return resp

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'cookie': f'PHPSESSID={self.php_session_id}',
        }
        try:
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            print(f"\n Richiesta GET a {url} eseguita con successo.")
            return response
        except RequestException:
            raise

    def post_request(self, url: str, data: dict[str, str]) -> Response:
        """Esegue richiesta HTTP POST ad un endpoint di Kiwi e restituisce la risposta"""

        if self._mock_file is not None:
            resp = Response()
            if not self._mock_file.is_file():
                return resp
            with open(self._mock_file, 'r', encoding='utf-8') as f:
                resp._content = f.read().encode('utf-8')
            return resp

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': f'PHPSESSID={self.php_session_id}'
        }
        try:
            response = self.session.post(url, data=data, headers=headers)
            response.raise_for_status()
            print(f"\n Richiesta POST a {url} eseguita con successo.")
            return response
        except RequestException:
            raise
