# Kiwi Automation Suite

[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **Automazione per l'ottimizzazione dei flussi di Business Intelligence e Workflow Management.**

Per una panoramica funzionale in lingua italiana, dedicata a stakeholder non tecnici, consultare **[Overview Business](./OVERVIEW_BUSINESS.md)**.

Per il diagramma completo dell'architettura, consultare **[Architecture](./ARCHITECTURE.md)**.

---

## Business Value & Impact

Questo sistema automatizza le operazioni ripetitive su Kiwi che prima richiedevano ore di lavoro manuale:

- **Monitoraggio Consulenti**: Legge automaticamente la Dashboard di Kiwi per vedere chi ha troppe pratiche aperte e prevenire sovraccarichi.  
- **Gestione Turni (Riassegnazioni)**: Sposta le pratiche da un consulente all'altro leggendo un semplice file Excel di istruzioni, oppure le retrocede a uno stato precedente.  
- **Controllo Anomalie**: Verifica che solo le persone autorizzate ricevano agende, segnalando eventuali errori di sistema.
- **Report Performance**: Scarica i dati storici delle lavorazioni dei consulenti per le analisi quotidiane, settimanali o mensili.  
- **Download Massivi**: Permette di scaricare grandi quantità di dati dividendo il lavoro in "pezzi" più piccoli per non abbattere il server.

## Indice

- [Kiwi Automation Suite](#kiwi-automation-suite)
  - [Business Value \& Impact](#business-value--impact)
  - [Indice](#indice)
    - [Utilizzi](#utilizzi)
    - [Funzioni di *automazione* (**routines**)](#funzioni-di-automazione-routines)
  - [Routines](#routines)
    - [1. Pulizia](#1-pulizia)
    - [2. Estrazione Utenze](#2-estrazione-utenze)
    - [3. Dashboard (Scraping)](#3-dashboard-scraping)
    - [4. Lavorazioni Consulente](#4-lavorazioni-consulente)
    - [5. Riassegnazioni](#5-riassegnazioni)
    - [6. Estrazioni](#6-estrazioni)
  - [Esempio di utilizzo](#esempio-di-utilizzo)
    - [ScheduledTasks](#scheduledtasks)
    - [DownloadEstrazioni](#downloadestrazioni)
  - [Emulazione per test](#emulazione-per-test)
  - [Setup](#setup)
  - [Proprietà e Termini d'Uso](#proprietà-e-termini-duso)

Questa **collezione** di scripts interagisce col gestionale **Kiwi** tramite *routine* automatiche:

```bash
python ScheduledTasks.py
```

o tramite estrazione interattiva di dati dal DB (solo manuale):

```bash
python DownloadEstrazioni.py
```

Alcune *automazioni* sono riproducibili anche offline leggendo dai dati di prova di questo repository.

Il codice sorgente di ciascuna *automazione* è contenuto nella cartella [routines](./routines/)

### Utilizzi

- **temporizzato** con Task Scheduler su Windows;
- **manuale** da riga di comando.

### Funzioni di *automazione* (**routines**)

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

### 6. Estrazioni

Download automatico di una o più estrazioni programmate, i cui parametri di estrazione vengono letti da CSV creato interattivamente in [multiplePayloadGenerator.py](./Estrazioni/_multiplePayloadGenerator.py).

- **Codice**: [DownloadEstrazioni.py](./DownloadEstrazioni.py)
- **Alias**: `download_estrazioni`

## Esempio di utilizzo

Ecco come appare l'output da terminale (nel caso in cui gli script siano lanciati manualmente anziché come routine schedulate)

### [ScheduledTasks](./ScheduledTasks.py)

```bash
python ScheduledTasks.py
```

```plain
[WIP]
```

### [DownloadEstrazioni](./DownloadEstrazioni.py)

Nota: in modalità Offline questo script può solo mostrare output, fallendo per ovvi motivi nella generazione dati (indisponibilità del server).  

```bash
python DownloadEstrazioni.py
```

```plain
[WIP]
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
