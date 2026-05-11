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
import logging
import base64
import binascii
from dataclasses import asdict, dataclass
import json
from typing import Any, Optional
from bs4 import BeautifulSoup, Tag
import csv

from source import __TEST__, ESTRAZIONI_DIR

@dataclass
class _Option:
    value: str
    data_filters: str
    text: str

class OptionManager:

    OPTIONS_CSV = ESTRAZIONI_DIR / 'options.csv'

    def __init__(self) -> None:
        self.data: list[_Option] = []
        self.file = self.OPTIONS_CSV

    def sync_available_options(self, html: str):
        """Recupera le opzioni dal server se mancanti o in modalità test."""
        jsonf = self.file.with_suffix('.json')
        csvf = self.file.with_suffix('.csv')
        if (jsonf.is_file() or csvf.is_file()) and not __TEST__:
            return

        self._extract_form_data(html) 

    def _extract_form_data(self, html: str) -> None:
        """Estrae dati dai menù a tendina disponibili nel form della pagina Estrazioni"""
        soup = BeautifulSoup(html, 'html.parser')
        estrazioni_filters = soup.find('div', {'id': 'estrazioni_filters'})
        if not isinstance(estrazioni_filters, Tag):
            logging.error("Elemento 'estrazioni_filters' non trovato nell'HTML.")
            return

        form_action = estrazioni_filters.find('form', {'action': '/mutui/esporta/estrazioni'})
        if not isinstance(form_action, Tag):
            logging.error("Form di estrazione non trovato.")
            return

        select = form_action.find('select', {'id': 'estrazione'})
        if not isinstance(select, Tag):
            logging.error("Menu a tendina 'estrazione' non trovato.")
            return

        options = select.find_all('option')
        if not options:
            logging.warning("Nessuna opzione di estrazione trovata nel form.")
            return

        for option in options:
            value = option.get('value', '')
            data_filters = option.get('data-filters', '')
            text = option.get_text().strip()
            # {'value': value, 'data_filters': data_filters, 'text': text}
            self.data.append(_Option(str(value), str(data_filters), text))

    def to_csv(self) -> None:
        """Salva i dati in un file CSV"""
        file = self.file.with_suffix('.csv')

        if not self.data:
            logging.warning(f"Nessun dato da salvare in CSV per {file}")
            return

        headers = list(asdict(self.data[0]).keys())
        with open(file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers, delimiter=";")
            writer.writeheader()
            writer.writerows(asdict(option) for option in self.data)
        logging.info(f"Opzioni salvate in CSV: {file}")

    @staticmethod
    def _decode_base64(data: str) -> Optional[dict[str, str]]:
        """Decodifica una stringa base64 e verifica se è un JSON valido."""
        try:
            decoded_data = base64.b64decode(data).decode('utf-8')
            json_data = json.loads(decoded_data)
            return json_data
        except (binascii.Error, json.JSONDecodeError):
            return

    def to_json(self) -> None:
        """Decodifica i filtri base64 e salva l'intera struttura in JSON"""
        file = self.file.with_suffix('.json')

        if not self.data:
            logging.warning(f"Nessun dato da salvare in JSON per {file}")
            return

        decoded_data: list[dict[str, Any]] = []
        for option in self.data:
            value = option.value
            decoded_data_filters = self._decode_base64(option.data_filters)

            if decoded_data_filters is None:
                continue

            decoded_data.append({
                "value": value,
                "data_filters": decoded_data_filters
            })

        # Scrive i dati decodificati nel file JSON
        with open(file, mode='w', encoding='utf-8') as jsonfile:
            json.dump(decoded_data, jsonfile, ensure_ascii=False, indent=4)
        logging.info(f"Opzioni decodificate salvate in JSON: {file}")
