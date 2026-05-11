import logging
from pathlib import Path

from source import (
    Auth,
    Riassegnazioni,
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

    try:
        # Definiamo il mock_path una volta sola
        mock_path = Path(__file__) if __TEST__ else None

        # Imposta la sessione HTTP
        kiwi = Auth(mock_path)
        kiwi.login()

        # Istanza custom per eseguire le due subroutine
        query = Riassegnazioni(kiwi, mock_path)

        # Subroutine: esegue tutte le riassegnazioni lette dal CSV delle riassegnazioni
        query.subroutine_riassegnazioni()

        # Subroutine: esegue tutte le retrocessioni lette dal CSV delle retrocessioni
        query.subroutine_retrocessioni()

    except Exception as e:
        logging.error(f"Errore durante la routine di riassegnazione/retrocessione: {e}", exc_info=True)
        raise
