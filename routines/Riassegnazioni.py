import logging
from pathlib import Path

from source import (
    Auth,
    Riassegnazioni,
    Endpoints
)

def run(__TEST__: bool = False) -> None:
    """
    Questo script si autentica a **Kiwi** per automatizzare la `riassegnazione` di agende
    da un consulente ad un altro (assegnatario) leggendo da un file CSV di input il cellulare,
    che permette di identificare l'agenda da riassegnare.

    Steps
    Il processo segue questi step:
    1.  Legge `./Riassegnazioni/input_cellulare.csv` contenente
        `consulente_id`, `assegnatario_id` e `cellulare`.
    2. Per ogni `cellulare`, interroga **Kiwi** per recuperare 
        `id_anagrafica` e `id_agenda`.
    3. Per ciascuna riga si invia una richiesta POST all'endpoint di riassegnazione,
        con `id_anagrafica` e `id_agenda` nel payload, per pushare la modifica.

    Questo script è progettato per essere eseguito tramite uno scheduler (es. crontab).
    """

    # Definiamo il mock_path una volta sola
    mock_path = Path(__file__) if __TEST__ else None

    # Imposta la sessione HTTP
    client = Auth(mock_path)
    client.login()

    # Istanza custom per eseguire le due subroutine
    query = Riassegnazioni(client)

    # Fetch dei dati da file
    riassegnazioni = query.get_riassegnazioni_list(query.CAMBI_STATO_CSV)
    logging.info(f"Trovate {len(riassegnazioni)} riassegnazioni da eseguire.")

    for riassegnazione in riassegnazioni:
        try:
            _ = client.request('POST', Endpoints.RIASSEGNAZ.value, riassegnazione.as_dict())
            logging.debug(f"Riassegnazione da {riassegnazione.consulente_id} a {riassegnazione.assegnatario_id} per agenda {riassegnazione.agenda} completata!")
        except Exception as e:
            logging.error(f"Riassegnazione {riassegnazione.anagrafica}({riassegnazione.agenda}) fallita: {e}")
            continue

    logging.info("Riassegnazioni completate.")
