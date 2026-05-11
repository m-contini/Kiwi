"""
Questo script preleva dal corpo HTML di "mutui/esporta/estrazioni"
tutte le possibili estrazioni con i loro parametri:
    - 'value', str che identifica l'estrazione, es. "AssegnazioniConsulenti"
    - 'data_filters' str contenente i filtri sulle date codificati in base64,  
        da decodificare e allegare al payload finale
    - 'text' str alias dell'estrazione così come appare su Kiwi, da trasformare in scelta int per l'utente

e salva i risultati in CSV e JSON:
    "value": "AssegnazioniConsulentiTiranaConFiltroSuAgenda",
    "data_filters": [
        {
            "name": "data_inizio",
            "type": "input",
            "default": ""
        },
        {
            "name": "data_fine",
            "type": "input",
            "default": ""
        },
        {
            "name": "consulente",
            "type": "select",
            "default": []
        }
    ]
"""
import base64
import binascii
from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any, Optional
from bs4 import BeautifulSoup
import csv

from source import ESTRAZIONI_DIR

# Percorsi dei file
OPTIONS_CSV = ESTRAZIONI_DIR / 'options.csv'
OPTIONS_JSON = ESTRAZIONI_DIR / 'options_decoded.json'

@dataclass
class Option:
    value: str
    data_filters: str
    text: str

def extract_form_data(html: str) -> Optional[list[Option]]:
    """Estrae dati dai menù a tendina disponibili nel form della pagina Estrazioni"""
    soup = BeautifulSoup(html, 'html.parser')
    estrazioni_filters = soup.find('div', {'id': 'estrazioni_filters'})
    if estrazioni_filters is None:
        print("Elemento estrazioni_filters non trovato.")
        return

    form_action = estrazioni_filters.find('form', {'action': '/mutui/esporta/estrazioni'})
    if not form_action:
        print("Elemento select non trovato.")
        return

    select = form_action.find('select', {'id': 'estrazione'})
    if not select:
        print("Form di estrazione non trovato.")
        return 

    options = select.find_all('option')
    if not options:
        print("Nessuna opzione trovata.")
        return

    data: list[Option] = []
    for option in options:
        value = option.get('value', '')
        data_filters = option.get('data-filters', '')
        text = option.get_text().strip()
        # {'value': value, 'data_filters': data_filters, 'text': text}
        data.append(Option(str(value), str(data_filters), text))

    return data

def save_to_csv(data: list[Option], file: Path):
    """Salva i dati in un file CSV"""
    headers = list(asdict(data[0]).keys())
    with open(file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers, delimiter=";")
        writer.writeheader()
        writer.writerows(asdict(option) for option in data)
    print(f"Dati salvati in {file}")

def decode_base64(data: str) -> Optional[dict[str, str]]:
    """Decodifica una stringa base64 e verifica se è un JSON valido."""
    try:
        decoded_data = base64.b64decode(data).decode('utf-8')
        json_data = json.loads(decoded_data)
        return json_data
    except (binascii.Error, json.JSONDecodeError):
        return

def save_to_json(data: list[Option], file: Path):

    decoded_data: list[dict[str, Any]] = []
    for option in data:
        value = option.value
        decoded_data_filters = decode_base64(option.data_filters)

        if decoded_data_filters is None:
            continue

        decoded_data.append({
            "value": value,
            "data_filters": decoded_data_filters
        })

    # Scrive i dati decodificati nel file JSON
    with open(file, mode='w', encoding='utf-8') as jsonfile:
        json.dump(decoded_data, jsonfile, ensure_ascii=False, indent=4)
    print(f"Dati salvati in {file}")
