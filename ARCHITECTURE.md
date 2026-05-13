# Architettura

## 1️⃣ Runtime Architecture

```mermaid
graph LR

    %% =========================
    %% STYLES
    %% =========================
    classDef entryPoint fill:#4A90E2,stroke:#2E5C8A,stroke-width:3px,color:#fff
    classDef core fill:#50C878,stroke:#2E7D4E,stroke-width:2px,color:#fff
    classDef routine fill:#FFB84D,stroke:#CC8A3D,stroke-width:2px,color:#000
    classDef output fill:#9B59B6,stroke:#6C3483,stroke-width:2px,color:#fff

    %% =========================
    %% ENTRY POINT
    %% =========================
    ST[🕐 ScheduledTasks.py<br/><i>Orchestrazione automazioni</i>]:::entryPoint

    %% =========================
    %% ROUTINES
    %% =========================
    subgraph ROUTINES["⚙️ Automated Routines"]
        direction TB

        RI[Riassegnazioni.py<br/><i>Riassegnazione agende</i>]:::routine
        RE[Retrocessioni.py<br/><i>Retrocessione stati</i>]:::routine
        EU[EstraiUtenze.py<br/><i>Monitoraggio utenze</i>]:::routine
        KF[KiwiFetch.py<br/><i>Dashboard scraping</i>]:::routine
        LC[LavorazioniConsulenti.py<br/><i>Report performance</i>]:::routine
        DC[DailyClear.py<br/><i>Pulizia file obsoleti</i>]:::routine
    end

    %% =========================
    %% CORE
    %% =========================
    subgraph CORE["💎 Core Services"]
        direction TB

        KW[kiwi.py<br/><i>Interazione con Kiwi</i>]:::core
        TY[types.py<br/><i>Strutture dati</i>]:::core
        EX[exceptions.py<br/><i>Gestione errori</i>]:::core
    end

    %% =========================
    %% OUTPUTS
    %% =========================
    subgraph OUTPUTS["📄 Generated Outputs"]
        direction TB

        UCSV[Utenze CSV]:::output
        DCSVJSONHTML[Dashboard HTML/CSV/JSON]:::output
        XLS[Excel Reports]:::output
    end

    %% =========================
    %% ORCHESTRATION
    %% =========================
    ST --> DC
    ST --> EU
    ST --> LC
    ST --> KF
    ST --> RI
    ST --> RE

    %% =========================
    %% CORE USAGE
    %% =========================
    EU -. usa .-> KW
    LC -. usa .-> KW
    KF -. usa .-> KW
    RI -. usa .-> KW
    RE -. usa .-> KW

    EU -. usa .-> TY
    LC -. usa .-> TY
    RI -. usa .-> TY
    RE -. usa .-> TY

    KW -. solleva .-> EX

    %% =========================
    %% OUTPUTS
    %% =========================
    EU --> UCSV

    LC --> XLS

    KF --> DCSVJSONHTML

    RI -. legge .-> UCSV
```

---

## 2️⃣ Extraction Workflow

```mermaid
graph TB

    %% =========================
    %% STYLES
    %% =========================
    classDef entryPoint fill:#4A90E2,stroke:#2E5C8A,stroke-width:3px,color:#fff
    classDef extraction fill:#E85D75,stroke:#B94A5E,stroke-width:2px,color:#fff
    classDef core fill:#50C878,stroke:#2E7D4E,stroke-width:2px,color:#fff
    classDef output fill:#9B59B6,stroke:#6C3483,stroke-width:2px,color:#fff

    %% =========================
    %% ENTRY POINT
    %% =========================
    DE[📥 DownloadEstrazioni.py<br/><i>Interfaccia estrazioni on-demand</i>]:::entryPoint

    %% =========================
    %% EXTRACTION LOGIC
    %% =========================
    subgraph EXTRACTIONS["📊 Extraction Management"]
        direction TB

        OM[_estrazioniDisponibiliDownload.py<br/><i>Recupera estrazioni disponibili</i>]:::extraction

        PM[_multiplePayloadGenerator.py<br/><i>Genera payload interattivo</i>]:::extraction
    end

    %% =========================
    %% CORE
    %% =========================
    subgraph CORE["💎 Core Services"]
        direction TB

        KW[kiwi.py<br/><i>Interazione con Kiwi</i>]:::core
        TY[types.py<br/><i>Strutture dati</i>]:::core
    end

    %% =========================
    %% OUTPUTS
    %% =========================
    subgraph OUTPUTS["📄 Generated Outputs"]
        direction TB

        CSVJSON[CSV/JSON]:::output
        XLS[Excel Export]:::output
    end

    %% =========================
    %% MAIN FLOW
    %% =========================
    DE -->|1. recupera opzioni| OM

    DE -->|2. genera payload| PM

    PM -.->|legge options.json| OM

    %% =========================
    %% CORE USAGE
    %% =========================
    DE -. usa .-> KW

    PM -. usa .-> TY

    %% =========================
    %% OUTPUTS
    %% =========================
    OM --> CSVJSON

    DE --> XLS
```

---

## 🧪 Modalità TEST

> Quando attivata tramite flag `--test`:
>
> * `kiwi.py` non effettua connessioni reali
> * vengono utilizzati snapshot HTML locali
> * tutte le routine operano offline
> * utile per sviluppo e debugging

---

## 📖 Legenda

| Elemento         | Significato                                            |
| ---------------- | ------------------------------------------------------ |
| 🔵 **Azzurro**   | **Entry Points** - Punti di ingresso dell'applicazione |
| 🟢 **Verde**     | **Core Services** - Moduli fondamentali condivisi      |
| 🟠 **Arancione** | **Automated Routines** - Automazioni schedulabili      |
| 🔴 **Rosa**      | **Extraction Management** - Gestione estrazioni dati   |
| 🟣 **Viola**     | **Generated Outputs** - File generati dal sistema      |
| ───              | **Linea solida** - Flusso principale                   |
| ╌╌╌              | **Linea tratteggiata** - Dipendenza / utilizzo         |

---

## 🔑 Note Architetturali

* `kiwi.py` rappresenta il cuore del sistema: tutte le routine che interagiscono con il gestionale passano attraverso questo modulo
* `ScheduledTasks.py` orchestra l'esecuzione sequenziale delle routine automatiche
* `DownloadEstrazioni.py` fornisce un'interfaccia guidata per estrazioni personalizzate
* `Riassegnazioni.py` legge istruzioni operative da file CSV compilati manualmente
* La modalità `__TEST__` consente di eseguire l'intero sistema offline utilizzando snapshot locali
