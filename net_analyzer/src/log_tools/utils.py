"""
Modul pomocných funkcií pre log_tools balík.
"""

import logging
from typing import Optional, Union
from pathlib import Path

from src.system_core.data_models import AnalysisState

# Nastavenie loggingu pre tento modul
logger = logging.getLogger(__name__)


def calculate_precision(tp: int, fp: int) -> float:
    """
    Vypočíta presnosť.

    Presnosť predstavuje pravdepodobnosť, že pozitívna predikcia
    modelu je skutočne pozitívna. Definícia sa nachádza
    v kapitole 4.1.4.

    Parametre:
        tp (int): Počet detekovaných skutočne pozitívnych prípadov
        fp (int): Počet detekovaných falošne pozitívnych prípadov

    Návratová hodnota:
        float: Hodnota presnosti v rozmedzí <0, 1>.
    """
    # Kontrola delenia nulou - ak nie sú žiadne pozitívne predikcie
    if tp + fp == 0:
        return 0.0

    # Výpočet presnosti pomocou základného vzorca
    return tp / (tp + fp)


def calculate_recall(tp: int, fn: int) -> float:
    """
    Vypočíta citlivosť.

    Citlivosť (alebo úplnosť) hovorí, aká je pravdepodobnosť, že
    model detekuje skutočne pozitívny prípad. Definícia sa nachádza
    v kapitole 4.1.3.

    Parametre:
        tp (int): Počet detekovaných skutočne pozitívnych prípadov
        fn (int): Počet falošne negatívnych prípadov

    Návratová hodnota:
        float: Hodnota úplnosti v rozmedzí <0, 1>.
    """
    # Kontrola delenia nulou - ak nie sú žiadne skutočne pozitívne prípady
    if tp + fn == 0:
        return 0.0

    # Výpočet úplnosti pomocou základného vzorca
    return tp / (tp + fn)


def f1_score(precision: float, recall: float) -> float:
    """
    Vypočíta F1 skóre.

    F1 skóre je harmonický priemer presnosti a citlivosti, ktorý poskytuje
    vyvážené hodnotenie modelu.

    Parametre:
        precision (float): Hodnota presnosti v rozmedzí <0, 1>
        recall (float): Hodnota citlivosti v rozmedzí <0, 1>

    Návratová hodnota:
        float: F1 skóre v rozmedzí <0, 1>.
    """
    # Kontrola delenia nulou - ak sú obe metriky nulové
    if precision + recall == 0:
        return 0.0

    # Výpočet F1 skóre pomocou harmonického priemeru
    return 2 * (precision * recall) / (precision + recall)


def read_linux_log_file(file_path: str) -> str:
    """
    Načíta obsah textového súboru obsahujúceho systémové logy.

    Funkcia bezpečne načíta obsah súboru s logmi a spracuje chyby pri čítaní.
    Očakáva sa, že súbor je v UTF-8 kódovaní. V prípade chyby vráti prázdny
    reťazec a zaloguje varovanie. Všetky chyby sú spracované vnútorne
    a zalogované bez vyvolania výnimiek.

    Parametre:
        file_path (str): Absolútna alebo relatívna cesta k .txt súboru s logmi

    Návratová hodnota:
        str: Obsah súboru ako reťazec. Prázdny reťazec v prípade chyby alebo
            neexistujúceho súboru.
    """
    # Konverzia na Path objekt pre lepšie spracovanie ciest
    file_path = Path(file_path)

    # Kontrola existencie súboru pred pokusmi o čítanie
    if not file_path.exists():
        logger.warning(f"Súbor {file_path} neexistuje.")
        return ""

    try:
        # Načítanie obsahu s explicitným UTF-8 kódovaním
        return file_path.read_text(encoding='utf-8')
    except IOError as e:
        # Spracovanie všetkých I/O chýb (permissions, disk space, atď.)
        logger.warning(f"Chyba pri čítaní súboru {file_path}: {e}")
        return ""


