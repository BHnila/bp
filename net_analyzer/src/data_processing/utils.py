"""
Tento modul obsahuje pomocné funkcie pre spracovanie datasetov.

Modul poskytuje nástroje pre:
- Validáciu súborových ciest a adresárov
- Načítavanie CSV súborov s robustným spracovaním chýb
- Manipuláciu s datasetmi (odstránenie stĺpcov, filtrovanie)
- Rozdelenie veľkých datasetov na menšie časti (chunks)
- Konverziu dát do formátov vhodných pre spracovanie LLM
"""

import logging
import pandas as pd
from pathlib import Path
from typing import List, Optional

# Nastavenie loggera pre tento modul
logger = logging.getLogger(__name__)


def validate_directory_path(directory_path: Path) -> None:
    """
    Validuje cestu k adresáru s datasetom.

    Parametre:
        directory_path (Path): Cesta k adresáru na validáciu

    Vyvoláva:
        FileNotFoundError: Ak adresár neexistuje
        NotADirectoryError: Ak cesta nie je adresár
    """
    # Overenie, či cesta existuje a je adresárom
    if not directory_path.exists():
        raise FileNotFoundError(f"Adresár '{directory_path}' neexistuje")
    if not directory_path.is_dir():
        raise NotADirectoryError(f"Cesta '{directory_path}' nie je adresár")


def load_single_csv_file(filepath: Path) -> Optional[pd.DataFrame]:
    """
    Načíta jeden CSV súbor s optimalizovaným spracovaním chýb.

    Parametre:
        filepath (Path): Cesta k CSV súboru

    Návratová hodnota:
        Optional[pd.DataFrame]: DataFrame ak sa načítanie podarilo, inak None

    Poznámka:
        Funkcia používa low_memory=False a definuje hodnoty pre NA.
        Všetky chyby sú logované a funkcia vracia None pri problémoch.
    """
    try:
        # Optimalizované načítanie s explicitne definovanými NA hodnotami
        df = pd.read_csv(
            filepath, low_memory=False, na_values=['', 'NA', 'NULL', 'null']
        )
        logger.info(
            f"Úspešne načítaný súbor: {filepath.name} - tvar: {df.shape}")
        return df
    except pd.errors.EmptyDataError:
        logger.error(f"Súbor '{filepath}' je prázdny")
        return None
    except pd.errors.ParserError as e:
        logger.error(f"Chyba pri parsovaní súboru '{filepath}': {e}")
        return None
    except Exception as e:
        logger.error(
            f"Neočakávaná chyba pri načítavaní súboru '{filepath}': {e}")
        return None


def get_csv_files(
    directory_path: Path, selected_files: Optional[List[str]] = None
) -> List[str]:
    """
    Získa zoznam CSV súborov z adresára.

    Parametre:
        directory_path (Path): Cesta k adresáru so súbormi
        selected_files (Optional[List[str]]): Konkrétne súbory na načítanie.
                                            Ak je None, vráti všetky CSV súbory.

    Návratová hodnota:
        List[str]: Zoznam názvov CSV súborov

    Vyvoláva:
        ValueError: Ak neboli nájdené žiadne CSV súbory
    """
    if selected_files is None:
        # Získaj všetky CSV súbory z adresára
        csv_files = [f.name for f in directory_path.iterdir()
                     if f.suffix == '.csv']
    else:
        # Validuj že všetky vybrané súbory existujú
        csv_files = []
        for file in selected_files:
            filepath = directory_path / file
            if filepath.exists():
                csv_files.append(file)
            else:
                logger.warning(
                    f"Súbor '{file}' nebol nájdený a bude preskočený")

    if not csv_files:
        raise ValueError("Neboli nájdené žiadne CSV súbory na spracovanie")

    return csv_files


def filter_important_columns(
    dataset: pd.DataFrame, important_columns: List[str]
) -> pd.DataFrame:
    """
    Filtruje dataset a ponechá len dôležité stĺpce.

    Táto funkcia vyberá z datasetu len tie stĺpce, ktoré sú zadané v zozname
    dôležitých stĺpcov a skutočne existujú v datasete. Je užitočná pre redukciu
    dimenzionality a zameranie sa len na relevantné vlastnosti dát.

    Parametre:
        dataset (pd.DataFrame): Pôvodný dataset na filtrovanie. Musí byť platný
                               DataFrame.
        important_columns (List[str]): Zoznam názvov stĺpcov, ktoré majú byť
                                      ponechané v datasete. Stĺpce, ktoré
                                      neexistujú v datasete, budú automaticky
                                      preskočené.

    Návratová hodnota:
        pd.DataFrame: Filtrovaný dataset obsahujúci len existujúce dôležité
                      stĺpce. Zachováva pôvodné poradie riadkov a typy dát.

    Poznámka:
        Funkcia loguje informáciu o rozmeroch filtrovaného datasetu
        pre kontrolu výsledku filtrovania.
    """
    # Vytvorenie zoznamu stĺpcov, ktoré skutočne existujú v datasete
    existing_columns = [
        col for col in important_columns if col in dataset.columns
    ]

    # Vytvorenie filtrovaného datasetu s existujúcimi stĺpcami
    filtered_dataset = dataset[existing_columns]

    # Výpis informácie o rozmeroch filtrovaného datasetu pomocou loggera
    logger.info(f"Filtered dataset shape: {filtered_dataset.shape}")

    return filtered_dataset


