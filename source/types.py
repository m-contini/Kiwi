"""
Questo file contiene le definizioni dei tipi di dato (Dataclasses e NamedTuples)
utilizzati per mappare le entità di Kiwi, come Agende, Utenti,
Riassegnazioni e Retrocessioni.
"""

from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Final, TypeAlias, TypedDict

if TYPE_CHECKING:
    from datetime import datetime

PayloadDict: TypeAlias = dict[str, str]

class RetrocessionePayload(TypedDict):
    """Definizione del payload per l'operazione di retrocessione."""
    operation: str
    idAnagrafica: str
    idGigAgenda: str
    idEsito: str
    pulsStato: str

class RiassegnazionePayload(TypedDict):
    """Definizione del payload per l'operazione di riassegnazione."""
    operation: str
    tipo_pratica: str
    stato_agenda: str
    lavorata: str
    quantita: str
    consulente: str
    assegnatario: str
    pulsAssegna: str
    anagrafica_list: str  # Questo rimane per stuttura generale, ma useremo un altro valore per la chiave sottostante

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
    ricerca_anagrafica: Final[str] = 'Ricerca'

    def as_dict(self) -> PayloadDict:
        return asdict(self)

@dataclass
class Agenda:
    anagrafica: str
    agenda: str

@dataclass
class Retrocessione:
    cellulare: str
    id_esito: str

    def as_dict(self, agenda: Agenda) -> RetrocessionePayload:
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

    def as_dict(self) -> RiassegnazionePayload:
        return {
            'operation': 'assegna',
            'tipo_pratica': 'aperte',
            'stato_agenda': '1',
            'lavorata': '',
            'quantita': '',
            'consulente': self.consulente_id,
            'assegnatario': self.assegnatario_id,
            'pulsAssegna': 'Assegna',
            'anagrafica_list': f'{self.anagrafica}_{self.agenda}'
        }  # type: ignore

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
