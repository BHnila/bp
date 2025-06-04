"""
Tento modul poskytuje funkcionalitu pre automatizovanú analýzu
sieťových tokov. Zahŕňa rozdelenie datasetu
na časti, detekciu útokov hrubou silou pomocou LLM analýzy
a výpočet výkonnostných metrík (presnosť, citlivosť, F1 skóre).
"""

import logging
from typing import Callable
from pandas import DataFrame

from src.data_processing.utils import (
    chunk_dataset,
    parse_chunk_to_string
)
from src.log_tools.utils import (
    print_progress_report,
    print_current_metrics,
    print_final_report,
    evaluate_result
)
from src.llm.flows import detect_brute_force_in_flow
from src.system_core.data_models import AnalysisState

# Nastavenie logovania pre tento modul
logger = logging.getLogger(__name__)


def analyze_flow(dataset: DataFrame, unlabel_dataset: Callable,
                 get_label: Callable, num_epochs: int = 8) -> AnalysisState:
    """
    Analyzuje toky paketov pomocou LLM technológie.

    Funkcia rozdelí dataset na jednotlivé časti (jeden záznam = jedna časť),
    odstráni štítky pre objektívnu analýzu, konvertuje každý záznam
    do textovej formy a použije LLM na detekciu útokov hrubou silou. Výsledky
    sa vyhodnocujú proti skutočnej hodnote získanej zo štítkov a počítajú sa
    výkonnostné metriky.

    Proces zahŕňa:
    1. rozdelenie datasetu na jednotlivé záznamy,
    2. vypísanie informácií o aktuálnom stave spracovania,
    3. spracovanie každého záznamu jednotlivo,
    4. odstránenie štítkov pre objektívnu analýzu,
    5. konverziu záznamu do textovej formy pre LLM analýzu,
    6. detekciu útokov hrubou silou pomocou LLM,
    7. vyhodnotenie presnosti detekcie a aktualizáciu metrík,
    8. priebežné reportovanie progresu,
    9. finálne zhrnutie výsledkov.

    Parametre:
        dataset (DataFrame): Predspracovaný dataset obsahujúci sieťové toky
        unlabel_dataset (Callable): Funkcia na odstránenie štítkov z datasetu
        get_label (Callable): Funkcia na získanie štítku pre daný záznam
        num_epochs (int): Počet epoch ladenia pre LLM analýzu (predvolene 8)

    Návratová hodnota:
        AnalysisState: Finálny stav analýzy obsahujúci všetky metriky
    """
    # Rozdelenie datasetu na jednotlivé záznamy
    # Toto umožňuje detailnú analýzu každého sieťového toku
    dataset_chunks = chunk_dataset(dataset, max_logs_per_chunk=1)
    total_chunks = len(dataset_chunks)
    logger.info(f"Dataset rozdelený na {total_chunks} chunk-ov")

    print("Začína sa analýza...")
    # Inicializácia stavu analýzy s nulovými hodnotami
    analysis_state = AnalysisState()

    # Spracovanie každého záznamu jednotlivo
    for i, chunk in enumerate(dataset_chunks, start=1):
        # Zobrazenie pokroku spracovania
        print_progress_report(i, total_chunks, f"chunk_{i}")

        try:
            # Odstránenie štítku pre objektívnu analýzu
            unlabeled_chunk = unlabel_dataset(chunk, label_column="Label")

            # Konverzia záznamu do textovej formy pre LLM analýzu
            chunk_string = parse_chunk_to_string(unlabeled_chunk)

            # Detekcia útokov hrubou silou pomocou LLM
            result_of_analysis = detect_brute_force_in_flow(
                chunk_string, num_epochs)

            malicious = get_label(chunk)

            # Vyhodnotenie výsledku proti štítkom a aktualizácia metrík
            analysis_state = evaluate_result(
                malicious, result_of_analysis.bruteforce, analysis_state
            )

            # Zobrazenie aktuálnych metrík po spracovaní záznamu
            print_current_metrics(analysis_state)

        except Exception as e:
            # Zaznamenanie chyby a pokračovanie v spracovaní ďalších záznamov
            logger.error(f"Chyba pri spracovaní chunk-u {i}: {e}")
            print(f"Chyba pri spracovaní chunk-u {i}: {e}")
            continue

    # Zobrazenie finálnej správy s výsledkami analýzy
    print_final_report(analysis_state)
    logger.info("Analýza sieťových tokov dokončená")

    return analysis_state
