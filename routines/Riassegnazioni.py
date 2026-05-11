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
        # Imposta la sessione HTTP
        kiwi = Auth(Path(__file__) if __TEST__ else None)
        _ = kiwi.login()

        # Istanza custom per eseguire le due subroutine
        query = Riassegnazioni(kiwi, Path(__file__) if __TEST__ else None)

        # Subroutine: esegue tutte le riassegnazioni lette dal CSV delle riassegnazioni
        print("==" * 10)
        print("RIASSEGNAZIONI")
        print("==" * 10)
        query.subroutine_riassegnazioni()

        # Subroutine: esegue tutte le retrocessioni lette dal CSV delle retrocessioni
        print("==" * 10)
        print("RETROCESSIONI")
        print("==" * 10)
        query.subroutine_retrocessioni()

    except Exception as e:
        print(e)
