import logging
from routines import (
    pulizia_quotidiana_file_obsoleti,
    estrai_utenze_attive,
    main_dashboard_fetch,
    lavorazioni_consulenti,
    riassegnazioni_retrocessioni
)
from source import __TEST__, LOG_FILE

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

if __name__ == '__main__':
    routines = [
        ("pulizia_quotidiana_file_obsoleti", pulizia_quotidiana_file_obsoleti),
        ("estrai_utenze_attive", estrai_utenze_attive),
        ("main_dashboard_fetch", main_dashboard_fetch),
        ("lavorazioni_consulenti", lavorazioni_consulenti),
        ("riassegnazioni_retrocessioni", riassegnazioni_retrocessioni)
    ]

    for name, routine in routines:
        routine.__name__ = name
        try:
            logging.info(f"Avvio routine: `{routine.__name__}`")
            routine(__TEST__)
            logging.info(f"Routine `{routine.__name__}` completata con successo.")
        except Exception as e:
            logging.error(f"Errore critico nella routine `{routine.__name__}`: {e}", exc_info=True)
