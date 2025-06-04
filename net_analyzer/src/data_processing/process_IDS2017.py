"""
Tento modul poskytuje funkcie pre načítanie, spracovanie a čistenie
datasetu CIC-IDS 2017 z CSV súborov. Umožňuje flexibilné načítanie súborov,
čistenie dát, štandardizáciu názvov stĺpcov a prípravu datasetu pre analýzu
útokov hrubou silou.
"""

import pandas as pd
import numpy as np
import logging
from typing import List, Optional
from pandas import DataFrame
from pathlib import Path

from src.data_processing.utils import (validate_directory_path, get_csv_files,
                                       load_single_csv_file, filter_important_columns)
from src.system_core.exceptions import DatasetLoadError

# Konfigurácia logovacieho systému
logger = logging.getLogger(__name__)


def clean_dataframe(df: pd.DataFrame,
                    drop_na: bool = True,
                    drop_inf: bool = True,
                    drop_duplicates: bool = True) -> pd.DataFrame:
    """
    Prečistí pandas DataFrame.

    Táto funkcia odstráni riadky s NaN hodnotami, nekonečnými hodnotami
    a duplicitné riadky podľa nastavení parametrov. Všetky operácie sú
    logované pre lepšiu sledovateľnosť.

    Parametre:
        df (pd.DataFrame): DataFrame na vyčistenie
        drop_na (bool): Či odstrániť riadky s NaN hodnotami
        drop_inf (bool): Či odstrániť riadky s nekonečnými hodnotami
        drop_duplicates (bool): Či odstrániť duplicitné riadky

    Návratová hodnota:
        pd.DataFrame: Vyčistený DataFrame
    """
    original_shape = df.shape

    # Odstránenie NaN hodnôt
    if drop_na:
        df = df.dropna()
        logger.info(f"Odstránené riadky s NaN hodnotami: "
                    f"{original_shape[0] - df.shape[0]}")

    # Odstránenie nekonečných hodnôt
    if drop_inf:
        # Nájdi numerické stĺpce
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            # Odstráň riadky s inf/-inf hodnotami iba v numerických stĺpcoch
            rows_before_inf = df.shape[0]
            mask = ~df[numeric_columns].isin([np.inf, -np.inf]).any(axis=1)
            df = df[mask]
            rows_removed_inf = rows_before_inf - df.shape[0]
            if rows_removed_inf > 0:
                logger.info(f"Odstránené riadky s nekonečnými hodnotami: "
                            f"{rows_removed_inf}")

    # Odstránenie duplicitných riadkov
    if drop_duplicates:
        duplicates_before = df.shape[0]
        df = df.drop_duplicates()
        duplicates_removed = duplicates_before - df.shape[0]
        if duplicates_removed > 0:
            logger.info(f"Odstránené duplicitné riadky: {duplicates_removed}")

    logger.info(f"Čistenie dokončené. Pôvodný tvar: {original_shape}, "
                f"nový tvar: {df.shape}")
    return df


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Štandardizuje názvy stĺpcov v DataFrame.

    Táto funkcia odstráni medzery a špeciálne znaky z názvov stĺpcov
    a zabezpečí, že názvy stĺpcov sú konzistentné a ľahko použiteľné.

    Parametre:
        df (pd.DataFrame): DataFrame so stĺpcami na štandardizáciu

    Návratová hodnota:
        pd.DataFrame: DataFrame so štandardizovanými názvami stĺpcov
    """
    # Odstráň medzery a špeciálne znaky z názvov stĺpcov
    df.columns = (df.columns.str.strip()
                  .str.replace(' ', '_')
                  .str.replace('[^a-zA-Z0-9_]', '', regex=True))

    return df


def standardize_label_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Štandardizuje stĺpec 'Label' v DataFrame.

    Táto funkcia zabezpečí, že stĺpec 'Label' bude mať konzistentný typ
    a formát. Odstráni medzery a prevedie hodnoty na typ string.

    Parametre:
        df (pd.DataFrame): DataFrame so stĺpcom 'Label'

    Návratová hodnota:
        pd.DataFrame: DataFrame so štandardizovaným stĺpcom 'Label'
    """
    if 'Label' in df.columns:
        df['Label'] = df['Label'].astype(str).str.strip()
        logger.info("Štandardizovaný stĺpec 'Label' na string typ")

    return df


