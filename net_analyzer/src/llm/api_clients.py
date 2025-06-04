"""
Tento modul obsahuje funkcie pre vytvorenie klientov pre
rôzne LLM API rozhrania.
"""

import os
import logging
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from src.system_core.handlers import (
    handle_dotenv_error,
    handle_missing_api_key,
    handle_client_creation_error
)
from src.llm.utils import retry_on_failure

# Konštanty pre konfiguráciu Ollama klientov/modelov
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_NUM_CTX = 8000
DEFAULT_TEMPERATURE = 0.2
DEFAULT_NUM_PREDICT = 4096
DEFAULT_TOP_K = 10
DEFAULT_TOP_P = 0.5

# Nastavenie loggingu
logger = logging.getLogger(__name__)


@retry_on_failure()
def spawn_openai_client() -> ChatOpenAI:
    """
    Vytvorí a vráti ChatOpenAI klienta pre GPT-4.1-mini API.

    Návratová hodnota:
        ChatOpenAI: Nakonfigurovaný OpenAI chat klient pre model GPT-4.1-mini

    Poznámka:
        Vyžaduje premennú OPENAI_API_KEY nastavenú v .env súbore.
    """
    # Načítanie premenných prostredia z .env súboru
    try:
        load_dotenv()
    except Exception as e:
        handle_dotenv_error(e)

    # Kontrola existencie API kľúča
    if not os.getenv("OPENAI_API_KEY"):
        handle_missing_api_key()

    # Vytvorenie a vrátenie OpenAI klienta
    try:
        return ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=DEFAULT_TEMPERATURE,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    except Exception as e:
        handle_client_creation_error("OpenAI", e, OLLAMA_BASE_URL)


@retry_on_failure()
def spawn_secllama_client(num_epochs: int) -> ChatOllama:
    """
    Vytvorí a vráti ChatOllama klienta nakonfigurovaného pre secLlama3B model.

    Táto funkcia inicializuje ChatOllama klienta so špecifickými parametrami
    optimalizovanými pre secLlama3B model bežiaci na Ollama serveri.
    Konfigurácia zahŕňa veľkosť kontextového okna, nastavenia teploty
    a limity predikcií.

    Parametre:
        num_epochs (int): Počet epoch ladenia modelu

    Návratová hodnota:
        ChatOllama: Nakonfigurovaný ChatOllama klient pripojený k secLlama3B
    """
    # Vytvorenie a vrátenie secLlama3B klienta s konfiguráciou pre zadaný počet epoch
    try:
        return ChatOllama(
            model=f"secLlama3B_{num_epochs}ep_Q4_K_M.gguf:latest",
            num_ctx=DEFAULT_NUM_CTX,
            temperature=DEFAULT_TEMPERATURE,
            num_predict=DEFAULT_NUM_PREDICT,
            top_k=DEFAULT_TOP_K,
            top_p=DEFAULT_TOP_P,
            base_url=OLLAMA_BASE_URL
        )
    except Exception as e:
        handle_client_creation_error("secLlama3B Ollama", e, OLLAMA_BASE_URL)


@retry_on_failure()
def spawn_brutellama_client(num_epochs: int) -> ChatOllama:
    """
    Vytvorí a vráti ChatOllama klienta nakonfigurovaného pre bruteLlama3B model.

    Táto funkcia inicializuje ChatOllama klienta so špecifickými parametrami
    optimalizovanými pre bruteLlama3B model bežiaci na Ollama serveri.
    Konfigurácia zahŕňa veľkosť kontextového okna, nastavenia teploty
    a limity predikcií.

    Parametre:
        num_epochs (int): Počet epoch ladenia modelu

    Návratová hodnota:
        ChatOllama: Nakonfigurovaný ChatOllama klient pripojený k bruteLlama3B
    """
    # Vytvorenie a vrátenie bruteLlama3B klienta s konfiguráciou pre zadaný počet epoch
    try:
        return ChatOllama(
            model=f"bruteLlama3B_{num_epochs}ep_Q4_K_M.gguf:latest",
            num_ctx=DEFAULT_NUM_CTX,
            temperature=DEFAULT_TEMPERATURE,
            num_predict=DEFAULT_NUM_PREDICT,
            top_k=DEFAULT_TOP_K,
            top_p=DEFAULT_TOP_P,
            base_url=OLLAMA_BASE_URL
        )
    except Exception as e:
        handle_client_creation_error("bruteLlama3B Ollama", e, OLLAMA_BASE_URL)


@retry_on_failure()
def spawn_llama3_client() -> ChatOllama:
    """
    Vytvorí a vráti ChatOllama klienta nakonfigurovaného pre Llama 3.2:3b model.

    Táto funkcia inicializuje ChatOllama klienta so špecifickými parametrami
    optimalizovanými pre Llama 3.2 3B model bežiaci na Ollama serveri.
    Konfigurácia zahŕňa veľkosť kontextového okna, nastavenia teploty
    a limity predikcií.

    Návratová hodnota:
        ChatOllama: Nakonfigurovaný ChatOllama klient pripojený k llama3.2:3b
    """
    # Vytvorenie a vrátenie Llama 3.2 klienta
    try:
        return ChatOllama(
            model="llama3.2:3b",
            num_ctx=DEFAULT_NUM_CTX,
            temperature=DEFAULT_TEMPERATURE,
            num_predict=DEFAULT_NUM_PREDICT,
            top_k=DEFAULT_TOP_K,
            top_p=DEFAULT_TOP_P,
            base_url=OLLAMA_BASE_URL
        )
    except Exception as e:
        handle_client_creation_error("Llama 3.2 Ollama", e, OLLAMA_BASE_URL)
