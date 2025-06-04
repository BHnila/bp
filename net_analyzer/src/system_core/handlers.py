"""
Modul pre spracovanie chýb a obnovu po zlyhaniach.
Funkcie pre spracovanie chýb vyvolávajú špecifické výnimky namiesto
ukončenia programu, zatiaľ čo funkcie pre obnovu poskytujú bezpečné
predvolené hodnoty.
"""

import logging

from src.system_core.data_models import (
    LogsMetadata,
    LogsDescription,
    LogsAnalysisResult,
    FlowAnalysisResult
)
from src.system_core.exceptions import (
    ApiClientInitializationError,
    MissingApiKeyError,
    EnvFileNotFoundError
)

# Inicializácia logovacieho systému
logger = logging.getLogger(__name__)


def handle_dotenv_error(error: Exception) -> None:
    """
    Spracuje chyby pri načítaní .env súboru a vyvolá EnvFileNotFoundError.

    Táto funkcia zobrazí používateľovi informatívnu chybovú správu
    o probléme. Následne vyvolá EnvFileNotFoundError výnimku.

    Parametre:
        error (Exception): Výnimka zachytená pri načítaní .env súboru

    Vyvoláva:
        EnvFileNotFoundError: Keď .env súbor nie je nájdený
    """
    # Vytvorí informačnú chybovú správu pre používateľa
    error_msg = (
        f"Chyba pri načítaní .env súboru: {error}\n"
        "Uistite sa, že .env súbor existuje a obsahuje OPENAI_API_KEY."
    )
    # Zobrazí chybovú správu
    logger.error(error_msg)
    # Vyvolá výnimku pre chýbajúci .env súbor
    raise EnvFileNotFoundError()


def handle_missing_api_key() -> None:
    """
    Spracuje chybu chýbajúceho OPENAI_API_KEY a vyvolá MissingApiKeyError.

    Táto funkcia sa volá, keď nie je možné načítať OPENAI_API_KEY
    z premenných prostredia. Zobrazí používateľovi informatívnu správu
    a vyvolá MissingApiKeyError výnimku.

    Vyvoláva:
        MissingApiKeyError: Keď API kľúč nie je nájdený alebo je neplatný
    """
    # Vytvorí informačnú chybovú správu o chýbajúcom API kľúči
    error_msg = (
        "Chyba: OPENAI_API_KEY nebol nájdený\n"
        "Uistite sa, že .env súbor obsahuje platný kľúč."
    )
    # Zobrazí chybovú správu
    logger.error(error_msg)
    # Vyvolá výnimku pre chýbajúci API kľúč
    raise MissingApiKeyError()


def handle_client_creation_error(
    client_name: str, error: Exception, ollama_base_url: str
) -> None:
    """
    Spracuje chyby pri vytváraní LLM klientov a vyvolá
    ApiClientInitializationError.

    Táto univerzálna funkcia spracováva rôzne typy chýb, ktoré môžu
    nastať pri vytváraní klientov pre OpenAI alebo Ollama API.
    Pre Ollama klientov pridáva špecifické pokyny na kontrolu servera.

    Parametre:
        client_name (str): Názov klienta/modelu, pre ktorý nastala chyba
        error (Exception): Výnimka zachytená pri vytváraní klienta
        ollama_base_url (str): URL adresa Ollama servera pre diagnostiku

    Vyvoláva:
        ApiClientInitializationError: Keď sa nepodarí inicializovať API klient
    """
    # Vytvorí základnú chybovú správu s názvom klienta a popisom chyby
    error_msg = f"Chyba pri vytváraní {client_name} klienta: {error}"

    # Pre Ollama klientov pridá špecifické pokyny na riešenie problému
    if "Ollama" in client_name:
        error_msg += (
            f"\nSkontrolujte, či je Ollama server spustený a dostupný "
            f"na {ollama_base_url}."
        )

    # Zobrazí kompletnú chybovú správu
    logger.error(error_msg)
    # Vyvolá výnimku pre zlyhanie inicializácie API klienta
    raise ApiClientInitializationError()


def handle_metadata_extractor_agent_failure() -> LogsMetadata:
    """
    Obnova chodu aplikácie po zlyhaní Extraktora metadát.

    Táto funkcia sa volá, keď zlyhá agent zodpovedný za extrahovanie
    metadát z log súborov. Namiesto ukončenia programu poskytne
    predvolené bezpečné hodnoty, ktoré umožnia pokračovať v analýze.

    Návratová hodnota:
        LogsMetadata: Predvolený objekt s metadátami obsahujúci:
            - duration: "None" (neurčená doba trvania)
            - attacker: "None" (neurčený útočník)
            - service: "Other" (neidentifikovaná služba)

    Poznámka:
        Predvolené hodnoty ovplyvnia výsledky analýzy.
        Táto funkcia informuje používateľa o zlyhaní.
    """
    # Upozornenie používateľa o zlyhaní Extraktora metadát
    logger.warning("Extraktor metadát zlyhal, použili sa predvolené hodnoty.")
    # Vráti predvolený objekt metadát v prípade zlyhania
    return LogsMetadata(
        duration="None",
        attacker="None",
        service="Other"
    )


