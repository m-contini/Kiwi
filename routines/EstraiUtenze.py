import logging
from pathlib import Path
from requests import Response

from source import (
    Endpoints,
    Auth,
    User,
    Utenze,
)

def run(__TEST__: bool = False) -> None:
    """
    Questo script si autentica a *Kiwi** per scaricare la tabella `tabella_ricerca_utenti`,
    contenente:
        - `user_id`
        - `username`
        - `ruolo`.

    Questo script è pensato per essere eseguito tramite uno scheduler (es. crontab).

    I dati vengono salvati in CSV e JSON con timestamp per mantenere uno storico, ai seguenti percorsi:  

    `./Utenze/YYYY_MM_DD_HH_MM_SS_user_id.csv`
    `./Utenze/YYYY_MM_DD_HH_MM_SS_user_id.json`

    In ambiente di test simula la pagina di atterraggio dopo login contenuta in 
    `./html/EstraiUtenze.html`

    Es. di struttura dei file di output:
    ### CSV
    ```plain
    21063;Contini Marco;Finance - Administrator
    ```

    ### JSON
    ```json
    {
        "user_id": 21063,
        "username": "Contini Marco",
        "ruolo": "Finance - Administrator"
    }
    ```
    """

    # Inizializzazione client e login
    client = Auth(Path(__file__) if __TEST__ else None).login()

    # Richiesta GET per ottenere la lista degli utenti di Kiwi
    response: Response = client.request('GET', Endpoints.USERLIST.value)

    # Istanza custom per effettuare parsing e salvataggio
    utenze: Utenze = Utenze(response.text)

    # Recupera utenze dal corpo della risposta HTML
    utenze.data = utenze.parse_response_utenze()
    utenze_data: list[User] = utenze.data

    # Stampa i dati
    logging.info(f"Estratte {len(utenze_data)} utenze.")
    for item in utenze_data:
        logging.debug(item)

    # Salva in CSV
    utenze.to_csv()
    logging.info(f"Utenze salvate in CSV: '{utenze.CSV_UTENZE.relative_to(Path.cwd())}'.")

    # Salva in JSON
    utenze.to_json()
    logging.info(f"Utenze salvate in JSON: '{utenze.CSV_UTENZE.with_suffix('.json').relative_to(Path.cwd())}'.")
