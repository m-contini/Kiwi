import logging
import os
from pathlib import Path
from typing import Optional, Any, Mapping

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from requests import RequestException, Response, Session

from .exceptions import NoActionUrl, NoCookies, NoCredentials, NoSession

from .const import AUTH_URL, KIWI, MOCK_DIR, Endpoints

class Scraper:
    def __init__(self, _mock_file: Optional[Path]) -> None:
        self._mock_file = MOCK_DIR / (_mock_file.stem + '.html') if _mock_file is not None else None
        self.session: Session = Session()
        self.mocked_response = self._handle_mock()

    def _handle_mock(self) -> Optional[Response]:
        """Helper per restituire una risposta fittizia se in modalità test."""
        if self._mock_file and self._mock_file.is_file():
            resp = Response()
            resp.status_code = 200
            resp._content = self._mock_file.read_bytes()
            logging.info(f"Mocking attivo: restituita risposta fittizia da '{self._mock_file.relative_to(Path.cwd())}'")
            return resp
        return None

    def request(
        self,
        method: str,
        url: str,
        data: Mapping[str, Any] = {}
    ) -> Response:
        """Esegue richiesta HTTP ad un endpoint di Kiwi e restituisce la risposta"""

        if method not in ('GET', 'POST', 'HEAD'):
            raise ValueError(f"Metodo non supportato: {method}")

        if self.mocked_response is not None:
            return self.mocked_response

        if method == 'GET':
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            }
            data = {}
            allow_redirects = True
        elif method == 'HEAD':
            headers = {k: str(v) for k, v in self.session.headers.items()}
            data = {}
            allow_redirects = True
        elif method == 'POST':
            headers = {k: str(v) for k, v in self.session.headers.items()}
            data = {k: str(v) for k, v in data.items()}
            allow_redirects = False

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                allow_redirects=allow_redirects
            )
            response.raise_for_status()
            logging.info(f"{method} {url} - OK")
            return response
        except (RequestException, ConnectionError) as e:
            logging.error(f"Errore durante la richiesta {method} a {url}: {e}")
            raise

class Auth(Scraper):

    def __init__(self, _mock_file: Optional[Path]) -> None:
        super().__init__(_mock_file)
        self.user, self.password = self._read_secrets(Path(__file__).parent.parent / '.env')

    def login(self) -> None:
        """Restituisce sessione autenticata a Kiwi, oltre che settarla nell'attributo di classe"""

        try:
            home_kiwi: Response = self.fetch_kiwi_home(self.user, self.password)
        except Exception as e:
            raise NoSession((f'Autenticazione fallita | [{e.__class__.__name__}] | {str(e)}'))

        if home_kiwi.url == KIWI:
            _ = self.request('GET', Endpoints.ADMIN.value)

        logging.info("Autenticazione avvenuta con successo.")

    def fetch_kiwi_home(self, user: str, password: str) -> Response:

        logging.info("Recupero della Home di Kiwi...")

        response = self.request('HEAD', Endpoints.LOGIN.value)
        if response is self.mocked_response:
            return response

        cookies: dict[str, str]= self.session.cookies.get_dict()
        if not cookies.get('PHPSESSID', ''):
            raise NoCookies("Impossibile ottenere il PHPSESSID.")

        login_page: Response = self.request('GET', AUTH_URL)

        soup = BeautifulSoup(login_page.text, 'html.parser')
        form = soup.find('form', {'id': 'kc-form-login'})
        if not form:
            raise NoActionUrl("Form di login non trovato nell'HTML.")

        action_url = form.get('action')
        if not isinstance(action_url, str):
            raise NoActionUrl("Impossibile estrarre l'URL di action dal form di login.")

        data: dict[str, str] = {
            'username': user,
            'password': password,
            'credentialId': ''
        }
        home_kiwi = self.request('POST', action_url, data=data)

        return home_kiwi

    def _read_secrets(self, env_path: Path) -> tuple[str, str]:
        """Legge le credenziali (username e password) dal file .env.
        Se in modalità test, cerca il file `.env.example`.
        """
        if self._mock_file is not None:
            env_path = env_path.with_name(env_path.name + '.example')

        load_dotenv(env_path)
        user = os.getenv('USERNAME', '')
        password = os.getenv('PASSWORD', '')

        logging.debug(f"Username: '{user}'")
        logging.debug(f"Password: '{'*'*len(password)}'\n")

        if not (user and password):
            raise NoCredentials('Impossibile leggere credenziali. Controllare `.env`')

        return user, password
