"""
Questo file contiene le definizioni dei tipi di dato (Dataclasses e NamedTuples)
utilizzati per mappare le entità di Kiwi, come Agende, Utenti,
Riassegnazioni e Retrocessioni.
"""

from dataclasses import asdict, dataclass
from datetime import datetime

@dataclass
class Estrazione:
    nome_estrazione: str
    indice: int
    start_date: datetime
    end_date: datetime

    def as_str(self) -> str:
        return '_'.join((
            self.nome_estrazione,
            str(self.indice),
            self.start_date.strftime('%Y-%m-%d'),
            self.end_date.strftime('%Y-%m-%d')
        ))

@dataclass
class Params:
    consulente_id: str
    assegnatario_id: str
    cellulare: str

@dataclass
class SearchForm:
    ricerca_telefono: str
    ricerca_id_anagrafica: str = ''
    ricerca_nome: str = ''
    ricerca_cognome: str = ''
    ricerca_email: str = ''
    ricerca_codice_fiscale: str = ''
    ricerca_anagrafica: str = 'Ricerca'

    def as_dict(self) -> dict[str, str]:
        return asdict(self)

@dataclass
class Agenda:
    anagrafica: str
    agenda: str

@dataclass
class Retrocessione:
    cellulare: str
    id_esito: str

    def as_dict(self, agenda: Agenda) -> dict[str, str]:
        return {
            'operation':    'modifica_stato',
            'idAnagrafica': agenda.anagrafica,
            'idGigAgenda':  agenda.agenda,
            'idEsito':      self.id_esito,
            'pulsStato':    'Modifica'
        }

@dataclass
class Riassegnazione:
    consulente_id: str
    assegnatario_id: str
    anagrafica: str
    agenda: str

    def as_dict(self) -> dict[str, str]:
        return {
            'operation': 'assegna',
            'tipo_pratica': 'aperte',
            'stato_agenda': '1',
            'lavorata': '',
            'quantita': '',
            'consulente': self.consulente_id,
            'assegnatario': self.assegnatario_id,
            'pulsAssegna': 'Assegna',
            'anagrafica[]': f'{self.anagrafica}_{self.agenda}'
        }

@dataclass
class User:
    user_id: int
    username: str
    ruolo: str

    def __str__(self) -> str:
        return (
            f"<user_id={self.user_id}, "
            f"username={self.username}, "
            f"ruolo={self.ruolo}>"
        )