def handle_logs_descriptor_agent_failure() -> LogsDescription:
    """
    Obnova chodu aplikácie po zlyhaní Popisovača logov.

    Táto funkcia sa volá, keď zlyhá agent zodpovedný za popis
    a identifikáciu aktivít obsiahnutých v log súboroch. Poskytne
    predvolenú správu označujúcu zlyhanie extrakcie vzoru.

    Návratová hodnota:
        LogsDescription: Predvolený objekt s popisom obsahujúci:
            - description: Správa o zlyhaní extrakcie vzoru aktivít

    Poznámka:
        Táto funkcia zabezpečuje, že program môže pokračovať aj pri
        zlyhaní analýzy aktivít, pričom jasne označí problém. Výsledky
        analýzy logov môžu byť ovplyvnené absenciou popisu aktivít.
    """
    # Upozornenie používateľa o zlyhaní Popisovača logov
    logger.warning("Popisovač logov zlyhal, použili sa predvolené hodnoty.")
    # Vráti predvolený objekt s informáciou o zlyhaní extrakcie vzoru
    return LogsDescription(description="Failed to extract pattern.")


def handle_logs_classifier_agent_failure() -> LogsAnalysisResult:
    """
    Obnova chodu aplikácie po zlyhaní Klasifikačného agenta pre logy.

    Táto funkcia sa volá, keď zlyhá agent zodpovedný za klasifikáciu
    log súborov a identifikáciu bezpečnostných hrozieb. Poskytne
    predvolenú bezpečnú klasifikáciu, ktorá označuje logy ako neškodné.

    Návratová hodnota:
        LogsAnalysisResult: Predvolený objekt s výsledkom analýzy obsahujúci:
            - bruteforce: False (žiadny brute force útok)
            - system_compromised: False (systém nie je kompromitovaný)
            - reason: Správa o zlyhaní analýzy s použitím bezpečnej
              klasifikácie

    Poznámka:
        Bezpečná predvolená klasifikácia minimalizuje riziko falošných
        pozitívnych výsledkov, ale môže viesť k falošne negatívnym výsledkom.
        V prípade zlyhania klasifikátora treba postupovať opatrne,
        pretože môže dôjsť k prehliadnutiu skutočných hrozieb.
    """
    # Upozornenie používateľa o zlyhaní Klasifikačného agenta pre logy
    logger.warning("Klasifikátor logov zlyhal, použili sa predvolené hodnoty.")
    # Vráti predvolenú bezpečnú klasifikáciu v prípade zlyhania
    return LogsAnalysisResult(
        bruteforce=False,
        system_compromised=False,
        reason="Failed to analyze logs - using default safe classification."
    )


def handle_flow_classifier_agent_failure() -> FlowAnalysisResult:
    """
    Obnova chodu aplikácie po zlyhaní Klasifikačného agenta pre sieťové toky.

    Táto funkcia sa volá, keď zlyhá agent zodpovedný za analýzu
    a klasifikáciu sieťových tokov pre identifikáciu útokov.
    Poskytne predvolenú bezpečnú klasifikáciu bez detekcie hrozieb, ktorá
    označí vstupné dáta ako neškodné.

    Návratová hodnota:
        FlowAnalysisResult: Predvolený objekt s výsledkom analýzy obsahujúci:
            - bruteforce: False (žiadny brute force útok v sieťových tokoch)
            - reason: Správa o zlyhaní analýzy s použitím bezpečnej
              klasifikácie

    Poznámka:
        Podobne ako pri analýze logov, bezpečná predvolená klasifikácia
        preferuje falošne negatívne výsledky pred falošne pozitívnymi.
        V prípade zlyhania klasifikátora je dôležité byť opatrný, pretože
        môže dôjsť k prehliadnutiu skutočných hrozieb v sieťových tokoch.
    """
    # Upozornenie používateľa o zlyhaní Klasifikačného agenta pre sieťové toky
    logger.warning(
        "Klasifikátor sieťových tokov zlyhal, použili sa predvolené hodnoty."
    )
    # Vráti predvolenú bezpečnú klasifikáciu pre sieťové toky
    # v prípade zlyhania
    return FlowAnalysisResult(
        bruteforce=False,
        reason="Failed to analyze flow - using default safe classification."
    )
