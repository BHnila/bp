"""
Modul pomocných funkcií pre systémovú analýzu a spracovanie dát.
Tento modul obsahuje funkcie na získavanie vstupov od používateľa,
spúšťanie analýz logov a sieťových tokov, ako aj na načítavanie
a predspracovanie vstupného datasetu.
"""

import time
import logging
from pathlib import Path
from typing import Callable
import pandas as pd

from src.log_tools.log_analyzer import analyze_logs
from src.log_tools.flow_analyzer import analyze_flow

logger = logging.getLogger(__name__)


def get_app_mode():
    """
    Získa a validuje výber módu analýzy z menu.

    Funkcia čaká na vstup používateľa a validuje, či je zadaná hodnota
    v správnom rozmedzí (1-3). V prípade nevalidného vstupu alebo
    prerušenia používateľom (Ctrl+C) poskytuje vhodnú reakciu.

    Návratová hodnota:
        int: Číslo vybratej možnosti (1, 2 alebo 3)
             Pri prerušení používateľom vráti 3 (ukončenie)
    """
    print("\nVyberte typ analýzy:")
    print("[1] Analýza Linux logov")
    print("[2] Analýza sieťových tokov")
    print("[3] Ukončiť program")

    while True:
        try:
            # Získanie vstupu od používateľa s ošetrením bielych znakov
            choice = input("\nZadajte váš výber (1-3): ").strip()

            # Validácia či je vstup jednou z povolených možností
            if choice in ['1', '2', '3']:
                return int(choice)
            else:
                print("Neplatný výber. Prosím zadajte 1, 2 alebo 3.")

        except KeyboardInterrupt:
            # Ošetrenie prerušenia programu používateľom (Ctrl+C)
            print("\n\nProgram bol prerušený používateľom.")
            return 3
        except Exception:
            # Ošetrenie ostatných chýb pri spracovaní vstupu
            print("Neplatný vstup. Prosím zadajte číslo 1, 2 alebo 3.")


def get_epochs_count():
    """
    Získa a validuje počet epoch od používateľa.

    Funkcia žiada používateľa o zadanie počtu epoch v rozmedzí 0-10.
    Pri zadaní 0 informuje používateľa o použití základného modelu.
    V prípade nevalidného vstupu alebo prerušenia používateľom (Ctrl+C)
    poskytuje vhodnú reakciu.

    Návratová hodnota:
        int: Počet epoch (0-10)
             Pri prerušení používateľom vráti None
    """
    while True:
        try:
            print("\nProsím, zvoľte počet epoch ladenia LLM modelu:")
            print("• 0 = Základný model Llama 3.2 3B (bez ladenia)")
            print("• 1-10 = Ladený model s daným počtom epoch")

            epochs_input = input("\nZadajte počet epoch (0-10): ").strip()

            # Validácia či je vstup číselný
            try:
                epochs = int(epochs_input)
            except ValueError:
                print("Neplatný vstup. Prosím zadajte číslo medzi 0 a 10.")
                continue

            # Validácia rozmedzí
            if 0 <= epochs <= 10:
                return epochs
            else:
                print("Neplatný výber. Prosím zadajte číslo medzi 0 a 10.")

        except KeyboardInterrupt:
            # Ošetrenie prerušenia programu používateľom (Ctrl+C)
            print("\n\nProgram bol prerušený používateľom.")
            return None
        except Exception:
            # Ošetrenie ostatných chýb pri spracovaní vstupu
            print("Neplatný vstup. Prosím zadajte číslo medzi 0 a 10.")


def run_log_analysis(folder_path: Path, num_epochs: int = 8):
    """
    Vykoná analýzu Linux logov zo zadaného priečinka.

    Funkcia spustí proces analýzy logov pomocou LLM agentov, meria
    čas vykonávania analýzy a zobrazuje výsledky používateľovi.
    V prípade chyby poskytuje informáciu o zlyhaní.

    Parametre:
        folder_path: Cesta k priečinku s log súbormi
        num_epochs: Počet epoch ladenia modelu (0-10)
    """
    print("\n=== Analýza Linux logov ===")
    # Zaznamenanie času začiatku analýzy
    start_time = time.time()

    try:
        # Spustenie analýzy logov zo zadaného priečinka
        analyze_logs(
            folder_path, num_epochs
        )

        # Výpočet a formátovanie času trvania analýzy
        end_time = time.time()
        elapsed = int(end_time - start_time)
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Zobrazenie času trvania v prehľadnom formáte
        print(f"\nAnalýza logov trvala {hours:02}:{minutes:02}:"
              f"{seconds:02} (hh:mm:ss).")

    except Exception as e:
        # Ošetrenie chýb pri analýze a informovanie používateľa
        print(f"Chyba pri analýze logov: {e}")


def run_flow_analysis(
    dataset: pd.DataFrame,
    unlabel_dataset: Callable,
    get_label: Callable,
    num_epochs: int = 8
):
    """
    Vykoná analýzu sieťových tokov z datasetu.

    Funkcia spustí proces analýzy sieťových tokov pomocou LLM agentov s použitím
    predspracovaného datasetu, meria čas vykonávania analýzy a zobrazuje výsledky
    používateľovi. V prípade chyby poskytuje informáciu o zlyhaní.

    Parametre:
        dataset: Predspracovaný pandas DataFrame so sieťovými tokmi
        unlabel_dataset: Funkcia na odstránenie labelov z datasetu
        get_label: Funkcia na získanie správnych labelov
        num_epochs: Počet epoch ladenia modelu (0-10)

    Návratová hodnota:
        None: Funkcia nevráti hodnotu, len zobrazuje výsledky
    """

    print("\n=== Analýza sieťových tokov ===")
    # Zaznamenanie času začiatku analýzy
    start_time = time.time()

    try:
        # Spustenie analýzy sieťových tokov s predspracovaným datasetom
        analyze_flow(dataset, unlabel_dataset,
                     get_label, num_epochs)

        # Výpočet a formátovanie času trvania analýzy
        end_time = time.time()
        elapsed = int(end_time - start_time)
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Zobrazenie času trvania v prehľadnom formáte
        print(f"\nAnalýza tokov trvala {hours:02}:{minutes:02}:"
              f"{seconds:02} (hh:mm:ss).")

    except Exception as e:
        # Ošetrenie chýb pri analýze a informovanie používateľa
        print(f"Chyba pri analýze tokov: {e}")