def chunk_dataset(
    dataset: pd.DataFrame, max_logs_per_chunk: int = 200000
) -> List[pd.DataFrame]:
    """
    Rozdelí dataset na menšie pandas DataFrame objekty pre efektívne spracovanie.

    Rozdelenie na menšie časti umožňuje postupné spracovanie a znižuje
    nároky na systémové prostriedky, čo je obzvlášť užitočné pri spracovaní
    veľkých datasetov s obmedzeným kontextovým oknom LLM.

    Parametre:
        dataset (pd.DataFrame): Dataset na rozdelenie. Musí byť platný DataFrame.
        max_logs_per_chunk (int, optional): Maximálny počet záznamov na chunk.
                                           Predvolená hodnota je 200,000.
                                           Musí byť kladné číslo.

    Návratová hodnota:
        List[pd.DataFrame]: Zoznam chunkov ako DataFrame objekty.
                           Každý chunk obsahuje maximálne max_logs_per_chunk
                           riadkov. Posledný chunk môže obsahovať menej riadkov.

    Vyvoláva:
        ValueError: Ak je max_logs_per_chunk menšie alebo rovné nulu.
    """
    # Validácia vstupného parametra
    if max_logs_per_chunk <= 0:
        raise ValueError("max_logs_per_chunk musí byť kladné číslo")

    # Kontrola prázdneho datasetu
    if dataset.empty:
        logger.warning("Dataset je prázdny, vytvorený jeden prázdny chunk")
        return [dataset.copy()]

    # Inicializácia zoznamu chunkov
    chunks = []
    total_rows = len(dataset)

    # Výpočet predpokladaného počtu chunkov
    expected_chunks = (total_rows + max_logs_per_chunk -
                       1) // max_logs_per_chunk
    logger.info(f"Spracovávam dataset s {total_rows:,} riadkami...")
    logger.info(f"Predpokladaný počet chunkov: {expected_chunks}")

    # Rozdelenie datasetu na chunky
    for chunk_idx, start in enumerate(range(0, total_rows,
                                           max_logs_per_chunk)):
        # Výpočet koncového indexu pre aktuálny chunk
        end = min(start + max_logs_per_chunk, total_rows)

        # Vytvorenie chunk pomocou iloc pre efektívne indexovanie
        # .copy() pre nezávislosť chunkov
        chunk = dataset.iloc[start:end].copy()
        chunks.append(chunk)

        # Progres pre veľké datasety
        if chunk_idx % 10 == 0 and chunk_idx > 0:
            logger.info(f"Spracovaných {chunk_idx} chunkov...")

    # Finálna správa o výsledku
    logger.info(f"Dataset úspešne rozdelený na {len(chunks)} chunkov.")
    logger.info(
        f"Priemerná veľkosť chunku: {total_rows / len(chunks):.0f} riadkov")

    return chunks


def parse_chunk_to_string(chunk: pd.DataFrame) -> str:
    """
    Konvertuje pandas DataFrame do textovej reprezentácie optimalizovanej pre LLM.

    Táto funkcia transformuje štruktúrované dáta z DataFrame do čitateľného
    textového formátu, ktorý je vhodný pre spracovanie pomocou jazykových modelov.

    Parametre:
        chunk (pd.DataFrame): Časť datasetu na konverziu. Musí byť platný DataFrame.

    Návratová hodnota:
        str: Textová reprezentácia časti datasetu vo formáte:
             "Columns: col1, col2, col3
              Row 1: col1: value1, col2: value2, col3: value3
              Row 2: ..."

    Poznámka:
        Táto funkcia používa originálne indexy z datasetu, nie postupné číslovanie.
        To umožňuje zachovanie kontextu pri spracovaní jednotlivých častí.
    """
    # Kontrola prázdneho chunku
    if chunk.empty:
        return "Spracovávaná časť datasetu je prázdna"

    # Vytvorenie hlavičky so zoznamom stĺpcov
    header = ", ".join(chunk.columns.astype(str))
    rows = [f"Columns: {header}"]

    # Spracovanie všetkých riadkov v chunki
    for position, (original_idx, row) in enumerate(chunk.iterrows(), 1):
        # Vytvorenie textovej reprezentácie riadku s bezpečným spracovaním
        row_values = []
        for col in chunk.columns:
            value = row[col]
            # Spracovanie špeciálnych hodnôt
            if pd.isna(value):
                value = "NULL"
            elif isinstance(value, str) and len(str(value)) > 100:
                # Skrátenie príliš dlhých textových hodnôt
                value = f"{str(value)[:97]}..."

            row_values.append(f"{col}: {value}")

        row_str = ", ".join(row_values)
        # Použitie originálneho indexu pre zachovanie kontextu
        rows.append(f"Row {original_idx}: {row_str}")

    return "\n".join(rows)
