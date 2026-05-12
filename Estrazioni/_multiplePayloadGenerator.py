"""
Questo script contiene solo funzioni per produrre payload ai fini del download di un'estrazione (anche più di una alla volta).

Non è stand-alone, ma viene evocato in `./routines/DownloadEstrazioni.py` se non esiste file di output.

Si chiede all'utente la scelta di una o più opzioni estrazioni
tra quelle contenute in `./Estrazioni/options.csv`, che ha questa struttura:
    value;data_filters;text
    AssegnazioniConsulenti;64ENCODEDSTR;Nome_Visibile_a_FrontEnd

Da queste estrazioni viene costruito lo scheletro del payload per ogni richiesta POST deputata al download.
Nel payload caricato bisogna inserire, tramite input da utente, i valori necessari (es. intervallo date).
Si ricodifica in base64 per avere il payload come stringa da allegare alla richiesta.

In un altro script `./routines/DownloadEstrazioni.py` si eseguono le richieste POST all'endpoint `/download`
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, TypeAlias
import csv
import base64
import json

from source import __TEST__, ESTRAZIONI_DIR, Estrazione

_DataFiltersType: TypeAlias = list[dict[str, str]]

@dataclass
class _Option:
    value: str
    data_filters: _DataFiltersType
    text: str | None = None

class PayloadManager:

    OPTIONS_JSON: Path = ESTRAZIONI_DIR / 'options_decoded.json'
    PAYLOAD_CSV: Path = ESTRAZIONI_DIR / 'PayloadForDownload.csv'

    def __init__(self) -> None:
        self.data: list[str] = []
        self.file = self.OPTIONS_JSON
        self.output_file: Path = self.PAYLOAD_CSV

    def generate_payload_list(self) -> None:
        """Gestisce l'interazione con l'utente per creare il file PayloadForDownload.csv."""

        if self.PAYLOAD_CSV.is_file() and not __TEST__:
            return

        print("Costruzione lista di payload per estrarre dati da database...")
        data = self._choose_extractions()

        for option in data:
            print(f"\nGenerazione payload per: {option.value}")
            payload = self._prompt(option)
            self.data.append(self._to_base64(payload))

    def to_csv(self) -> None:
        """Salva i payload codificati in un file CSV"""
        with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=";")
            # Scrivi l'intestazione
            writer.writerow(['payload', 'format'])
            # Scrivi i dati
            for payload_base64 in self.data:
                writer.writerow([payload_base64, 'csv'])
        print(f"Payload codificati salvati in {self.PAYLOAD_CSV}")

    def read_payload_list(self) -> list[dict[str, str]]:
        with open(self.PAYLOAD_CSV, 'r', encoding='utf-8') as csvfile:
            reader = list(csv.DictReader(csvfile, delimiter=';'))

        # Chiavi: 'payload_str', 'file_name'
        payload_list: list[dict[str, str]] = []
        for i, row in enumerate(reader):
            payload_str: str = row['payload']
            params: dict[str, str] = self._payload_decode(payload_str)

            print(f"Riga {i+1} - payload (decoded):")
            print(json.dumps(params, indent=2))

            step = self._segment_length()
            print(f"Suddivisione in segmenti da {step} giorni...")

            # Lista di range di date (segmenti sequenziali dell'estrazione)
            date_ranges_list = self._split_date_range(
                start_date=self._parse_date(params['data_inizio']),
                end_date=self._parse_date(params['data_fine']),
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
                    end_date=end_date
                )

                payload_list.append({
                    'payload64': current_payload_64,
                    'file_name': estrazione.as_str()
                })

        return payload_list

    def _choose_extractions(self) -> list[_Option]:
        # Legge il file JSON
        with open(self.file, 'r', encoding='utf-8') as f:
            options_list: list[dict[Any, Any]] = json.load(f)

        options: list[_Option] = []
        for option in options_list:
            options.append(
                _Option(
                    value=option['value'],
                    data_filters=option['data_filters'],
                    text=option.get('text', None)
                )
            )

        # Ordinamento per attributo value
        options.sort(key=lambda x: x.value)

        # Stampa le opzioni disponibili ordinate
        print("\nScegli una o più opzioni (separate da virgola):")
        for i, opzione in enumerate(options):
            print(f"{i + 1}. {opzione.value}")

        # Ottiene le scelte dell'utente
        while True:
            scelte_input = input("\nInserisci i numeri delle opzioni scelte (separati da virgola): ")
            try:
                choices = [int(num.strip()) - 1 for num in scelte_input.split(',')]
                if all(0 <= scelta < len(options) for scelta in choices):
                    break
            except ValueError:
                print(f"Inserisci numeri validi tra 1 e {len(options)} separati da virgole.")

        return [options[choice] for choice in choices]

    def _prompt(self, option: _Option) -> dict[str, str]:

        value: str = option.value
        date_filters: _DataFiltersType = option.data_filters

        payload = {"estrazione": value}

        for date_filter in date_filters:
            name = date_filter["name"]
            tipo = date_filter["type"]
            default = date_filter.get("default", "")

            valore = ""
            print()

            if tipo == "input":
                valore = input(f"Inserisci il valore per {name} (premer Enter per utilizzare il valore di default: '{default}'): ") or default

            if tipo == "select":
                possible_values: list[dict[str, str]] = date_filter.get("default", [])
                print(f"Seleziona un valore per {name}:")
                for i, opt in enumerate(possible_values):
                    print(f"{i+1}. {opt['name']} ({opt['value']})")
                while True:
                    try:
                        scelta = int(input("\nInserisci il numero dell'opzione scelta: ")) - 1
                        if not 0 <= scelta < len(possible_values):
                            print(f"Per favore, inserisci un numero tra 1 e {len(possible_values)}.")
                            continue
                        valore = possible_values[scelta]["value"]
                        break
                    except ValueError:
                        print("Per favore, inserisci un numero valido.")

            payload[name] = valore

        return payload

    @staticmethod
    def _to_base64(payload: dict[str, str]) -> str:
        # Converti il payload in JSON con escaping dei caratteri slash
        payload_str = json.dumps(payload, ensure_ascii=False, separators=(',', ':'))

        # Escapa i caratteri /
        payload_str_escaped = payload_str.replace("/", "\\/")

        # Converti la stringa in binario
        payload_bytes = payload_str_escaped.encode('utf-8')

        # Codifica in base64
        base64_bytes = base64.b64encode(payload_bytes)

        # Converti in stringa
        return base64_bytes.decode('utf-8')

    @staticmethod
    def _payload_decode(payload_str: str) -> dict[str, str]:
        return json.loads(base64.b64decode(payload_str).decode('utf-8'))

    @staticmethod
    def _segment_length() -> int:
        while True:
            try:
                step = int(input("\nInserisci la larghezza in giorni dei singoli intervalli di date (tra 1 e 20): "))
                if not (1 <= step <= 20):
                    print("Errore: è possibile scaricare un massimo di 20 giorni alla volta.")
                    continue
                return step
            except ValueError:
                print("Errore: devi inserire un numero intero.")

    @staticmethod
    def _split_date_range(start_date: datetime, end_date: datetime, interval_days: int) -> list[tuple[datetime, datetime]]:

        intervals: list[tuple[datetime, datetime]] = []

        start = start_date
        while start < end_date:
            end = min(start + timedelta(days=interval_days), end_date)
            intervals.append((start, end))
            start = end + timedelta(days=1)
        return intervals

    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        """Converti data in formato YYYY-MM-DD."""
        if not date_str:
            date_str = datetime.now().strftime('%d/%m/%Y')

        for fmt in ('%d/%m/%Y', '%d/%m/%y', '%d-%m-%Y', '%d-%m-%y', '%Y-%m-%d'):
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                pass
        raise ValueError(f"Formato data non riconosciuto: '{date_str}'")
