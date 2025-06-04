"""
Tento modul obsahuje toky pre detekciu útokov hrubou silou.
"""

import logging
import time

from src.llm.agents import (
    spawn_logs_classifier_agent,
    spawn_logs_metadata_extractor_agent,
    spawn_logs_descriptor_agent,
    spawn_flow_classifier_agent
)
from src.llm.utils import (
    validate_input_data,
    safe_agent_invoke,
    preprocess_metadata,
    preprocess_description,
    retry_on_failure
)
from src.system_core.handlers import (
    handle_metadata_extractor_agent_failure,
    handle_logs_descriptor_agent_failure,
    handle_logs_classifier_agent_failure,
    handle_flow_classifier_agent_failure
)
from src.system_core.data_models import LogsAnalysisResult, FlowAnalysisResult
from src.llm.api_clients import (
    spawn_secllama_client,
    spawn_brutellama_client,
    spawn_llama3_client
)

# Nastavenie loggingu
logger = logging.getLogger(__name__)


@retry_on_failure(max_retries=2)
def detect_brute_force_in_logs(logs_to_process: str,
                               num_epochs: int) -> LogsAnalysisResult:
    """
    Detekuje útoky hrubou silou v logových súboroch. Implementuje metódu
    analýzy logov (kapitola 2.1).

    Táto funkcia orchestruje celý proces analýzy logov pomocou AI agentov:
    1. validuje vstupné dáta,
    2. inicializuje LLM API klientov,
    3. inicializuje LLM agentov,
    4. extrahuje metadáta z logov,
    5. popíše aktivitu v logoch,
    6. spracuje čiastočnné výstupy z krokov 4 a 5,
    7. klasifikuje, či došlo k útoku hrubou silou.

    Parametre:
        logs_to_process (str): Logové záznamy na analýzu
        num_epochs (int): Počet epoch ladenia LLM pre bruteLlama3B

    Návratová hodnota:
        LogsAnalysisResult: Výsledok klasifikácie s indikátormi útoku
    """
    # Spustenie časomiery
    start_time = time.time()
    logger.info("Inicializujem detekciu brute force útokov v logoch...")

    # Validácia vstupných dát
    validation_result, validation_reason = validate_input_data(logs_to_process)
    if not validation_result:
        logger.error(f"Neplatné vstupné logy: {validation_reason}")
        return handle_logs_classifier_agent_failure()
    logger.info("Vstupné logy sú validné.")

    # Inicializácia LLM klientov
    if num_epochs > 0:
        llm_client = spawn_brutellama_client(num_epochs)
    else:
        llm_client = spawn_llama3_client()
    logger.info("LLM klient úspešne inicializovaný")

    # Inicializácia LLM agentov
    metadata_extractor_agent = spawn_logs_metadata_extractor_agent(
        llm_client)
    logs_descriptor_agent = spawn_logs_descriptor_agent(llm_client)
    logs_classifier_agent = spawn_logs_classifier_agent(llm_client)
    logger.info("LLM agenti úspešne inicializovaní")

    # Vyvolanie Extrahovača metadát
    metadata = safe_agent_invoke(
        metadata_extractor_agent,
        {"input": logs_to_process},
        "extrahovanie metadát",
        handle_metadata_extractor_agent_failure
    )
    logger.info(f"Extrahované metadáta: {metadata}")

    # Vyvolanie Popisovača logov
    description = safe_agent_invoke(
        logs_descriptor_agent,
        {"input": logs_to_process},
        "popisovanie logov",
        handle_logs_descriptor_agent_failure
    )
    logger.info(f"Popis logov: {description.description}")

    # Klasifikácia logov
    try:
        # Predspracovanie metadát a popisu pre Klasifikačného agenta
        preprocessed_metadata = preprocess_metadata(metadata)
        preprocessed_description = preprocess_description(description)

        # Vyvolanie Klasifikačného agenta
        classification_result = safe_agent_invoke(
            logs_classifier_agent,
            {
                "logs": logs_to_process,
                "logs_metadata": preprocessed_metadata,
                "logs_description": preprocessed_description
            },
            "klasifikácia výsledkov",
            handle_logs_classifier_agent_failure
        )

        # Zaznamenanie času spracovania
        end_time = time.time()
        processing_time = end_time - start_time
        logger.info(f"Analýza dokončená za {processing_time:.2f} sekúnd")
        logger.info(f"Výsledok: {classification_result}")

        return classification_result

    except Exception as e:
        logger.error(f"Neočakávaná chyba počas klasifikácie: {e}")
        # Vrátenie predvoleného bezpečného výsledku v prípade chyby
        return handle_logs_classifier_agent_failure()


@retry_on_failure(max_retries=2)
def detect_brute_force_in_flow(flow_to_process: str,
                               num_epochs: int) -> FlowAnalysisResult:
    """
    Detekuje útoky hrubou silou v tokoch paketov. Implementuje metódu
    analýzy tokov paketov (kapitola 2.1).

    Táto funkcia orchestruje celý proces analýzy tokov paketov pomocou jedného
    AI agenta:
    1. validuje vstupné dáta,
    2. klasifikuje, či došlo k útoku hrubou silou.

    Parametre:
        flow_to_process (str): Toky paketov na analýzu
        num_epochs (int): Počet epoch ladenia LLM pre secLlama3B

    Návratová hodnota:
        FlowAnalysisResult: Výsledok klasifikácie s indikátormi útoku
    """
    # Spustenie časomiery
    start_time = time.time()
    logger.info("Inicializujem detekciu brute force útokov v tokoch paketov...")

    # Validácia vstupných dát
    validation_result, validation_reason = validate_input_data(flow_to_process)
    if not validation_result:
        logger.error(f"Neplatné vstupné dáta: {validation_reason}")
        return handle_flow_classifier_agent_failure()
    logger.info("Vstupné dáta sú validné.")

    # Inicializácia LLM klienta
    if num_epochs > 0:
        llm_client = spawn_secllama_client(num_epochs)
    else:
        llm_client = spawn_llama3_client()
    logger.info("LLM klient pre flow analýzu úspešne inicializovaný")

    # Inicializácia LLM agenta
    netflow_classifier_agent = spawn_flow_classifier_agent(llm_client)
    logger.info("Klasifikačný agent úspešne inicializovaný")

    try:
        # Vyvolanie Klasifikačného agenta
        classification_result = safe_agent_invoke(
            netflow_classifier_agent,
            {"flow_data": flow_to_process},
            "klasifikácia toku paketov",
            handle_flow_classifier_agent_failure
        )

        # Zaznamenanie času spracovania
        end_time = time.time()
        processing_time = end_time - start_time
        logger.info(
            f"Analýza toku paketov dokončená za {processing_time:.2f} sekúnd"
        )
        logger.info(f"Výsledok: {classification_result}")

        return classification_result

    except Exception as e:
        logger.error(f"Neočakávaná chyba počas klasifikácie: {e}")
        # Vrátenie predvoleného bezpečného výsledku v prípade chyby
        return handle_flow_classifier_agent_failure()