def load_ids2017_dataset(
        directory_path: Path,
        selected_files: Optional[List[str]] = None,
        drop_na: bool = True,
        drop_inf: bool = True,
        drop_duplicates: bool = True) -> pd.DataFrame:
    """
    Načíta a spracuje IDS 2017 dataset z CSV súborov.

    Táto funkcia poskytuje komplexné riešenie pre načítanie IDS 2017 datasetu
    s možnosťou výberu konkrétnych súborov, čistenia dát a konfigurácie výstupu.

    Parametre:
        directory_path (Path): Cesta k adresáru obsahujúcemu CSV súbory.
            Musí existovať a byť dostupný pre čítanie.
        selected_files (Optional[List[str]]): Konkrétne súbory na načítanie.
            Ak je None, načítajú sa všetky CSV súbory z adresára.
            Súbory musia existovať v zadanom adresári.
        drop_na (bool): Či odstrániť riadky obsahujúce NaN hodnoty.
            Predvolené: True
        drop_inf (bool): Či odstrániť riadky obsahujúce nekonečné hodnoty.
            Predvolené: True
        drop_duplicates (bool): Či odstrániť duplicitné riadky.
            Predvolené: True

    Návratová hodnota:
        pd.DataFrame: Kombinovaný a vyčistený dataset zo všetkých načítaných
            súborov. DataFrame obsahuje štandardizované názvy stĺpcov
            a vyčistené dáta.

    Vyvoláva:
        FileNotFoundError: Ak zadaný adresár neexistuje
        NotADirectoryError: Ak zadaná cesta nie je adresár
        ValueError: Ak neboli nájdené žiadne CSV súbory na spracovanie
        Exception: Pri iných neočakávaných chybách počas spracovania
    """
    try:
        # Kontrola prítomnosti adresára
        validate_directory_path(directory_path)

        # Získanie zoznamu CSV súborov
        csv_files = get_csv_files(directory_path, selected_files)
        logger.info(f"Nájdených {len(csv_files)} súborov na načítanie: "
                    f"{csv_files}")

        # Načítanie všetkých CSV súborov
        dataframes = []
        total_rows = 0

        for filename in csv_files:
            filepath = directory_path / filename
            logger.info(f"Načítavam súbor: {filename}")

            # Načítanie jednotlivého súboru
            df = load_single_csv_file(filepath)
            if df is not None:
                dataframes.append(df)
                total_rows += df.shape[0]
            else:
                logger.warning(f"Súbor '{filename}' bol preskočený kvôli "
                               f"chybám")

        # Kontrola či sa podarilo načítať aspoň jeden súbor
        if not dataframes:
            raise ValueError("Nepodarilo sa načítať žiadny súbor")

        logger.info(f"Spájam {len(dataframes)} datasetov s celkovým počtom "
                    f"{total_rows} riadkov")
        # Spojenie všetkých DataFrames
        dataset = pd.concat(dataframes, ignore_index=True, sort=False)
        logger.info(f"Dataset po spojení má tvar: {dataset.shape}")

        # Štandardizácia datasetu
        dataset = standardize_column_names(dataset)
        dataset = standardize_label_column(dataset)

        # Čistenie datasetu
        dataset = clean_dataframe(
            dataset,
            drop_na=drop_na,
            drop_inf=drop_inf,
            drop_duplicates=drop_duplicates
        )

        return dataset

    except Exception as e:
        logger.error(f"Chyba pri načítavaní datasetu: {e}")
        raise DatasetLoadError(
            f"Chyba pri načítavaní datasetu z '{directory_path}': {e}"
        ) from e