def determine_label_from_filename(filename: str) -> Optional[bool]:
    """
    Určí označenie skupiny logov na základe názvu súboru.

    Funkcia analyzuje názov súboru a na základe kľúčových slov určí, či obsahuje
    škodlivé alebo neškodné logy. Funkcia hľadá kľúčové
    slová "MALICIOUS" a "BENIGN" v názve súboru (case-insensitive).

    Parametre:
        filename (str): Názov súboru (môže obsahovať cestu) na analýzu

    Návratová hodnota:
        bool: True ak súbor obsahuje škodlivé logy,
            False ak súbor obsahuje neškodné logy, alebo None ak sa nedá
            určiť typ obsahu.
    """
    # Konverzia na veľké písmená pre case-insensitive porovnanie
    filename_upper = filename.upper()

    # Kontrola prítomnosti kľúčových slov v názve súboru
    if 'MALICIOUS' in filename_upper:
        return True
    elif 'BENIGN' in filename_upper:
        return False

    # Ak sa nenašli žiadne známe kľúčové slová
    return None


def count_txt_files(folder_path: Union[str, Path]) -> int:
    """
    Spočíta celkový počet textových súborov (.txt) v zadanom priečinku.

    Funkcia rekurzívne prechádza zadaný priečinok a všetky jeho podpriečinky,
    spočíta všetky súbory s príponou .txt. Užitočné pre získanie celkového
    počtu log súborov v datasete pred spracovaním. Ak priečinok neexistuje,
    funkcia vráti 0 bez vyvolania výnimky.

    Parametre:
        folder_path (Union[str, Path]): Cesta k priečinku, v ktorom sa majú počítať .txt
            súbory

    Návratová hodnota:
        int: Celkový počet .txt súborov nájdených v priečinku a podpriečinkoch.
    """
    # Konverzia na Path objekt pre lepšie spracovanie ciest
    folder_path = Path(folder_path)

    # Vrátenie 0 ak priečinok neexistuje
    if not folder_path.exists():
        return 0

    # Spočítanie všetkých .txt súborov rekurzívne pomocou rglob
    return len(list(folder_path.rglob("*.txt")))


def print_progress_report(iteration: int, total_files: int, filename: str) -> None:
    """
    Vypíše informácie o progrese spracovania aktuálneho súboru.

    Funkcia zobrazuje užívateľovi priebežné informácie o progrese analýzy
    logov. Poskytuje prehľad o tom, koľko súborov už bolo spracovaných
    a ktorý súbor sa práve spracováva. Užitočné pre dlhé analýzy s veľkým
    počtom súborov.

    Parametre:
        iteration (int): Poradové číslo aktuálne spracovávaného súboru
            (začína od 1)
        total_files (int): Celkový počet súborov určených na spracovanie
        filename (str): Názov aktuálne spracovávaného súboru

    Návratová hodnota:
        None: Funkcia iba vypíše informácie na štandardný výstup.
    """
    print(f"=== Aktuálny progres {iteration}/{total_files} ===")
    print(f"Aktuálny súbor: {filename}")


def print_final_report(analysis_state: AnalysisState) -> None:
    """
    Vypíše finálnu správu s kompletným súhrnom analýzy.

    Funkcia vytvorí a zobrazí finálnu správu obsahujúcu všetky dôležité
    štatistiky z procesu analýzy logov. Správa obsahuje počty jednotlivých
    typov detekcií (skutočne pozitívne, falošne pozitívne, falošne negatívne)
    a vypočítané výkonnostné metriky modelu detekcie.

    Parametre:
        analysis_state (AnalysisState): Finálny stav analýzy obsahujúci
            všetky vypočítané štatistiky a metriky

    Návratová hodnota:
        None: Funkcia iba vypíše finálnu správu na štandardný výstup.
    """
    print("\n=== Výsledok analýzy ===")
    print(f"Celkový počet pozitívnych: {analysis_state.positives}")
    print(f"Skutočne pozitívne: {analysis_state.detected_real_positives}")
    print(f"Falošne pozitívne: {analysis_state.detected_false_positives}")
    print(f"Falošne negatívne: {analysis_state.detected_false_negatives}")
    print("--- Výkonnostné metriky ---")
    print(f"Presnosť: {analysis_state.precision:.4f}")
    print(f"Úplnosť: {analysis_state.recall:.4f}")
    print(f"F1 skóre: {analysis_state.f1_score:.4f}")
    print("===============")


