"""
Tento modul definuje dátové modely používané v aplikácii.
"""

from pydantic import BaseModel
from typing import Literal


class LogsMetadata(BaseModel):
    """
    Dátový model pre metadáta logov.

    Je využívaný ako štruktúrovaný výstup Extraktora metadát
    (logs_metadata_extractor_agent).

    Obsahuje základné informácie o analyzovaných logoch - doba trvania
    útoku, IP adresa útočníka a typ služby.
    """
    # Doba trvania útoku (napr. "5 minút", "2 hodiny")
    duration: str
    # IP adresa alebo identifikátor útočníka
    attacker: str
    # Typ služby pod útokom
    service: Literal['SSH', 'telnet', 'SMB', 'Other']


class LogsDescription(BaseModel):
    """
    Dátový model pre popis logov.

    Je využívaný ako štruktúrovaný výstup Popisovača logov
    (logs_descriptor_agent).

    Zachytáva špecifickú aktivitu detekovanú v log súboroch.
    """
    # Popis detekovanej aktivity
    description: str


class FlowAnalysisResult(BaseModel):
    """
    Dátový model pre výsledok analýzy tokov paketov.

    Je využívaný ako štruktúrovaný výstup Klasifikačného agenta
    (flow_classifier_agent).

    Obsahuje informácie o prítomnosti útoku hrubou silou a
    zdôvodnenie svojho rozhodnutia.
    """
    bruteforce: bool  # True ak bol detekovaný útok hrubou silou
    reason: str  # Zdôvodnenie rozhodnutia


class LogsAnalysisResult(BaseModel):
    """
    Dátový model pre komplexný výsledok analýzy logov.

    Je využívaný ako štruktúrovaný výstup Klasifikačného agenta
    (logs_classifier_agent).

    Obsahuje informácie o prítomnosti útoku hrubou silou,
    či bola narušená integrita systému a zdôvodnenie svojho
    rozhodnutia.
    """
    bruteforce: bool  # True ak bol detekovaný útok hrubou silou
    system_compromised: bool  # True ak bol systém kompromitovaný
    reason: str = None  # Zdôvodnenie rozhodnutia


class AnalysisState(BaseModel):
    """
    Dátový model reprezentujúci stav behu programu.

    Obsahuje veličiny matice konfúzie a vypočítané metriky
    využívané pri hodnotení úspešnosti detekcie
    (kapitola 1.8).
    """
    # Celkový počet pozitívnych prípadov
    positives: int = 0
    # Detekované skutočne pozitívne prípady
    detected_real_positives: int = 0
    # Detekované falošne pozitívne prípady
    detected_false_positives: int = 0
    # Detekované falošne negatívne prípady
    detected_false_negatives: int = 0

    # Metriky úspešnosti
    # Presnosť
    precision: float = 0.0
    # Citlivosť
    recall: float = 0.0
    # F1 skóre
    f1_score: float = 0.0
