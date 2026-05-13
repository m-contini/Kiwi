import logging
from pathlib import Path
from typing import Any, Literal, Optional
from bs4 import BeautifulSoup, ResultSet, Tag
import re
import csv
import json
from datetime import datetime
from dataclasses import asdict, fields

# Costanti
from .const import (
    LAVORAZIONI_DIR,
    RIASSEGNAZIONI_DIR,
    UTENZE_DIR,
    HomeKiwiOutput,
    Endpoints,
)
from .exceptions import FetchError

# Tipi di dato
from .types import (
    Agenda,
    Params,
    Retrocessione,
    Riassegnazione,
    SearchForm,
    User
)

from .kiwi import Auth

class Riassegnazioni:

    ANAGRAFICA_RICERCA_NAME: str = 'risultati_ricerca_anagrafica'
    RICERCA_URL: str = Endpoints.RICERCA.value

    # consulente_id;assegnatario_id;anagrafica_list
    CSV_AGENDE: Path = RIASSEGNAZIONI_DIR / "output_anagrafica_list.csv"

    # consulente_id;assegnatario_id;cellulare
    CAMBI_STATO_CSV : Path = RIASSEGNAZIONI_DIR / "input_cellulare.csv"

    # cellulare;idEsito
    RETROCESSIONI_CSV: Path = RIASSEGNAZIONI_DIR / 'input_cellulare_retrocessioni_di_stato.csv'

    def __init__(self, kiwi: Auth) -> None:
        self.kiwi = kiwi
        self.response = None

    def get_riassegnazioni_list(self, input_csv_file: Path) -> list[Riassegnazione]:

        # Carica il CSV e costruisce la query
        query_list = self._get_query_params_list(input_csv_file)
        if query_list is None:
            raise FetchError("Nessuna query costruita dal CSV riassegnazioni.")

        # Itera sui payloads
        all_results: list[Riassegnazione] = []
        for params in query_list:
            # Crea il payload per la richiesta POST
            payload = SearchForm(
                ricerca_id_anagrafica='',
                ricerca_telefono=params.cellulare,
                ricerca_email='',
                ricerca_codice_fiscale='',
                ricerca_anagrafica='Ricerca'
            )

            try:
                # Esegui la richiesta POST
                self.response = self.kiwi.request('POST', self.RICERCA_URL, payload.as_dict())
                agenda: Agenda = self.parse_agenda(self.ANAGRAFICA_RICERCA_NAME)
            except Exception as e:
                logging.error(f"Lookup per cellulare '{params.cellulare}' fallita: {e}")
                continue

            all_results.append(
                Riassegnazione(
                    consulente_id=params.consulente_id,
                    assegnatario_id=params.assegnatario_id,
                    anagrafica=agenda.anagrafica,
                    agenda=agenda.agenda
                )
            )

        if not all_results:
            raise ValueError("Nessuna riassegnazione trovata.")

        return all_results

    def get_retrocessioni_list(self, input_csv_file: Path) -> list[Retrocessione]:
        # Leggi il CSV e ottieni i numeri di cellulare e gli idEsito
        with open(input_csv_file, 'r', encoding='utf-8') as f:
            return [
                Retrocessione(**row) for row in csv.DictReader(f, delimiter=';')
            ]

    @staticmethod
    def _get_query_params_list(input_csv_path: Path) -> Optional[list[Params]]:
        """Carica il CSV con la lista di query."""

        try:
            # Leggi il CSV e forza la colonna 'cellulare' come stringa
            data: list[Params] = []
            with open(input_csv_path, 'r', encoding='utf-8') as f:
                for row in csv.DictReader(f, delimiter=';'):
                    data.append(Params(**row))
                return data
        except KeyError:
            logging.error(f"Colonna 'cellulare' non trovata nel CSV {input_csv_path}")
        except FileNotFoundError:
            logging.error(f"File CSV non trovato: {input_csv_path}")
        return None

    def parse_agenda(self, table_id: str) -> Agenda:
        """Converte il corpo della risposta HTTP in una lista di dizionari"""

        if self.response is None:
            raise FetchError("Impossibile parsare l'agenda: nessuna risposta precedente disponibile.")

        # Parsing del contenuto HTML con BeautifulSoup
        soup = BeautifulSoup(self.response.content, 'html.parser')

        # Trova la tabella con l'id specificato
        table = soup.find('table', {'id': table_id})
        if table is None:
            raise ValueError(f"Nessuna tabella con id '{table_id}' trovata.")

        agenda = self._extract_anagrafica_agenda(table)
        if agenda is None:
            raise ValueError(f"Nessuna agenda valida trovata nella tabella {table_id}.")

        return agenda

    @staticmethod
    def _extract_anagrafica_agenda(table: Tag) -> Optional[Agenda]:
        """Estrai il valore di Agenda e Anagrafica."""

        tbody = table.find('tbody')
        if not tbody:
            logging.error("Tbody non trovato nella tabella.")
            return

        rows: list[list[str]] = []
        for row in tbody.find_all('tr'):
            cells = row.find_all('td')
            row_data = [cell.text.strip() for cell in cells]
            rows.append(row_data)

        if not rows:
            logging.warning("Tabella vuota: nessuna riga trovata.")
            return

        pattern = r"(\d+)\r*\n\((\d+)\s.*\)" 
        for row in rows:
            # {id_anagrafica}\n({id_agenda} Dom 2026 May 09 19:45)
            if len(row) <= 1:
                continue
            if 'Aperta' not in row[1]:
                continue

            match_ = re.search(pattern, row[0])
            if match_:
                id_anagrafica, id_gig_agenda = match_.groups()
                return Agenda(id_anagrafica.strip(), id_gig_agenda.strip())

        logging.error("Nessuna agenda aperta valida trovata tra le righe elaborate.")
        return

