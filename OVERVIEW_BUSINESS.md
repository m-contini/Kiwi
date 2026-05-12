# Suite di interrogazione di "Kiwi"

Questo repository contiene una collezione di script progettati per interagire e automatizzare le operazioni sul gestionale aziendale **Kiwi**.  
Il sistema agisce come un "assistente virtuale silenzioso" che si occupa delle attività ripetitive a basso valore aggiunto, garantendo precisione nei dati e liberando tempo prezioso per attività a maggior valore strategico.

## 🎯 Cosa risolve questo progetto?

In un contesto operativo ad alto volume, la gestione manuale può generare colli di bottiglia e allungare le tempistiche di servizio.

1. **Tempo**: Automatizza l'estrazione dati da database, che prima richiedevano ore di navigazione manuale e preprocessing in Excel, in maniera sequenziale e sicura.
2. **Monitoraggio**: Fornisce una vista in tempo reale sui carichi di lavoro (Dashboard), permettendo al business di bilanciare le risorse prima che si verifichino disservizi.
3. **Continuità**: Gestisce lo scambio di agende tra operatori in modo massivo. Ad esempio, al cambio turno, il sistema può spostare centinaia di pratiche in pochi secondi tramite un semplice file di istruzioni Excel.
4. **Integrità**: Riduce l'errore umano tipico del "copia-incolla" manuale e controlla le anomalie di assegnazione provocate da eventuali bug del sistema principale.

---

## 🛠️ Modalità d'Uso

Il sistema è stato progettato per essere utilizzato in due modi, a seconda delle necessità del Business:

### 1. Attività Programmate

È il cuore dell'automazione.
Lo script `ScheduledTasks.py` gestisce le operazioni "silenziose" che devono avvenire periodicamente:

- **Igiene dei Dati**: Pulizia automatica dei file temporanei e obsoleti per mantenere il sistema efficiente.
- **Sincronizzazione**: Aggiornamento costante delle anagrafiche utenze e dei permessi.
- **Monitoraggio**: Scansione dei carichi di lavoro per prevenire saturazioni.

### 2. Estrazioni On-Demand

È uno strumento guidato per l'utente.
Lo script `DownloadEstrazioni.py` permette di scaricare report personalizzati dal portale. La particolarità è la **gestione intelligente del carico**: il sistema spezza automaticamente le richieste troppo pesanti in piccoli segmenti, garantendo la stabilità del portale Kiwi senza rallentare il lavoro degli altri utenti.

---

## 📋 Funzionalità di Business (Routines)

Le "routine" sono i compiti specifici che il sistema sa eseguire. Ecco le principali dal punto di vista funzionale:

### 📉 Monitoraggio Dashboard (Real-time)

Esegue una scansione della home page di Kiwi per contare le pratiche in gestione.
È fondamentale per accorgersi tempestivamente se un operatore ha troppe pratiche in coda e necessita di supporto.

### 🔄 Riassegnazioni Massive

Permette di spostare pratiche da un operatore all'altro o riportarle a uno stato precedente (retrocessione). L'input è un semplice file Excel: il sistema utilizza il **numero di cellulare** come chiave univoca per individuare le pratiche e aggiornarle automaticamente.

#### 👥 Controllo Accessi e Utenze

Monitora chi è censito nel portale e con quale ruolo.
Serve a prevenire anomalie per cui profili non autorizzati potrebbero ricevere erroneamente pratiche da gestire.

### 📊 Analisi Performance

Scarica lo storico delle attività svolte in un determinato periodo, fornendo la base dati necessaria per creare report di produttività e monitorare il raggiungimento degli obiettivi (KPI).

---

## 🧪 Sicurezza e Simulazione (Ambiente di Test)

Il progetto include una solida modalità **Test/Simulazione**:

- **In modalità TEST (Default)**: Il sistema non si collega al gestionale reale ma utilizza "copie HTML" locali. Questo permette di mostrare il funzionamento del software in totale sicurezza, senza rischiare di modificare dati reali o interferire con la produzione.
- **In modalità ONLINE**: Il sistema opera direttamente sul gestionale Kiwi per eseguire le attività programmate.

---

## 💡 Valore Aggiunto del Progetto

Questo progetto dimostra come sia possibile tradurre esigenze operative concrete (es. "ridurre il tempo speso in attività manuali") in soluzioni tecniche efficienti.
L'approccio utilizzato mette al primo posto la **stabilità del server (Kiwi)**, la **qualità dei dati raccolti** e la **facilità d'uso** per l'operatore finale.
