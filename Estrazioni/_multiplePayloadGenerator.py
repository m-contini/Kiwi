"""
Questo script contiene solo funzioni per produrre payload ai fini del download di un'estrazione (anche più di una alla volta).

Non è stand-alone, ma viene evocato in `./routines/EstrazioniDownload.py` se non esiste file di output.

Si chiede all'utente la scelta di una o più opzioni estrazioni
tra quelle contenute in `./Estrazioni/options.csv`, che ha questa struttura:
    value;data_filters;text
    AssegnazioniConsulenti;64ENCODEDSTR;Nome_Visibile_a_FrontEnd

Da queste estrazioni viene costruito lo scheletro del payload per ogni richiesta POST deputata al download.
Nel payload caricato bisogna inserire, tramite input da utente, i valori necessari (es. intervallo date).
Si ricodifica in base64 per avere il payload come stringa da allegare alla richiesta.

In un altro script `./routines/EstrazioniDownload.py` si eseguono le richieste POST all'endpoint `/download`
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeAlias, Union
import csv
import base64
import json

from source import ROOT

# Percorsi file
OPTIONS_JSON = ROOT / 'options_decoded.json'
PAYLOAD_CSV = ROOT / 'PayloadForDownload.csv'

DataFiltersType: TypeAlias = list[dict[str, str]]
OptionType: TypeAlias = dict[
    str,
    Union[None, str, DataFiltersType]
]

@dataclass
class Option:
    value: str
    data_filters: DataFiltersType
    text: str | None = None

def choose_extractions(path: Path) -> list[Option]:
    # Legge il file JSON
    with open(path, 'r', encoding='utf-8') as f:
        options_list: list[dict[Any, Any]] = json.load(f)

    options: list[Option] = []
    for option in options_list:
        options.append(
            Option(
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

def prompt_for_payload(option: Option) -> dict[str, str]:

    value: str = option.value
    date_filters: DataFiltersType = option.data_filters

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

def payload_to_base64(payload: dict[str, str]) -> str:
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

def payload_to_csv(payload_list: list[str], output_file: Path):
    """Salva i payload codificati in un file CSV"""
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        # Scrivi l'intestazione
        writer.writerow(['payload', 'format'])
        # Scrivi i dati
        for payload_base64 in payload_list:
            writer.writerow([payload_base64, 'csv'])