class Utenze:

    USER_TABLE_NAME: str = 'tabella_ricerca_utenti'

    # user_id;username;ruolo
    CSV_UTENZE: Path = UTENZE_DIR / f'{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}_user_id.csv'

    def __init__(self, html: str) -> None:
        self.html: str = html
        self.data: list[User] = []

    def parse_response_utenze(self) -> list[User]:
        """Converte il corpo della risposta HTTP in una lista di dizionari"""

        # Parsing del contenuto HTML con BeautifulSoup
        soup = BeautifulSoup(self.html, 'html.parser')

        # Trova la tabella con l'id specificato
        table = soup.find('table', {'id': self.USER_TABLE_NAME})
        if table is None:
            raise ValueError(f"Nessuna tabella con id '{self.USER_TABLE_NAME}' trovata.")

        # Trova tutte le righe della tabella (escludendo l'header)
        rows = table.find_all('tr')

        data: list[User] = []
        for row in rows:

            # Trova tutte le celle della riga
            cells = row.find_all('td')
            if len(cells) < 3:
                continue

            # Trova l'immagine nella prima cella
            # link (per user edit) nella seconda
            # e il ruolo nella quarta
            img = cells[0].find('img')
            link = cells[1].find('a')
            ruolo = cells[3].text.strip()

            if not (img and link):
                continue

            # Estrai e pulisci i dati
            img_src: str = str(img.get('src', ''))
            href = link.get('href', '')
            user_id: int = int(str(href).split('/')[-1])
            username: str = link.text.strip()

            # Le utenze attive devono avere icona verde
            if 'bull_green' not in str(img_src):
                continue

            data.append(
                User(
                    user_id=user_id,
                    username=username,
                    ruolo=ruolo
                )
            )

        return data

    def to_csv(self) -> None:
        """Scrivi i dati in CSV"""
        if not self.data:
            logging.warning("Nessun dato da salvare in CSV per Utenze.")
            return

        with open(self.CSV_UTENZE, 'w', encoding='utf-8', newline='') as csvfile:
            fieldnames = [f.name for f in fields(self.data[0])]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')

            writer.writeheader()
            for item in self.data:
                writer.writerow(asdict(item))

    def to_json(self) -> None:
        """Scrivi i dati in JSON"""
        with open(self.CSV_UTENZE.with_suffix('.json'), 'w', encoding='utf-8') as jsonfile:
            json.dump(
                [asdict(item) for item in self.data],
                jsonfile,
                ensure_ascii=False,
                indent=4
            )

class Lavorazioni:

    TBL_NAME: str = 'tabella_lavorazione_consulenti'

    def __init__(self, login_id: str) -> None:
        self.data: list[dict[str, str]] = []

        timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        self.output_file: Path = LAVORAZIONI_DIR / f"{timestamp}_{login_id}.csv"

    @staticmethod
    def parse_lavorazioni_html(html_content: str) -> list[dict[str, str]]:

        soup = BeautifulSoup(html_content, 'html.parser')

        # Cerca la tabella specifica
        table = soup.find('table', id=Lavorazioni.TBL_NAME)
        if not table:
            raise ValueError(f"Tabella {Lavorazioni.TBL_NAME} non trovata nell'HTML fornito.")

        thead = table.find('thead')
        if not thead:
            raise ValueError("Tag <thead> non trovato nella tabella.")

        headers: list[str] = [th.get_text(strip=True) for th in thead.find_all('th')]

        parsed_data: list[dict[str, str]] = []
        tbody = table.find('tbody')

        if tbody:
            rows = tbody.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                # Assicurati che il numero di celle corrisponda al numero di colonne
                if len(cells) == len(headers):
                    row_dict = {
                        headers[i]: cells[i].get_text(strip=True) 
                        for i in range(len(headers))
                    }
                    parsed_data.append(row_dict)

        return parsed_data

    def to_csv(self) -> None:
        if not self.data:
            logging.warning("Nessun dato fornito per il salvataggio in CSV.")
            return

        # Prende le intestazioni dalle chiavi del primo dizionario
        fieldnames = list(self.data[0].keys())

        try:
            with open(self.output_file, mode='w', newline='', encoding='utf-8') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=';')

                writer.writeheader()
                writer.writerows(self.data)

            # logging.info(f"Dati salvati con successo in: {self.output_file}")
        except Exception as e:
            logging.error(f"Errore durante il salvataggio del CSV: {e}")

