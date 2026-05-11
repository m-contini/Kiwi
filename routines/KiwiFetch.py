
import logging
from pathlib import Path

from source import (
    Auth,
    HomeKiwiOutput,
    KiwiTable,
)

def run(__TEST__: bool = False) -> None:
    """
    Questo script si autentica a **Kiwi** per recuperare numeri dalla dashboard nella Home,
    estrarre le tabelle in cui sono contenuti e salvarle in formato CSV e JSON.

    Questo script è pensato per essere eseguito tramite uno scheduler (es. crontab).

    La risposta HTML viene salvata, con timestamp identificativo, al percorso:  
    `./HomeKiwi/htmlTbls/HomeKiwi_2026_05_10_19_14_22.html`

    I dati vengono salvati in CSV e JSON, identificati univocamente da un timestamp, ai seguenti percorsi:  
    `./HomeKiwi/csvTbls/2026_05_10_19_14_22_Consulente Milano.csv`
    `./HomeKiwi/jsonTbls/2026_05_10_19_14_22_Consulente Milano.json`
    `./HomeKiwi/csvTbls/2026_05_10_19_14_22_Consulente Tirana.csv`
    `./HomeKiwi/jsonTbls/2026_05_10_19_14_22_Consulente Tirana.json`

    Es. di struttura dei due file:
    ### CSV
    ```plain
    Consulente Milano,Nuove Anagrafiche,Primo reminder,Ultimo reminder,Totale aperte,"Stato "Nuova Anagrafica"",Riceve Anagrafiche
    Al*********co,0,"20 Feb, 20:53","Gio 27 Giu, 13:02",8,5,NO
    ```

    ### JSON
    ```json
    {
        "Consulente Tirana": "Al************ra",
        "Nuove Anagrafiche": "21",
        "Primo reminder": "Gio 20 Giu, 18:01",
        "Ultimo reminder": "Gio 04 Lug, 14:00",
        "Totale aperte (*)": "517",
        "Stato \"Nuova Anagrafica\"": "517",
        "Riceve Anagrafiche": "SI"
    }
    ```
    """

    try:
        # Imposta la sessione HTTP
        kiwi = Auth(Path(__file__) if __TEST__ else None)
        kiwi.login()

        # Richiesta GET per ottenere KPI dalla dashboard Home Kiwi
        home_kiwi = kiwi.get_dashboard_snapshot()
        logging.info("Snapshot della dashboard recuperato correttamente.")

        # Istanza custom per effettuare parsing e salvataggio
        kiwi_table = KiwiTable()

        # Salva risposta HTML
        kiwi_table.to_html(home_kiwi.text)

        # Parsing delle due tabelle nella Home Kiwi
        # 1) `Consulente Milano` (Consulenti)
        # 2) `Consulente Tirana` (GDO)
        tables = kiwi_table.fetch_all_tables(home_kiwi.text)
        tables_processed = 0

        for table in tables:

            if not (headers := kiwi_table.is_valid_dashboard_table(table)):
                continue

            # Salva in CSV e JSON le tabelle identificate
            kiwi_table.to_csv(table, headers)
            kiwi_table.to_json(table, headers)
            tables_processed += 1
            logging.info(f"Tabella con header {headers[0]} elaborata e salvata.")

        logging.info(f"Operazione completata. Elaborate {tables_processed} tabelle.")
        logging.info(f"Tabelle salvate nelle sottocartelle di {HomeKiwiOutput.CSV_DIR.name} e {HomeKiwiOutput.JSON_DIR.name}")

    except Exception as e:
        logging.error(f"Errore critico durante il KiwiFetch: {e}", exc_info=True)
        raise
