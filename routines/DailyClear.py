import logging
import shutil

from source import HomeKiwiOutput

def run(__TEST__: bool = False) -> None:
    """
    Questa routine si occupa della pulizia delle directory di output.
    Viene utilizzata per pulire i file temporanei e i report generati (HTML, CSV, JSON)
    salvati all'interno della cartella 'HomeKiwi'

    Solitamente viene eseguito tramite scheduler (es. crontab) una volta al giorno.

    La sua esecuzione è facoltativa.

    In ambiente di test stampa i nomi dei file senza rimuoverli effettivamente
    """

    # Elenco cartelle da rimuovere
    directories: list[HomeKiwiOutput] = [
        HomeKiwiOutput.CSV_DIR,
        HomeKiwiOutput.HTML_DIR,
        HomeKiwiOutput.JSON_DIR
    ]

    for directory in directories:

        path = directory.value

        if not path.exists():
            continue

        # Cancella contenuto delle cartelle
        for file_path in path.iterdir():

            if file_path.name.startswith('.'):
                continue

            logging.info(f"Rimozione {file_path.name}...")
            if __TEST__:
                continue

            try:
                # Se file o collegamento
                if file_path.is_file() or file_path.is_symlink():
                    file_path.unlink()
                # Se cartella
                if file_path.is_dir():
                    shutil.rmtree(file_path)
            except Exception as e:
                logging.error(f'Errore: {e}')
