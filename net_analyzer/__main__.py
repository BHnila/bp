"""
Hlavný modul pre spustenie LLM Log Analyzer aplikácie.

Tento modul poskytuje interaktívne rozhranie pre používateľa na výber
a spustenie rôznych typov analýzy logov a sieťových tokov.
"""

import logging
from pathlib import Path

from src.system_core.utils import (
    get_app_mode,
    get_epochs_count,
    run_log_analysis,
    run_flow_analysis
)
from src.system_core.exceptions import DatasetLoadError
from src.data_processing.process_IDS2017 import (
    load_and_preprocess_ids2017_dataset,
    unlabel_IDS2017_dataset,
    get_IDS2017_label
)

# Globálne nastavenie logovania pre celú aplikáciu
logging.basicConfig(
    level=logging.INFO,
)

# Definícia ciest k vstupným súborom
PATH_TO_FLOWS = "./flow_input"  # Cesta k súborom so sieťovými tokmi
PATH_TO_LOGS = "./log_input"    # Cesta k súborom s logmi

# Inicializácia loggera pre tento modul
logger = logging.getLogger(__name__)


def main():
    """
    Hlavná funkcia aplikácie - riadenie používateľského rozhrania.

    Implementuje hlavnú slučku programu, ktorá zobrazuje menu,
    spracováva výber používateľa a spúšťa príslušné analýzy.
    Poskytuje možnosť opakovania analýz alebo ukončenia programu.
    """
    # Zobrazenie úvodnej hlavičky aplikácie
    print(r"""
             _   _      _                          _
            | \ | |    | |       /\               | |
            |  \| | ___| |_     /  \   _ __   __ _| |_   _ _______ _ __
            | . ` |/ _ \ __|   / /\ \ | '_ \ / _` | | | | |_  / _ \ '__|
            | |\  |  __/ |_   / ____ \| | | | (_| | | |_| |/ /  __/ |
            |_| \_|\___|\__| /_/    \_\_| |_|\__,_|_|\__, /___\___|_|
                                                      __/ |
                                                     |___/
        """)
    print("Vitajte v LLM Net Analyzer aplikácii!\n")
    print("© Boris Hnila, 2025")

    # Hlavná slučka programu
    while True:
        # Získanie výberu režimu aplikácie od používateľa
        # (log analýza vs flow analýza)
        choice = get_app_mode()

        # Získanie počtu epoch ladenia modelu
        epochs = get_epochs_count()

        # Zobrazenie informácie o type modelu, ktorý bude použitý
        if epochs == 0:
            print("\nBude použitý základný model Llama 3.2 3B bez ladenia.")
        else:
            if choice == 1:
                print(f"\nBude použitý ladený model BruteLlama3B "
                      f"s {epochs} epochami.")
            elif choice == 2:
                print(f"\nBude použitý ladený model SecLlama3B "
                      f"s {epochs} epochami.")

        # Spracovanie výberu používateľa
        if choice == 1:
            # Analýza Linux logov - režim 1
            # Pokračuj len ak používateľ nezrušil zadávanie
            if epochs is not None:
                run_log_analysis(Path(PATH_TO_LOGS), epochs)
            else:
                continue  # Vráť sa do menu ak používateľ prerušil zadávanie
        elif choice == 2:
            # Analýza sieťových tokov - režim 2
            # Pokračuj len ak používateľ nezrušil zadávanie
            if epochs is not None:
                try:
                    # Načítanie a predspracovanie IDS2017 datasetu
                    dataset = load_and_preprocess_ids2017_dataset(
                        Path(PATH_TO_FLOWS)
                    )
                    logger.info("Dataset úspešne načítaný")
                except Exception as e:
                    logger.error(f"Chyba pri načítaní datasetu: {e}")
                    raise DatasetLoadError(
                        f"Chyba pri načítaní datasetu: {e}"
                    )
                # Spustenie analýzy sieťových tokov s príslušnými
                # pomocnými funkciami
                run_flow_analysis(
                    dataset,
                    unlabel_IDS2017_dataset,
                    get_IDS2017_label,
                    epochs
                )
            else:
                continue  # Vráť sa do menu ak používateľ prerušil zadávanie
        elif choice == 3:
            # Ukončenie programu
            print("\nUkončujem program...")
            break

        # Dotaz na pokračovanie alebo ukončenie po dokončení analýzy
        while True:
            continue_choice = input(
                "\nChcete spustiť ďalšiu analýzu? (a/n): "
            ).strip().lower()

            # Pokračovanie v ďalšej analýze
            if continue_choice in ['a', 'ano', 'y', 'yes']:
                break  # Opusť vnútornú slučku a pokračuj v hlavnej slučke
            # Ukončenie programu
            elif continue_choice in ['n', 'nie', 'no']:
                print("\nUkončujem program...")
                return  # Ukončí celú funkciu main()
            # Neplatný vstup - opakuj dotaz
            else:
                print("Prosím zadajte 'a' pre áno alebo 'n' pre nie.")


# Spustenie hlavnej funkcie ak je súbor spustený priamo
if __name__ == "__main__":
    main()
