"""
In questo script si eseguono le ultime richieste POST per scaricare le estrazioni.
Se non si ha il CSV da cui leggere le estrazioni da effettuare, si invoca lo script per crearlo.

Di default si ha 'format'='csv'.

Per ragioni di stabilità e nel rispetto della fragilità del server, l'utente deve scegliere di segmentare l'intervallo di date desiderato.
Il segmento non può comunque superare i 20 giorni.

I file di output sono costruiti in modo da avere come nome {nome_estrazione}_{data_inizio}_{data_fine}.csv con date in formato yyyy-mm-dd
"""

import logging
from pathlib import Path
from typing import Optional, Final
from tqdm import tqdm
import sys

from source import (
    Auth,
    Endpoints,
    LOG_FILE,
)

from Estrazioni import PayloadManager, OptionManager

# Configurazione del logging per l'esecuzione standalone
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
    ]
)

def main() -> None: 

    # Flag globale
    # Se True: esegue gli script offline caricando mock HTML
    __test__: bool = any(arg in sys.argv for arg in ('--test', '-t'))
    mode_desc: str = "TEST (Mock)" if __test__ else "PROD (Reale)"
    mock_path: Optional[Path] = Path(__file__) if __test__ else None

    logging.info(f"Avvio in modalità {mode_desc}.")

    try:
        # Imposta la sessione HTTP
        kiwi = Auth(mock_path).login()
    except Exception as e:
        logging.error(f"Errore durante l'autenticazione: {e}")
        raise

    # --------------------
    # FETCH SCELTE DISPONIBILI A SISTEMA
    # --------------------

    logging.info("Recupero elenco estrazioni disponibili a sistema...")
    response = kiwi.request('GET', Endpoints.ESTRAZIONI.value)
    options = OptionManager()

    options.sync_available_options(response.text)
    options.to_csv()
    options.to_json()

    # --------------------
    # PAYLOAD GENERATION
    # --------------------
    # Se non esiste il CSV contenente lista di payload delle estrazioni da scaricare
    # crealo ora
    payloads = PayloadManager()
    payloads.generate_payload_list()
    payloads.to_csv()

    # Legge la lista di payload dal CSV
    # per ciascuno chiede di inserire numero di giorni per ciascuna estrazione.
    # Il download sarà così segmentato
    # per non appesantire il server.
    payload_list: list[dict[str, str]] = payloads.read_payload_list()

    # ------------------------------
    # Percorso in cui salvare i DOWNLOAD
    # ------------------------------
    default_dir: Final[Path] = PayloadManager.PAYLOAD_CSV.parent
    output_dir = Path(input(f'\nInserire percorso per download (Default: \'{default_dir}\'): ').strip() or default_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    conferma = input("\nProcedere con il download dei file CSV? (y/n): ").strip().lower()
    if conferma != 'y':
        print("Download annullato.")
        return

    # ------------------------------
    # Inizio sequenza di download 
    # ------------------------------
    for params in tqdm(
        payload_list, 
        desc="Download Progress", 
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
    ):

        current_payload_64, file_name = params['payload64'], params['file_name']

        # ------------------------------
        # DOWNLOAD 
        # ------------------------------
        response_txt = download_estrazione(kiwi, current_payload_64)
        if response_txt is None:
            continue

        # ---------------
        # SALVATAGGIO
        # --------------
        save_estrazione(response_txt, output_dir, file_name)

def download_estrazione(kiwi: Auth, current_payload_64: str) -> Optional[str]:

    payload = {
        'payload': current_payload_64,
        'format': 'csv'
    }
    response = kiwi.request('POST', Endpoints.DOWNLOAD.value, data=payload)

    set_cookie = response.headers.get('Set-Cookie', '')
    if 'fileDownload=true' not in set_cookie:
        logging.error(f"Errore durante il download del payload {current_payload_64[:15]}...")
        return None

    return response.text

def save_estrazione(content: str, output_dir: Path, file_name: str) -> None:
    try:
        with open(output_dir / f"{file_name}.csv", 'w', encoding='utf-8') as f:
            f.write(content)

        logging.info(f"File CSV salvato: {output_dir / f'{file_name}.csv'}")

        if (output_dir / f"{file_name}.csv").is_file():
            tqdm.write(f"File salvato: '{file_name}.csv'")
    except Exception as e:
        logging.error(f"Impossibile salvare il file {file_name}: {e}")

if __name__ == "__main__":
    main()
