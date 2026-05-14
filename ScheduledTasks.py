import logging
from typing import Final, Callable, TypeAlias
import sys
from routines import (
    pulizia_quotidiana_file_obsoleti,
    estrai_utenze_attive,
    main_dashboard_fetch,
    lavorazioni_consulenti,
    run_retrocessioni,
    run_riassegnazioni,
)
from source import LOG_FILE


# Configurazione base del logging per monitorare l'esecuzione
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        # Output to console
        logging.StreamHandler(),
        # Output to file (append)
        logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
    ]
)

# Routines da eseguire, con nome descrittivo e funzione associata
RoutineEntry: TypeAlias = tuple[str, Callable[[bool], None]]
ROUTINES: Final[list[RoutineEntry]] = [
    ("pulizia_quotidiana_file_obsoleti", pulizia_quotidiana_file_obsoleti),
    ("estrai_utenze_attive", estrai_utenze_attive),
    ("main_dashboard_fetch", main_dashboard_fetch),
    ("lavorazioni_consulenti", lavorazioni_consulenti),
    ("run_retrocessioni", run_retrocessioni),
    ("run_riassegnazioni", run_riassegnazioni),
]

def main() -> None:

    # Flag globale
    # Se True: esegue gli script offline
    # facendo scraping da file HTML che simulano Kiwi
    # anziché da web
    __test__: bool = any(arg in sys.argv for arg in ('--test', '-t'))
    mode_desc: str = "TEST (Mock)" if __test__ else "PROD (Reale)"

    logging.info(f"Avvio in modalità {mode_desc}.")

    for name, routine in ROUTINES:
        print("="*80)
        try:
            logging.info(f"Avvio routine: `{name}`")
            routine(__test__)
            logging.info(f"Routine `{name}` completata con successo.")
        except Exception as e:
            logging.error(f"Errore critico nella routine `{name}`: {e}")

if __name__ == '__main__':
    main()
