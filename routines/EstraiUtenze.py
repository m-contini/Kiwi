from pathlib import Path

from source import (
    Endpoints,
    Auth,
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

    I dati vengono salvati in CSV e JSON, sovrascrivendo quelli esistenti, ai seguenti percorsi:  

    `./Utenze/user_id.csv`
    `./Utenze/user_id.json`

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

    try:
        # Imposta la sessione HTTP
        kiwi = Auth(Path(__file__) if __TEST__ else None)
        _ = kiwi.login()

        # Istanza custom per effettuare parsing e salvataggio
        utenze = Utenze()

        # Richiesta GET per ottenere la lista degli utenti di Kiwi
        response = kiwi.get_request(Endpoints.USERLIST.value)

        # Recupera utenze dal corpo della risposta HTML
        utenze.data = utenze.parse_response_utenze(response.text)

        # Stampa i dati
        for item in utenze.data:
            print(item)

        # Salva in CSV
        utenze.to_csv()

        # Salva in JSON
        utenze.to_json()

    except Exception as e:
        print(e)