def preprocess_IDS2017_dataset(dataset: DataFrame) -> DataFrame:
    """
    Spracuje načítaný CIC-IDS2017 dataset pre analýzu útokov hrubou silou.

    Táto funkcia filtruje dataset na najdôležitejšie stĺpce pre detekciu útokov
    hrubou silou a vyberá reprezentatívne vzorky pre ďalšiu analýzu.

    Proces spracovania:
        1. Filtrovanie na 12 najdôležitejších stĺpcoch pre detekciu útokov
        2. Výber 100 BENIGN vzoriek (normálna sieťová aktivita)
        3. Výber 100 SSH-Patator vzoriek (útoky hrubou silou)
        4. Spojenie vzoriek do výsledného datasetu

    Parametre:
        dataset (DataFrame): Načítaný a vyčistený CIC-IDS2017 dataset

    Vyvoláva:
        DatasetLoadError: Ak sa vyskytne chyba pri spracovaní datasetu

    Návratová hodnota:
        DataFrame: Spracovaný dataset obsahujúci:
            - 12 vybraných stĺpcov relevantných pre detekciu útokov
            - Maximálne 200 reprezentatívnych vzoriek (100 BENIGN + 100 SSH-Patator)
            - Štandardizované štítky a názvy stĺpcov
    """
    logger.info("Spúšťa sa analýza IDS2017 datasetu...")

    # Definícia kľúčových stĺpcov pre detekciu útokov hrubou silou
    # Tieto stĺpce boli vybrané na základe ich relevantnosti pre útoky
    # podľa predchádzajúcej analýzy a literatúry.
    important_columns = [
        "Destination_Port",        # Cieľový port
        "Flow_Duration",           # Trvanie komunikácie
        "Total_Fwd_Packets",       # Počet odoslaných paketov
        "Total_Backward_Packets",  # Počet prijatých paketov
        "Flow_Bytes/s",            # Intenzita toku v bytoch za sekundu
        "Flow_Packets/s",         # Intenzita toku v paketoch za sekundu
        "Fwd_Packet_Length_Mean",  # Priemerná dĺžka odoslaných paketov
        "Bwd_Packet_Length_Mean",  # Priemerná dĺžka prijatých paketov
        "SYN_Flag_Count",         # Počet SYN flagov (nadväzovanie spojenia)
        "ACK_Flag_Count",         # Počet ACK flagov (potvrdenia)
        "Init_Win_bytes_forward",  # Veľkosť initial window
        "Label"                   # Klasifikáačný štítok
    ]

    # Filtrovanie datasetu na vybrané dôležité stĺpce
    try:
        filtered_dataset = filter_important_columns(dataset, important_columns)
        logger.info("Dataset úspešne filtrovaný")

        # Výber reprezentatívnych vzoriek pre efektívnu analýzu
        # 100 BENIGN vzoriek - normálna sieťová aktivita
        benign_samples = filtered_dataset[
            filtered_dataset["Label"] == "BENIGN"
        ].head(100)

        # 100 SSH-Patator vzoriek - útoky na SSH
        ssh_patator_samples = filtered_dataset[
            filtered_dataset["Label"] == "SSH-Patator"
        ].head(100)

        # Spojenie vzoriek do jedného datasetu pre analýzu
        filtered_dataset = pd.concat(
            [benign_samples, ssh_patator_samples], ignore_index=True
        )

    except Exception as e:
        logger.error(f"Chyba pri spracovaní datasetu: {e}")
        raise DatasetLoadError(
            f"Chyba pri spracovaní IDS2017 datasetu: {e}"
        ) from e

    logger.info(
        f"Vybrané vzorky: {len(benign_samples)} BENIGN, "
        f"{len(ssh_patator_samples)} SSH-Patator"
    )

    return filtered_dataset


def get_IDS2017_label(frame: pd.DataFrame) -> bool:
    """
    Určuje, či záznam v datasete IDS2017 je škodlivý alebo neškodný.

    Parametre:
        frame (pd.DataFrame): DataFrame obsahujúci aspoň jeden riadok s posledným
                             stĺpcom ako štítkom

    Návratová hodnota:
        bool: True ak je záznam označený ako "SSH-Patator", inak False

    Poznámka:
        Funkcia kontroluje len prvý riadok DataFrame a konkrétne hľadá
        štítok "SSH-Patator" v poslednom stĺpci.
    """
    label = frame.iloc[0, -1]
    if label == "SSH-Patator":
        malicious = True
    else:
        malicious = False

    return malicious


