# Flag globale
# Se True: esegue gli script offline
# facendo scraping da file HTML che simulano Kiwi
# anziché da web
__test__: bool = False

import logging
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
        # Output to file
        logging.FileHandler(LOG_FILE)
    ]
)

routines = [
    ("pulizia_quotidiana_file_obsoleti", pulizia_quotidiana_file_obsoleti),
    ("estrai_utenze_attive", estrai_utenze_attive),
    ("main_dashboard_fetch", main_dashboard_fetch),
    ("lavorazioni_consulenti", lavorazioni_consulenti),
    ("run_retrocessioni", run_retrocessioni),
    ("run_riassegnazioni", run_riassegnazioni)
]

def main() -> None:

    global __test__, routines

    if sys.argv[-1] in ['--test', '-t']:
        __test__ = True
        logging.info("Modalità TEST: verranno utilizzati file di mock e non saranno effettuate richieste reali.")
    else:
        logging.info("Modalità NORMALE: verranno effettuate richieste reali a Kiwi e salvati file di output.")

    for name, routine in routines:
        print("="*80)
        routine.__name__ = name
        try:
            logging.info(f"Avvio routine: `{routine.__name__}`")
            routine(__test__)
            logging.info(f"Routine `{routine.__name__}` completata con successo.")
        except Exception as e:
            logging.error(f"Errore critico nella routine `{routine.__name__}`: {e}")

if __name__ == '__main__':
    main()
