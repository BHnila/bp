"""
Pomocné funkcie pre llm balík.
"""

import logging
import time
from typing import Tuple, Any, Callable
from functools import wraps
from langchain.schema.runnable import Runnable

from src.system_core.data_models import LogsMetadata, LogsDescription
from src.system_core.exceptions import AgentInitializationError

# Nastavenie loggera pre tento modul
logger = logging.getLogger(__name__)

# Konfigurácia pre robustnosť
# Maximálny počet opakovaní pri zlyhaní agenta
MAX_RETRIES = 2
# Časový interval medzi opakovanými pokusmi v sekundách
RETRY_DELAY = 2.0


def validate_input_data(data: str) -> Tuple[bool, str]:
    """
    Validuje vstupné dáta pre analýzu logov a sieťových tokov.

    Funkcia overuje základné požiadavky na vstupné dáta ako ich
    prítomnosť a typ.

    Parametre:
        data (str): Vstupné dáta na validáciu (logy alebo sieťové toky)

    Návratová hodnota:
        Tuple[bool, str]: Tuple obsahujúci:
            - bool: True ak sú dáta validné, inak False
            - str: Chybová správa ak sú dáta nevalidné, inak prázdny reťazec
    """
    # Kontrola typu vstupných dát
    if not isinstance(data, str):
        return False, "Vstupné dáta musia byť inštancia string"

    # Kontrola prázdneho reťazca
    if not data or not data.strip():
        return False, "Vstupné dáta nesmú byť prázdne"

    # Ak dáta prešli všetkými kontrolami, sú validné
    return True, ""


def safe_agent_invoke(agent: Runnable, input_data: dict, operation_name: str,
                      recovery_function: Callable) -> Any:
    """
    Robustným spôsobom vyvolá LLM agenta.

    Táto funkcia zabezpečuje spoľahlivú komunikáciu s LLM agentmi pomocou
    robustného mechanizmu obnovy v prípade chyby.

    Parametre:
        agent (Runnable): AI agent objekt s invoke() metódou
        input_data (dict): Vstupné dáta pre agenta vo forme slovníka
        operation_name (str): Popisný názov operácie pre účely loggingu
        recovery_function (Callable): Funkcia volaná pri chybe agenta

    Návratová hodnota:
        Any: Výsledok úspešného vyvolania agenta alebo recovery funkcie
    """
    try:
        # Logovanie začiatku operácie
        logger.info(f"Spúšťam {operation_name}...")

        # Vyvolanie agenta s vstupnými dátami
        result = agent.invoke(input_data)

        # Logovanie úspechu
        logger.info(f"{operation_name} úspešne dokončená")
        # Vrátenie výsledku agenta
        return result

    except Exception as e:
        # Logovanie chyby a spustenie mechanizmu obnovy
        logger.error(f"Chyba pri {operation_name}: {e}")
        logger.info(f"Používam mechanizmus obnovy pre {operation_name}")
        return recovery_function()


def preprocess_metadata(metadata: LogsMetadata) -> str:
    """
    Úpraví výstup Extraktora metadát do formy vhodnej pre
    Klasifikačného agenta.

    Serializuje LogsMetadata objekt.

    Parametre:
        metadata (LogsMetadata): Metadáta extrahované z logov

    Návratová hodnota:
        str: JSON reťazec s escapovanými zátvorkami pre LangChain
    """
    # Serializácia metadát do JSON formátu s úpravou pre LangChain
    return metadata.model_dump_json().replace('{', '{{').replace("}", "}}")


def preprocess_description(description: LogsDescription) -> str:
    """
    Úpraví výstup Popisovača logov do formy vhodnej pre
    Klasifikačného agenta.

    Serializuje LogsDescription objekt.

    Parametre:
        description (LogsDescription): Aktivita a vzory extrahované z logov

    Návratová hodnota:
        str: JSON reťazec s escapovanými zátvorkami
    """
    # Serializácia opisu do JSON formátu s úpravou pre LangChain
    return description.model_dump_json().replace('{', '{{').replace("}", "}}")


def retry_on_failure(max_retries: int = MAX_RETRIES,
                     delay: float = RETRY_DELAY) -> Callable:
    """
    Dekorátor pre automatické opakovanie neúspešných operácií.

    Implementuje stratégiu pre zotavenie sa z dočasných chýb.
    Užitočné pre API volania a nestabilné sieťové operácie.

    Parametre:
        max_retries (int): Maximálny počet pokusov
        delay (float): Základné čakanie medzi pokusmi v sekundách

    Návratová hodnota:
        Callable: Dekorovanú funkciu

    Vyvolá:
        AgentInitializationError: Ak všetky pokusy zlyhajú
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:

            # Vykonávaj opakované pokusy
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:

                    # Ak nie je posledný pokus, čakaj a opakuj
                    if attempt < max_retries:
                        logger.warning(
                            f"Pokus {attempt + 1}/{max_retries + 1} pre "
                            f"{func.__name__} neúspešný: {e}. "
                            f"Opakujem za {delay}s..."
                        )
                        time.sleep(delay)
                    else:
                        # Všetky pokusy vyčerpané
                        logger.error(
                            f"Všetky pokusy pre {func.__name__} neúspešné. "
                            f"Posledná chyba: {e}"
                        )

            # Ak všetky pokusy zlyhali, vyvolaj špecializovanú výnimku
            raise AgentInitializationError()

        return wrapper
    return decorator
