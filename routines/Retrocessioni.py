import logging
from pathlib import Path

from source import (
    Auth,
    Endpoints,
    Riassegnazioni,
    SearchForm
)

def run(__TEST__: bool = False) -> None:
    """
    Questo script si autentica a **Kiwi** per automatizzare:
    - `Riassegnazione` di agende da un consulente all'altro
    - `Retrocessione` di agende
    basandosi su un file CSV di input.

    Il processo segue questi step:
    1.  a. Legge `./RiassegnazioniChat/input_cellulare.csv` contenente
        `consulente_id`, `assegnatario_id` e `cellulare`.
        b. Legge `./RiassegnazioniChat/input_cellulare_retrocessioni_di_stato.csv`
        contenente `cellulare` e `idEsito`.
    2. Per ogni `cellulare`, interroga **Kiwi** per recuperare 
        `id_anagrafica` e `id_agenda`.

    Per ciascuna riga di entrambi i file, si invia una richiesta POST all'endpoint di riassegnazione/retrocessione,
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
    retrocessioni = query.get_retrocessioni_list(query.RETROCESSIONI_CSV)
    logging.info(f"Trovate {len(retrocessioni)} retrocessioni da eseguire.")

    for retrocessione in retrocessioni:
        cellulare = retrocessione.cellulare
        id_esito = retrocessione.id_esito

        # Effettua la ricerca per cellulare
        payload = SearchForm(
            ricerca_telefono=cellulare,
        )

        try:
            query.response = client.post_request(Endpoints.RICERCA.value, payload.as_dict())

            # Estrai Anagrafica_id e Agenda_id
            agenda = query.parse_agenda(query.ANAGRAFICA_RICERCA_NAME)

            logging.debug(f"Retrocessione Anagrafica(Agenda) -> {agenda.anagrafica}({agenda.agenda})")

            # Aggiorna lo stato
            _ = client.post_request(Endpoints.UPDATE.value, retrocessione.as_dict(agenda))
            # Ottieni lo status di destinazione dall'ultimo carattere di id_esito
            logging.debug(f"Retrocessione in stato {str(id_esito)[-1]} per agenda {agenda.agenda} completata!")
        except Exception as e:
            logging.error(f"Operazione per cellulare '{cellulare}' fallita: {e}")
            continue

    logging.info("Retrocessioni completate.")
