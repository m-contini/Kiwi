from routines import (
    pulizia_quotidiana_file_obsoleti,
    estrai_utenze_attive,
    main_dashboard_fetch,
    lavorazioni_consulenti,
    riassegnazioni_retrocessioni
)

# Flag globale
# Se True: esegue gli script offline
# facendo scraping da file HTML che simulano Kiwi
# anziché da web
__TEST__ = True

if __name__ == '__main__':

    for routine in (
        pulizia_quotidiana_file_obsoleti,
        estrai_utenze_attive,
        main_dashboard_fetch,
        lavorazioni_consulenti,
        riassegnazioni_retrocessioni
    ):
        routine(__TEST__)
