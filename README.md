# Kiwi

- [Kiwi](#kiwi)
  - [Utilizzi](#utilizzi)
  - [Routines](#routines)
    - [1. Pulizia](#1-pulizia)
    - [2. Estrazione Utenze](#2-estrazione-utenze)
    - [3. Dashboard (Scraping)](#3-dashboard-scraping)
    - [4. Lavorazioni Consulente](#4-lavorazioni-consulente)
    - [5. Riassegnazioni](#5-riassegnazioni)
    - [6. Estrazioni (WIP)](#6-estrazioni-wip)
  - [Esempio di Output da terminale](#esempio-di-output-da-terminale)
    - [Scheduled Tasks](#scheduled-tasks)
      - [Output](#output)
    - [EstrazioniDownload \[WIP\]](#estrazionidownload-wip)
  - [Emulazione per test](#emulazione-per-test)
  - [Setup](#setup)
  - [Proprietà e Termini d'Uso](#proprietà-e-termini-duso)

Questo sistema automatizza le operazioni ripetitive su Kiwi che prima richiedevano ore di lavoro manuale:

- **Monitoraggio Consulenti**: Legge automaticamente la Dashboard di Kiwi per vedere chi ha troppe pratiche aperte e prevenire sovraccarichi.  
- **Gestione Turni (Riassegnazioni)**: Sposta le pratiche da un consulente all'altro leggendo un semplice file Excel di istruzioni, oppure le retrocede a uno stato precedente.  
- **Controllo Anomalie**: Verifica che solo le persone autorizzate ricevano agende, segnalando eventuali errori di sistema.
- **Report Performance**: Scarica i dati storici delle lavorazioni dei consulenti per le analisi quotidiane, settimanali o mensili.  
- **Download Massivi**: Permette di scaricare grandi quantità di dati dividendo il lavoro in "pezzi" più piccoli per non abbattere il server.

## Utilizzi

Questa collezione di scripts interagisce col gestionale **Kiwi** tramite *routine* automatiche:

```bash
python ScheduledTasks.py
```

o tramite estrazione interattiva di dati dal DB (solo manuale):

```bash
python DownloadEstrazioni.py
```

Alcune *automazioni* sono riproducibili anche offline leggendo dai dati di prova di questo repository.

Il codice sorgente di ciascuna *automazione* è contenuto nella cartella [routines](./routines/)

Utilizzi:

- **temporizzato** con Task Scheduler su Windows;
- **manuale** da riga di comando.

Funzioni di *automazione* (**routines**):

- Estrazione delle utenze attive (*Operations* + *Business*) nel gestionale per monitorare un occasionale bug di sistema per cui le utenze non *Operations* ricevevano agende da lavorare;
- Scraping in tempo reale della dashboard della home page, contenente tutte le agende (aperte e chiuse) di ogni consulente censito a sistema;
- Estrazione delle lavorazioni effettuate da un dato consulente in un dato intervallo temporale, per monitorarne le performance;
- Automazioni nel riassegnare pratiche da un consulente all'altro (es. per cambio turno) e nel retrocedere pratiche, usando per entrambi i casi il cellulare come chiave di ricerca.
- **\[Beta\]**: download di una o più estrazioni, leggendo i requisiti da un CSV che, se inesistente, viene creato a runtime.

## Routines

Le *routine* sono moduli specializzati in automazione, definiti nella cartella [routines](/routines/).  
Di seguito il dettaglio tecnico delle operazioni che esse eseguono.

### 1. Pulizia

Identifica e rimuove file temporanei che non sono più necessari

- **Codice**: [DailyClear.py](./routines/DailyClear.py)
- **Alias**: `pulizia_quotidiana_file_obsoleti`

### 2. Estrazione Utenze

Estrazione delle utenze attive (*Operations* + *Business*) nel gestionale per monitorare un occasionale bug di sistema per cui le utenze non *Operations* ricevevano agende da lavorare.

- **Codice**: [EstraiUtenze.py](./routines/EstraiUtenze.py)
- **Alias**: `estrai_utenze_attive`

### 3. Dashboard (Scraping)

Scraping in tempo reale della dashboard della home page di Kiwi, contenente tutte le agende (aperte e chiuse) di ogni consulente censito a sistema.
Lo scopo è di monitorare se alcuni consulenti sono eccessivamente carichi di nuove anagrafiche e determinarne evenualmente la [redistribuzione automatica](#5-riassegnazioni).

- **Codice**: [KiwiFetch.py](./routines/KiwiFetch.py)
- **Alias**: `main_dashboard_fetch`

### 4. Lavorazioni Consulente

Estrazione delle lavorazioni effettuate da un dato consulente in un dato intervallo temporale, per monitorarne le performance.

- **Codice**: [LavorazioniConsulenti.py](./routines/LavorazioniConsulenti.py)
- **Alias**: `lavorazioni_consulenti`

Work in Progress: prendere in input una lista di consulenti

### 5. Riassegnazioni

Automazioni nel riassegnare pratiche da un consulente all'altro (es. per cambio turno) e/o nel retrocederle, usando per entrambi i casi il cellulare come chiave di ricerca.
La lista di agende da riassegnare/retrocedere viene letta da 2 distinti CSV, compilati a mano su Excel dal team.

- **Codice**: [Riassegnazioni.py](./routines/Riassegnazioni.py)
- **Alias**: `riassegnazioni_retrocessioni`

### 6. Estrazioni (WIP)

Download automatico di una o più estrazioni programmate, i cui parametri di estrazione vengono letti da CSV creato interattivamente in [multiplePayloadGenerator.py](./Estrazioni/_multiplePayloadGenerator.py).

- **Codice**: [DownloadEstrazioni.py](./DownloadEstrazioni.py)
- **Alias**: `download_estrazioni`

## Esempio di Output da terminale

Ecco come appare l'output da terminale (nel caso in cui gli script siano lanciati manualmente anziché come routine schedulate)

### Scheduled Tasks

```bash
python ScheduledTasks.py
```

#### Output

```plain
Rimozione 2026_05_10_19_14_22_Consulente Milano.csv...
Rimozione 2026_05_10_19_14_22_Consulente Tirana.csv...
Rimozione 2026_05_11_08_12_45_Consulente Milano.csv...
Rimozione 2026_05_11_08_12_45_Consulente Tirana.csv...
Rimozione 2026_05_11_08_17_03_Consulente Milano.csv...
Rimozione 2026_05_11_08_17_03_Consulente Tirana.csv...
Rimozione 2026_05_11_08_19_19_Consulente Milano.csv...
Rimozione 2026_05_11_08_19_19_Consulente Tirana.csv...
Rimozione HomeKiwi_2026_05_10_19_14_22.html...
Rimozione HomeKiwi_2026_05_11_08_12_45.html...
Rimozione HomeKiwi_2026_05_11_08_17_03.html...
Rimozione HomeKiwi_2026_05_11_08_19_19.html...
Rimozione 2026_05_10_19_14_22_Consulente Milano.json...
Rimozione 2026_05_10_19_14_22_Consulente Tirana.json...
Rimozione 2026_05_11_08_12_45_Consulente Milano.json...
Rimozione 2026_05_11_08_12_45_Consulente Tirana.json...
Rimozione 2026_05_11_08_17_03_Consulente Milano.json...
Rimozione 2026_05_11_08_17_03_Consulente Tirana.json...
Rimozione 2026_05_11_08_19_19_Consulente Milano.json...
Rimozione 2026_05_11_08_19_19_Consulente Tirana.json...
----------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------
Username: 'mcontini'
Password: '**********'

Pagina finale raggiunta: https://kiwi.facile.it/mutui/admin
Login riuscito senza reindirizzamenti.

<user_id=20625, username=Al*******ne, ruolo=Finance - Administrator>
<user_id=19957, username=Ar************ta, ruolo=Finance - Administrator>
[...]
<user_id=19257, username=To*************lo, ruolo=Mutui - Team leader>
<user_id=18889, username=Va**************io, ruolo=Mutui - Team leader>

Dati scritti nel file 'C:\Users\mcontini\Postman-main\Utenze\user_id.csv'.
Dati scritti nel file 'C:\Users\mcontini\Postman-main\Utenze\user_id.json'.
----------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------
Username: 'mcontini'
Password: '**********'

Pagina finale raggiunta: https://kiwi.facile.it/mutui/admin
Login riuscito senza reindirizzamenti.

[HTML] Risposta salvata in C:\Users\mcontini\Postman-main\HomeKiwi\htmlTbls\HomeKiwi_2026_05_11_08_20_33.html

[CSV] Risposta salvata in C:\Users\mcontini\Postman-main\HomeKiwi\csvTbls\2026_05_11_08_20_33_Consulente Milano.csv
[JSON] Risposta salvata in C:\Users\mcontini\Postman-main\HomeKiwi\jsonTbls\2026_05_11_08_20_33_Consulente Milano.json

[CSV] Risposta salvata in C:\Users\mcontini\Postman-main\HomeKiwi\csvTbls\2026_05_11_08_20_33_Consulente Tirana.csv
[JSON] Risposta salvata in C:\Users\mcontini\Postman-main\HomeKiwi\jsonTbls\2026_05_11_08_20_33_Consulente Tirana.json

Operazione completata. I file sono stati salvati nelle sottocartelle di ./HomeKiwi
----------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------
Username: 'mcontini'
Password: '**********'

Pagina finale raggiunta: https://kiwi.facile.it/mutui/admin
Login riuscito senza reindirizzamenti.

    ==================================================
    Dettagli della richiesta:
            URL: https://kiwi.facile.it/mutui/admin/visualizza/lavorazioneConsulenti
            Metodo: POST
            Headers: {'content-type': 'application/x-www-form-urlencoded'}
            Dati inviati: {'login_operatore': '14091', 'data_from': '2024-06-28', 'data_to': '', 'esporta': 'Esporta in Excel'}

    ==================================================
    Dettagli della risposta:
            Status code: 200
            Headers: {'content-type': 'application/vnd.ms-excel'}
            Lunghezza del contenuto: 1611

Contenuto risposta:
{'Id consulente': '14091', 'Nome consulente': 'Ma*******si', 'Id agenda': '8541002', 'Orario lavorazione': '2024-06-28 09:15:33'}
{'Id consulente': '14091', 'Nome consulente': 'Ma*******si', 'Id agenda': '8541015', 'Orario lavorazione': '2024-06-28 10:42:11'}
[...]
{'Id consulente': '14091', 'Nome consulente': 'Ma*******si', 'Id agenda': '8541129', 'Orario lavorazione': '2024-06-28 16:22:10'}
Dati salvati con successo in: ./Lavorazioni/2026_05_11_08_20_33_14091.csv
----------------------------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------------------------
Username: 'mcontini'
Password: '**********'

Pagina finale raggiunta: https://kiwi.facile.it/mutui/admin
Login riuscito senza reindirizzamenti.

====================
RIASSEGNAZIONI
====================
{'consulente_id': '14056', 'assegnatario_id': '80667', 'cellulare': '32************1'}
[...]
{'consulente_id': '80667', 'assegnatario_id': '21364', 'cellulare': '34************6'}
{'consulente_id': '80696', 'assegnatario_id': '80617', 'cellulare': '33************2'}

Riassegnazione da 14056 a 80667 per agenda 999456 completata!
Riassegnazione da 14286 a 80705 per agenda 999456 completata!
Riassegnazione da 10103 a 10109 per agenda 999456 completata!
Riassegnazione da 14286 a 80705 per agenda 999456 completata!
Riassegnazione da 80626 a 80697 per agenda 999456 completata!
Riassegnazione da 80667 a 21364 per agenda 999456 completata!
Riassegnazione da 80696 a 80617 per agenda 999456 completata!

====================
RETROCESSIONI
====================
Retrocessione Anagrafica(Agenda) -> 555123(999456)
Retrocessione in stato 2 per agenda 999456 completata!

Retrocessione Anagrafica(Agenda) -> 555123(999456)
Retrocessione in stato 2 per agenda 999456 completata!

Retrocessione Anagrafica(Agenda) -> 555123(999456)
Retrocessione in stato 3 per agenda 999456 completata!

Retrocessione Anagrafica(Agenda) -> 555123(999456)
Retrocessione in stato 2 per agenda 999456 completata!
```

### EstrazioniDownload [WIP]

Nota: in modalità Offline questo script può solo mostrare output, fallendo per ovvi motivi nella generazione dati (indisponibilità del server).  

```bash
python EstrazioniDownload.py
```

```plain
Username: 'mcontini'
Password: '**********'

Pagina finale raggiunta: https://kiwi.facile.it/mutui/admin
Login riuscito senza reindirizzamenti.

Recupero elenco estrazioni disponibili a sistema...
Dati salvati in ./Estrazioni/options.csv
Dati salvati in ./Estrazioni/options_decoded.json

Costruzione lista di payload per estrarre dati da database...

Scegli una o più opzioni (separate da virgola):
1. AgendeChiuse
2. AgendeClientiRitorno
3. AgendeConPassaggioDiStato
[...]
1.  TotaleInviiConDettaglio
2.  TransazioniGoogleAnalytics
3.  ValidazioniAnagraficheFido
4.  VerificheCondizioniSalvataggioAgende

Inserisci i numeri delle opzioni scelte (separati da virgola): 10, 20, 27

Generazione payload per: AssegnazioniConsulentiTiranaConFiltroSuAgenda

Inserisci il valore per data_inizio (premer Enter per utilizzare il valore di default: ''): 01/01/2026

Inserisci il valore per data_fine (premer Enter per utilizzare il valore di default: ''):

Seleziona un valore per consulente:
1. -- SELEZIONARE -- ()
2. A********* C***** (80740)
3. A********* T*** V******** D*** C** R********* (7518)
4. A********* T*** V******** D*** S**** R********* (7519)

Inserisci il numero dell'opzione scelta: 3

Generazione payload per: Erogazioni
Inserisci il valore per data_inizio (premer Enter per utilizzare il valore di default: ''): 10/05/2026
Inserisci il valore per data_fine (premer Enter per utilizzare il valore di default: ''): 11/05/2026

Generazione payload per: LavorazioniGDO
Inserisci il valore per data_inizio (premer Enter per utilizzare il valore di default: '17/06/2024'):
Inserisci il valore per data_fine (premer Enter per utilizzare il valore di default: '25/06/2024'):

Seleziona un valore per consulente:
1. -- SELEZIONARE -- ()
2. C***** A******** (80740)
3. T*** V******* D*** C** R******** A********* (7518)
4. P***** B*******( (14127)

Inserisci il numero dell'opzione scelta: 2
Payload codificati salvati in ./Estrazioni/PayloadForDownload.csv

Riga 1 - payload (decoded):
{
  "estrazione": "AssegnazioniConsulentiTiranaConFiltroSuAgenda",
  "data_inizio": "01/01/2026",
  "data_fine": "",
  "consulente": "7518"
}

Inserisci la larghezza in giorni dei singoli intervalli di date (tra 1 e 20): 5

Riga 2 - payload (decoded):
{
  "estrazione": "Erogazioni",
  "data_inizio": "10/05/2026",
  "data_fine": "11/05/2026"
}

Inserisci la larghezza in giorni dei singoli intervalli di date (tra 1 e 20): 4

Riga 3 - payload (decoded):
{
  "estrazione": "LavorazioniGDO",
  "data_inizio": "17/06/2024",
  "data_fine": "25/06/2024",
  "consulente": "80740"
}

Inserisci la larghezza in giorni dei singoli intervalli di date (tra 1 e 20): 10
Il range di date verrà suddiviso in intervalli da 10 giorni.

Inserire percorso per download: ./Output

Procedere con il download dei file CSV? (y/n): n
Download annullato.
```

## Emulazione per test

Di default è attivo un flag globale `__TEST__`:
    - **`__TEST__ = True`**: Modalità dimostrativa. Le *routine* operano offline leggendo dati da file HTML locali.
    - **`__TEST__ = False`**: Modalità online. Le *routine* interagiscono con Kiwi.

*Assicurarsi di aver configurato il flag `__TEST__ = False` all'interno di `ScheduledTasks.py` se si è realmente connessi a Kiwi.*

## Setup

```bash
python -m pip install -r requirements.txt
```

## Proprietà e Termini d'Uso

Il codice viene fornito as-is, a scopo puramente illustrativo delle competenze tecniche e delle logiche di automazione implementate. L'autore non si assume alcuna responsabilità per tentativi di esecuzione impropria o per l'uso del codice al di fuori del contesto operativo autorizzato.

Di default è attivo il flag `__TEST__ = True` (modificabile in [ScheduledTasks.py](./ScheduledTasks.py)) per imitare offline le pagine web principali di **Kiwi**.
