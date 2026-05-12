import logging
from pathlib import Path
from typing import Any

from source import (
    Endpoints,
    Auth,
    Lavorazioni
)

LOGIN_ID_TEST: str = '14091'
DATA_FROM_TEST: str = '2024-06-28'
DATA_TO_TEST: str = ''

class RequestTest:
    def __init__(self, url: str, data: dict[str, Any], method: str, headers: dict[str, str]) -> None:
        self.url: str = url
        self.data: dict[str, Any] = data
        self.method: str = method
        self.headers: dict[str, str] = headers

class ResponseTest:
    def __init__(self, status_code: int, headers: dict[str, str], text: str) -> None:
        self.status_code: int = status_code
        self.headers: dict[str, str] = headers
        self.text: str = text

def run(__TEST__: bool = False) -> None:
    """
    Questo script si autentica a **Kiwi** per scaricare la tabella `tabella_lavorazione_consulenti`,
    contenente le lavorazioni di un dato consulente nell'intervallo date specificato, prendendo come parametri:
    - `login_operatore`
    - `data_from`
    - `data_to`

    La tabella recuperata dall'HTML contiene le seguenti colonne:
    - `Id consulente`
    - `Nome consulente`
    - `Id agenda`
    - `Orario lavorazione`

    Questo script è pensato per essere eseguito tramite uno scheduler (es. crontab).

    NOTA:  
    Essendo rimasto in fase di test, lo script si limita a
    stampare a schermo il contenuto della risposta,
    senza salvataggio né analisi.
    """

    try:
        # Imposta la sessione HTTP
        kiwi = Auth(Path(__file__) if __TEST__ else None)
        kiwi.login()

        # Dati TEST da usare come payload
        data: dict[str, str] = {
            'login_operatore': LOGIN_ID_TEST,
            'data_from': DATA_FROM_TEST,
            'data_to': DATA_TO_TEST,
            'esporta': 'Esporta in Excel'
        }

        url = Endpoints.LAVORAZ_CONS.value

        # Richiesta POST per ottenere le lavorazioni di un dato consulente
        response = kiwi.post_request(url, data)

        # RICHIESTA FITTIZIA DI TEST
        request_test = RequestTest(
            url=url,
            data=data,
            method='POST',
            headers={
                'content-type': 'application/x-www-form-urlencoded',
            }
        )
        # Logging dettagliato per debug
        logging.debug(f"Richiesta POST a {url} con dati: {data}")

        # RISPOSTA DI TES
        response_test = ResponseTest(
            status_code=200,
            headers={
                'content-type': 'application/vnd.ms-excel',
            },
            text=response.text,
        )
        if response_test.status_code != 200:
            logging.error(f"Errore server: {response_test.status_code}")
            return

        # Mostra i dettagli della richiesta
        logging.debug("=" * 50)
        logging.debug(f"""Dettagli della richiesta:
            URL: {request_test.url}
            Metodo: {request_test.method}
            Headers: {request_test.headers}
            Dati inviati: {request_test.data}
        """)

        # Mostra i dettagli della risposta
        logging.debug("=" * 50)
        logging.debug(f"""Dettagli della risposta:
            Status code: {response_test.status_code}
            Headers: {response_test.headers}
            Lunghezza del contenuto: {len(response_test.text)}
        """)

        # Recupero e parsing delle lavorazioni
        lavorazioni = Lavorazioni(LOGIN_ID_TEST)
        lavorazioni.data = lavorazioni.parse_lavorazioni_html(response.text)

        logging.info(f"Estratte {len(lavorazioni.data)} lavorazioni per il conslente {LOGIN_ID_TEST}.")
        for row in lavorazioni.data:
            logging.debug(row)

        # Salvataggio
        lavorazioni.to_csv()
        logging.info(f"Lavorazioni salvate in: {lavorazioni.output_file}")

    except Exception as e:
        logging.error(f"Errore durante l'estrazione lavorazioni consulenti: {e}", exc_info=True)
        raise
