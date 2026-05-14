import logging
from pathlib import Path
from typing import Final, Optional

from source import (
    Auth,
    Endpoints,
    Riassegnazioni,
    SearchForm,
    Retrocessione,
    Agenda
)

def run(__TEST__: bool = False) -> None:
    """
    Questo script si autentica a **Kiwi** per automatizzare la `retrocessione` di agende
    prese da un file CSV di input in cui si ha `cellulare` e `idEsito` a cui retrocedere.

    Steps:
    1.  Legge `./Riassegnazioni/input_cellulare_retrocessioni_di_stato.csv`
        contenente `cellulare` e `idEsito`.
    2. Per ogni `cellulare`, interroga **Kiwi** per recuperare 
        `id_anagrafica` e `id_agenda`.
    3. Per ciascuna riga si invia una richiesta POST all'endpoint di retrocessione,
        con `id_anagrafica` e `id_agenda` nel payload, per pushare la modifica.

    Questo script è progettato per essere eseguito tramite uno scheduler (es. crontab).
    """

    # Definiamo il mock_path una volta sola
    mock_path: Final[Optional[Path]] = Path(__file__) if __TEST__ else None

    # Inizializzazione client e login
    client = Auth(mock_path).login()

    # Istanza custom per eseguire le due subroutine
    query: Riassegnazioni = Riassegnazioni(client)

    # Fetch dei dati da file
    retrocessioni: list[Retrocessione] = query.get_retrocessioni_list(query.RETROCESSIONI_CSV)
    logging.info(f"Trovate {len(retrocessioni)} retrocessioni da eseguire.")

    for retrocessione in retrocessioni:
        cellulare: str = retrocessione.cellulare
        id_esito: str = retrocessione.id_esito

        # Effettua la ricerca per cellulare
        payload: SearchForm = SearchForm(
            ricerca_telefono=cellulare,
        )

        try:
            query.response = client.request('POST', Endpoints.RICERCA.value, payload.as_dict())

            # Estrai Anagrafica_id e Agenda_id
            agenda: Agenda = query.parse_agenda(query.ANAGRAFICA_RICERCA_NAME)

            logging.debug(f"Retrocessione Anagrafica(Agenda) -> {agenda.anagrafica}({agenda.agenda})")

            # Aggiorna lo stato
            _ = client.request('POST', Endpoints.UPDATE.value, retrocessione.as_dict(agenda))
            # Ottieni lo status di destinazione dall'ultimo carattere di id_esito
            logging.debug(f"Retrocessione in stato {str(id_esito)[-1]} per agenda {agenda.agenda} completata!")
        except Exception as e:
            logging.error(f"Operazione per cellulare '{cellulare}' fallita: {e}")
            continue

    logging.info("Retrocessioni completate.")