def unlabel_IDS2017_dataset(
    dataset: pd.DataFrame, label_column: str = 'Label'
) -> pd.DataFrame:
    """
    Odstráni klasifikačný stĺpec so štítkom z datasetu.

    Táto funkcia bezpečne odstráni zadaný stĺpec z DataFrame. Je užitočná pri
    príprave dát pre analýzu, kde potrebujeme odstrániť klasifikačný štítok alebo
    iné nepotrebné stĺpce. Funkcia kontroluje existenciu stĺpca pred odstránením.

    Parametre:
        dataset (pd.DataFrame): Dataset na úpravu. Musí byť platný DataFrame.
        label_column (str, optional): Názov stĺpca na odstránenie.
                                     Predvolená hodnota je 'Label'.

    Návratová hodnota:
        pd.DataFrame: Dataset bez klasifikačného stĺpca. Ak stĺpec neexistuje,
                      vracia pôvodný dataset bez zmien.

    Poznámka:
        Táto funkcia nevyvoláva výnimky, ak stĺpec neexistuje, ale vypíše
        upozornenie do logu. Je vhodná pre prípady, keď nie je isté, či
        stĺpec existuje v každom datasete.
    """
    # Kontrola existencie stĺpca pred odstránením
    if label_column in dataset.columns:
        # Vytvorenie kópie datasetu bez zadaného stĺpca
        return dataset.drop(columns=[label_column])
    else:
        # Ak stĺpec neexistuje, vrátime pôvodný dataset
        logger.warning(f"Upozornenie: Stĺpec '{label_column}' nebol nájdený")
        return dataset


def load_and_preprocess_ids2017_dataset(
        directory_path: Path,
        selected_files: Optional[List[str]] = None,
        drop_na: bool = True,
        drop_inf: bool = True,
        drop_duplicates: bool = True) -> pd.DataFrame:
    """
    Načíta a predspracuje IDS 2017 dataset v jednom kroku.

    Táto funkcia kombinuje načítanie datasetu a jeho predspracovanie
    pre analýzu útokov hrubou silou. Poskytuje kompletné riešenie
    od načítania CSV súborov až po prípravu datasetu pre analýzu.

    Parametre:
        directory_path (Path): Cesta k adresáru obsahujúcemu CSV súbory
        selected_files (Optional[List[str]]): Konkrétne súbory na načítanie.
            Ak je None, načítajú sa všetky CSV súbory z adresára.
            Predvolené: None
        drop_na (bool): Či odstrániť riadky obsahujúce NaN hodnoty.
            Predvolené: True
        drop_inf (bool): Či odstrániť riadky obsahujúce nekonečné hodnoty.
            Predvolené: True
        drop_duplicates (bool): Či odstrániť duplicitné riadky.
            Predvolené: True

    Návratová hodnota:
        pd.DataFrame: Načítaný a predspracovaný dataset pripravený na analýzu

    Vyvoláva:
        DatasetLoadError: Ak sa vyskytne chyba pri načítaní alebo spracovaní datasetu
    """
    try:
        # Načítanie datasetu
        logger.info("Načítavam IDS2017 dataset...")
        dataset = load_ids2017_dataset(
            directory_path=directory_path,
            selected_files=selected_files,
            drop_na=drop_na,
            drop_inf=drop_inf,
            drop_duplicates=drop_duplicates
        )

        # Predspracovanie datasetu
        logger.info("Predspracovávam dataset...")
        preprocessed_dataset = preprocess_IDS2017_dataset(dataset)

        logger.info("Dataset úspešne načítaný a predspracovaný")
        return preprocessed_dataset

    except Exception as e:
        logger.error(f"Chyba pri načítaní a predspracovaní datasetu: {e}")
        raise DatasetLoadError(
            f"Chyba pri načítaní a predspracovaní datasetu z '{directory_path}': {e}"
        ) from e
