"""
Tento modul poskytuje hlavnú funkcionalitu pre kompletnú analýzu log súborov.
Umožňuje detekciu útokov hrubou silou pomocou LLM agentov a následné vyhodnotenie
presnosti detekcie pomocou výkonnostných metrík ako presnosť, citlivosť a F1 skóre.
"""

import logging
from pathlib import Path

from src.llm.flows import detect_brute_force_in_logs
from src.system_core.data_models import AnalysisState
from src.log_tools.utils import (
    read_linux_log_file,
    count_txt_files,
    determine_label_from_filename,
    print_progress_report,
    print_current_metrics,
    print_final_report,
    evaluate_result
)

# Nastavenie logovania pre tento modul
logger = logging.getLogger(__name__)


def analyze_logs(folder_path: Path, num_epochs: int = 8) -> AnalysisState:
    """
    Spracuje log súbory v špecifikovanom priečinku a vypočíta výkonnostné metriky.

    Hlavná funkcia modulu, ktorá vykonáva kompletnú analýzu všetkých log
    súborov v zadanom priečinku. Funkcia rekurzívne prechádza všetky
    podpriečinky, načíta každý .txt súbor, vyhodnotí jeho obsah pomocou
    LLM detekčného systému a porovná výsledky so skutočnými štítkami
    určenými z názvov súborov.

    Proces zahŕňa:
    1. overenie existencie priečinka,
    2. spočítanie celkového počtu súborov na spracovanie,
    3. rekurzívne prechádzanie všetkých .txt súborov,
    4. zistenie klasifikačných štítkov z názvov súborov,
    5. načítanie obsahu log súboru do pamäte,
    6. vypísanie informácií o aktuálnom stave spracovania,
    7. detekciu útokov hrubou silou pomocou LLM systému,
    8. vyhodnotenie presnosti detekcie a aktualizáciu metrík,
    9. priebežné reportovanie progresu,
    10. finálne zhrnutie výsledkov.

    Parametre:
        folder_path (Path): Absolútna alebo relatívna cesta k priečinku
            obsahujúcemu log súbory na analýzu. Priečinok môže obsahovať
            podpriečinky, ktoré budú tiež spracované.
        num_epochs (int): Počet epoch ladenia pre LLM detekčný systém.

    Návratová hodnota:
        AnalysisState: Finálny stav analýzy obsahujúci všetky vypočítané
            štatistiky a výkonnostné metriky (presnosť, citlivosť, F1 skóre).

    Výnimky:
        FileNotFoundError: Ak špecifikovaná cesta k priečinku neexistuje.
    """

    if not folder_path.exists():
        raise FileNotFoundError(f"Cesta k priečinku {folder_path} neexistuje.")

    # Inicializácia logovania a úvodných informácií
    logger.info("Spúšťa sa analýza logov...")
    print("Pripravuje sa analýza...\n")

    # Inicializácia stavu analýzy a počítanie celkového počtu súborov
    analysis_state = AnalysisState()
    total_files = count_txt_files(folder_path)
    processed_files = 0

    # Rekurzívne prechádzanie všetkých súborov v priečinku a podpriečinkoch
    for file_path in folder_path.rglob("*.txt"):
        # Získanie názvu súboru pre reportovanie progresu a určenie štítku
        file_name = file_path.name
        # Určenie klasifikačného štítku zo súboru
        label = determine_label_from_filename(file_name)
        # Preskočenie súborov bez jasného štítku (neznámy formát názvu)
        if label is None:
            logger.warning(
                f"Preskakuje sa súbor {file_name}: nedá sa určiť štítok"
            )
            continue

        # Aktualizácia počítadla spracovaných súborov a zobrazenie progresu
        processed_files += 1
        print_progress_report(processed_files, total_files, file_name)

        try:
            # Načítanie obsahu log súboru do pamäte
            file_content = read_linux_log_file(file_path)

            # Vykonanie analýzy obsahu pomocou LLM detekčného systému
            analysis_result = detect_brute_force_in_logs(
                file_content, num_epochs)

            # Vyhodnotenie výsledku voči skutočnosti a aktualizácia metrík
            analysis_state = evaluate_result(
                label, analysis_result.system_compromised, analysis_state
            )

            # Zobrazenie aktuálneho stavu metrík
            print_current_metrics(analysis_state)

        except Exception as e:
            # Spracovanie ešte nezachytených chýb pri načítaní alebo
            # analýze súboru
            logger.error(f"Chyba pri spracovaní súboru {file_name}: {e}")
            print(f"Chyba pri spracovaní súboru {file_name}: {e}")
            continue

    # Zobrazenie finálnej správy s kompletným súhrnom analýzy
    print_final_report(analysis_state)
    logger.info("Analýza logov dokončená")

    return analysis_state
