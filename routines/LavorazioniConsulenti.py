import logging
from pathlib import Path
from typing import Final
from requests import Response

from source import (
    Endpoints,
    Auth,
    Lavorazioni
)

LOGIN_ID_TEST: Final[str] = '14091'
DATA_FROM_TEST: Final[str] = '2024-06-28'
DATA_TO_TEST: Final[str] = ''

def run(__TEST__: bool = False) -> None:
    """
    Questo script si autentica a **Kiwi** per scaricare la tabella `tabella_lavorazione_consulenti`,
    contenente le lavorazioni di un dato consulente nell'intervallo date specificato, prendendo come parametri:
    - `login_operatore`
    - `data_from`
    - `data_to`

    NOTA: Attualmente la routine utilizza parametri di test hardcodati. 
    In produzione, questi dovrebbero essere passati dinamicamente o letti da config.
    
    Questo script è pensato per essere eseguito tramite uno scheduler (es. crontab).

    I dati vengono salvati in CSV al percorso:
    `./Lavorazioni/YYYY_MM_DD_HH_MM_SS_{login_operatore}.csv`
    """

    # Inizializzazione client e login
    client = Auth(Path(__file__) if __TEST__ else None).login()

    # Dati TEST da usare come payload
    data: Final[dict[str, str]] = {
        'login_operatore': LOGIN_ID_TEST,
        'data_from': DATA_FROM_TEST,
        'data_to': DATA_TO_TEST,
        'esporta': 'Esporta in Excel'
    }

    # Richiesta POST per ottenere le lavorazioni di un dato consulente
    response: Response = client.request('POST', Endpoints.LAVORAZ_CONS.value, data)

    if response.status_code != 200:
        logging.error(f"Errore server: {response.status_code}")
        return

    # Recupero e parsing delle lavorazioni
    lavorazioni: Lavorazioni = Lavorazioni(LOGIN_ID_TEST)
    lavorazioni.data = lavorazioni.parse_lavorazioni_html(response.text)

    logging.info(f"Estratte {len(lavorazioni.data)} lavorazioni per il consulente {LOGIN_ID_TEST}.")
    for row in lavorazioni.data:
        logging.debug(row)

    # Salvataggio
    lavorazioni.to_csv()
    logging.info(f"Lavorazioni salvate in: '{lavorazioni.output_file.relative_to(Path.cwd())}'")
