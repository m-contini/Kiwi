"""
In questo script si eseguono le ultime richieste POST per scaricare le estrazioni.
Se non si ha il CSV da cui leggere le estrazioni da effettuare, si invoca lo script per crearlo.

Di default si ha 'format'='csv'.

Per ragioni di stabilità e nel rispetto della fragilità del server, l'utente deve scegliere di segmentare l'intervallo di date desiderato.
Il segmento non può comunque superare i 20 giorni.

I file di output sono costruiti in modo da avere come nome {nome_estrazione}_{data_inizio}_{data_fine}.csv con date in formato yyyy-mm-dd
"""

from pathlib import Path
import base64
import json
import csv
import os
from datetime import datetime, timedelta
from typing import Optional
from tqdm import tqdm

from source import (
    __TEST__,
    Auth,
    Endpoints,
    ESTRAZIONI_DIR,
    Estrazione
)

# Percorsi file
OPTIONS_CSV = ESTRAZIONI_DIR / 'options.csv'
OPTIONS_JSON = ESTRAZIONI_DIR / 'options_decoded.json'
PAYLOAD_CSV = ESTRAZIONI_DIR / 'PayloadForDownload.csv'

def main() -> None: 

    try:
        # Imposta la sessione HTTP
        kiwi = Auth(Path(__file__) if __TEST__ else None)
        kiwi.login()
    except Exception as e:
        print(e)
        raise

    # --------------------
    # FETCH SCELTE DISPONIBILI A SISTEMA
    # --------------------
    sync_available_options(kiwi)

    # --------------------
    # PAYLOAD GENERATION
    # --------------------
    generate_payload_list(PAYLOAD_CSV)

    # Legge la lista di payload dal CSV
    # per ciascuno chiede di inserire numero di giorni per ciascuna estrazione.
    # Il download sarà così segmentato
    # per non appesantire il server.
    payload_list = read_payload_list(PAYLOAD_CSV)


    # ------------------------------
    # Percorso in cui salvare i DOWNLOAD
    # ------------------------------
    output_dir = Path(input('\nInserire percorso per download (Default: \'./Estrazioni\'): ').strip() or ESTRAZIONI_DIR)
    os.makedirs(output_dir, exist_ok=True)

    conferma = input("\nProcedere con il download dei file CSV? (y/n): ").strip().lower()
    if conferma != 'y':
        print("Download annullato.")
        return

    # ------------------------------
    # Inizio sequenza di download 
    # ------------------------------
    for params in tqdm(payload_list, desc="Download Progress", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"):

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

def sync_available_options(session: Auth):
    """Recupera le opzioni dal server se mancanti o in modalità test."""
    if (OPTIONS_JSON.is_file() or OPTIONS_CSV.is_file()) and not __TEST__:
        return

    from Estrazioni._estrazioniDisponibiliDownload import (extract_form_data, save_to_csv, save_to_json, Option)

    print("Recupero elenco estrazioni disponibili a sistema...")
    response = session.get_request(Endpoints.ESTRAZIONI.value)
    data: list[Option] = extract_form_data(response.text)
    
    if data:
        save_to_csv(data, OPTIONS_CSV)
        save_to_json(data, OPTIONS_JSON)
    else:
        print("Nessun dato estratto dal form di estrazione.")

def generate_payload_list(payload_list_file: Path) -> None:
    """Gestisce l'interazione con l'utente per creare il file PayloadForDownload.csv."""

    if payload_list_file.is_file() and not __TEST__:
        return

    # Se non esiste il CSV contenente lista di payload delle estrazioni da scaricare
    # crealo ora
    from Estrazioni._multiplePayloadGenerator import (choose_extractions, prompt_for_payload, payload_to_base64, payload_to_csv)

    print("Costruzione lista di payload per estrarre dati da database...")
    selected_options = choose_extractions(OPTIONS_JSON)
    payloads_base64: list[str] = []

    for option in selected_options:
        print(f"\nGenerazione payload per: {option.value}")
        payload = prompt_for_payload(option)
        payloads_base64.append(payload_to_base64(payload))

    payload_to_csv(payloads_base64, payload_list_file)
    print(f"Payload codificati salvati in {payload_list_file}")

def read_payload_list(payload_list_file: Path) -> list[dict[str, str]]:
    with open(payload_list_file, 'r', encoding='utf-8') as csvfile:
        reader = list(csv.DictReader(csvfile, delimiter=';'))

    # Chiavi: 'payload_str', 'file_name'
    payload_list: list[dict[str, str]] = []
    for i, row in enumerate(reader):
        payload_str: str = row['payload']
        params: dict[str, str] = payload_decode(payload_str)

        print(f"Riga {i+1} - payload (decoded):")
        print(json.dumps(params, indent=2))

        step = segment_length()
        print(f"Il range di date verrà suddiviso in intervalli da {step} giorni.\n")

        # Lista di range di date (segmenti sequenziali dell'estrazione)
        date_ranges_list = split_date_range(
            start_date=parse_date(params['data_inizio']),
            end_date=parse_date(params['data_fine']),
            interval_days=step
        )

        # ------------------------------
        # LISTA DI PAYLOAD PER DOWNLOAD MULTIPLI
        # ------------------------------
        for j, (start_date, end_date) in enumerate(date_ranges_list):
            params['data_inizio'] = start_date.strftime('%d/%m/%y')
            params['data_fine'] = end_date.strftime('%d/%m/%Y')

            current_payload_64 = base64.b64encode(
                json.dumps(params).encode('utf-8')
            ).decode('utf-8')

            estrazione = Estrazione(
                nome_estrazione=params['estrazione'],
                indice=j + 1,
                start_date=start_date,
                end_date=start_date,
            )

            payload_list.append({
                'payload64': current_payload_64,
                'file_name': estrazione.as_str()
            })

    return payload_list

def download_estrazione(kiwi: Auth, current_payload_64: str) -> Optional[str]:

        payload = {
            'payload': current_payload_64,
            'format': 'csv'
        }
        response = kiwi.post_request(Endpoints.DOWNLOAD.value, data=payload)

        set_cookie = response.headers.get('Set-Cookie', '')
        if 'fileDownload=true' not in set_cookie:
            print(f"\nErrore: Non è stato possibile scaricare il file CSV.")
            return

        return response.text

def save_estrazione(content: str, output_dir: Path, file_name: str) -> None:

        with open(output_dir / f"{file_name}.csv", 'w') as f:
            f.write(content)

        print(f"\nFile CSV salvato: {output_dir / f"{file_name}.csv"}")

        if (output_dir / f"{file_name}.csv").is_file():
            tqdm.write(f"File salvato: '{file_name}.csv'")

def split_date_range(start_date: datetime, end_date: datetime, interval_days: int) -> list[tuple[datetime, datetime]]:

    intervals: list[tuple[datetime, datetime]] = []

    start = start_date
    while start < end_date:
        end = min(start + timedelta(days=interval_days), end_date)
        intervals.append((start, end))
        start = end + timedelta(days=1)
    return intervals

def parse_date(date_str: str) -> datetime:
    """Converti data in formato YYYY-MM-DD."""
    if not date_str:
        date_str = datetime.now().strftime('%d/%m/%Y')

    for fmt in ('%d/%m/%Y', '%d/%m/%y', '%d-%m-%Y', '%d-%m-%y', '%Y-%m-%d'):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            pass
    raise ValueError(f"Formato data non riconosciuto: '{date_str}'")

def segment_length() -> int:
    while True:
        try:
            step = int(input("\nInserisci la larghezza in giorni dei singoli intervalli di date (tra 1 e 20): "))
            if not (1 <= step <= 20):
                print("Errore: è possibile scaricare un massimo di 20 giorni alla volta.")
                continue
            return step
        except ValueError:
            print("Errore: devi inserire un numero intero.")

def payload_decode(payload_str: str) -> dict[str, str]:
    return json.loads(base64.b64decode(payload_str).decode('utf-8'))

if __name__ == "__main__":
    main()