class KiwiTable:

    HEADERS: dict[str, list[str]] = {
        'Milano': ['Consulente Milano', 'Nuove Anagrafiche', 'Primo reminder', 'Ultimo reminder', 'Totale aperte', 'Stato "Nuova Anagrafica"', 'Riceve Anagrafiche'],
        'Tirana': ['Consulente Tirana', 'Nuove Anagrafiche', 'Primo reminder', 'Ultimo reminder', 'Totale aperte (*)', 'Stato "Nuova Anagrafica"', 'Riceve Anagrafiche'],
    }

    def __init__(self, html: str) -> None:
        self.html: str = html
        self.html_directory: Path = HomeKiwiOutput.HTML_DIR.value
        self.csv_directory: Path = HomeKiwiOutput.CSV_DIR.value
        self.json_directory: Path = HomeKiwiOutput.JSON_DIR.value

        self.timestamp: str = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    def is_valid_dashboard_table(self, table: Tag) -> list[str]:
        t_head = table.find('thead')
        if t_head is None:
            return []

        table_headers = [th.get_text(strip=True) for th in t_head.find_all('th')]
        if table_headers not in self.HEADERS.values():
            return []
        return table_headers

    def fetch_all_tables(self) -> ResultSet[Tag]:
        # Salva le tabelle identificate nei file CSV e JSON
        soup = BeautifulSoup(self.html, 'html.parser')

        central_content_div: Optional[Tag] = soup.find('div', id='GG_central-content')
        if central_content_div is None:
            raise ValueError("Div 'GG_central-content' non trovato nella risposta HTML.")

        tables: ResultSet[Tag] = central_content_div.find_all('table', class_='GG_standard_table')

        return tables

    def to_html(self) -> None:
        """ Salva risposta HTML in un file con timestamp """

        self.html_directory.mkdir(parents=True, exist_ok=True)
        file_path = self.html_directory / f"HomeKiwi_{self.timestamp}.html"

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(self.html)
        logging.debug(f"[HTML] Risposta salvata in {file_path}")

    def to_csv(self, table: Tag, headers: list[str]):
        """ Salva i dati della tabella in un file CSV """

        self.csv_directory.mkdir(parents=True, exist_ok=True)
        file_path = self.csv_directory / f"{self.timestamp}_{headers[0]}.csv"

        data = self._fetch_table(table, headers, 'csv')

        with open(file_path, "w", newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            for row in data:
                writer.writerow(row)
        logging.debug(f"[CSV] Risposta salvata in {file_path}")

    def to_json(self, table: Tag, headers: list[str]):
        """ Salva i dati della tabella in un file JSON """
        self.json_directory.mkdir(parents=True, exist_ok=True)
        file_path = self.json_directory / f"{self.timestamp}_{headers[0]}.json"

        data = self._fetch_table(table, headers, 'json')

        json_data: dict[str, Any] = {
            'timestamp': self.timestamp,
            'headers': headers,
            'data': data
        }

        with open(file_path, "w", encoding="utf-8") as jsonfile:
            json.dump(json_data, jsonfile, indent=4, ensure_ascii=False)
        logging.debug(f"[JSON] Risposta salvata in {file_path}")

    @staticmethod
    def _fetch_table(table: Tag, headers: list[str], format: Literal['csv', 'json']) -> list[list[str] | dict[str, str]]:

        data: list[list[str] | dict[str, str]] = []
        tbodies = table.find_all('tbody')
        for tbody in tbodies:
            rows = tbody.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) != len(headers):
                    continue
                if format == 'json':
                    row_data = {headers[i]: cell.get_text(strip=True) for i, cell in enumerate(cells)}
                elif format == 'csv':
                    row_data = [cell.get_text(strip=True) for cell in cells]
                data.append(row_data)

        return data