def print_current_metrics(analysis_state: AnalysisState) -> None:
    """
    Vypíše aktuálne metriky pre momentálnu iteráciu spracovania.

    Funkcia zobrazuje priebežné výsledky analýzy po spracovaní každého
    súboru. Poskytuje užívateľovi okamžitú spätnú väzbu o výkonnosti
    detekčného systému počas behu analýzy. Zobrazuje aktuálne počty
    detekcií a momentálne hodnoty vypočítaných metrík.

    Parametre:
        analysis_state (AnalysisState): Aktuálny stav analýzy s priebežnými
            štatistikami a metrikami

    Návratová hodnota:
        None: Funkcia iba vypíše aktuálne metriky na štandardný výstup.
    """
    print("Momentálny stav analýzy:")
    print(f"  Pozitívne: {analysis_state.positives}")
    print(f"  Skutočne pozitívne: {analysis_state.detected_real_positives}")
    print(f"  Falošne pozitívne: {analysis_state.detected_false_positives}")
    print(f"  Falošne negatívne: {analysis_state.detected_false_negatives}")
    print("Momentálne hodnoty metrík:")
    print(f"  Presnosť: {analysis_state.precision}")
    print(f"  Citlivosť: {analysis_state.recall}")
    print(f"  F1 skóre: {analysis_state.f1_score}")
    print("===============\n")


def evaluate_result(
    malicious: bool,
    analysis_result: bool,
    analysis_state: AnalysisState
) -> AnalysisState:
    """
    Vyhodnotí výsledok detekcie a aktualizuje stav analýzy.

    Funkcia porovná skutočný stav súboru (referenčnú hodnotu) s výsledkom detekcie
    a na základe toho aktualizuje príslušné počítadlá v matici konfúzie.
    Vypočíta nové hodnoty výkonnostných metrík (presnosť, citlivosť, F1 skóre).

    Parametre:
        malicious (bool): Skutočný stav súboru (True = škodlivý, False = neškodný)
        analysis_result (bool): Výsledok detekcie (True = detekovaný ako škodlivý)
        analysis_state (AnalysisState): Aktuálny stav analýzy s počítadlami

    Návratová hodnota:
        AnalysisState: Nový stav analýzy s aktualizovanými počítadlami a metrikami.
    """
    # Extrakcia aktuálnych hodnôt zo stavu analýzy
    positives = analysis_state.positives
    true_positives = analysis_state.detected_real_positives
    false_positives = analysis_state.detected_false_positives
    false_negatives = analysis_state.detected_false_negatives

    # Aktualizácia počítadiel na základe výsledku detekcie a skutočného stavu
    if malicious:
        # Súbor obsahuje škodlivé aktivity (skutočný stav)
        positives += 1
        if analysis_result:
            # Skutočne pozitívny: správne identifikované škodlivé aktivity
            true_positives += 1
        else:
            # Falošne negatívny: zmeškané škodlivé aktivity (nedetegované)
            false_negatives += 1
    else:
        # Súbor obsahuje neškodné aktivity (skutočný stav)
        if analysis_result:
            # Falošne pozitívny: nesprávne označené benígne aktivity ako škodlivé
            false_positives += 1

    # Výpočet aktualizovaných výkonnostných metrík
    precision = calculate_precision(true_positives, false_positives)
    recall = calculate_recall(true_positives, false_negatives)
    f1 = f1_score(precision, recall)

    # Vytvorenie a vrátenie nového stavu analýzy s aktualizovanými hodnotami
    return AnalysisState(
        positives=positives,
        detected_real_positives=true_positives,
        detected_false_positives=false_positives,
        detected_false_negatives=false_negatives,
        precision=precision,
        recall=recall,
        f1_score=f1
    )
