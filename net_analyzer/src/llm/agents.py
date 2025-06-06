"""Tento modul obsahuje definície LLM agentov pre analýzu logov a tokov
paketov. Agenti používajú LangChain na spracovanie a analýzu údajov.
Agenti sú bližšie popísaní v kapitole 3.2
Pre konfiguráciu robustnosti pozrite src/llm/utils.py.
"""

import logging

from langchain_core.prompts import PromptTemplate
from langchain.schema.runnable import Runnable
from langchain_core.language_models.chat_models import BaseChatModel
from src.system_core.data_models import (
    FlowAnalysisResult,
    LogsDescription,
    LogsAnalysisResult,
    LogsMetadata,
)
from src.llm.utils import retry_on_failure

# Nastavenie loggingu
logger = logging.getLogger(__name__)


@retry_on_failure(max_retries=2)
def spawn_logs_metadata_extractor_agent(llm_client: BaseChatModel) -> Runnable:
    """
    Vytvorí nakonfigurovanú inštanciu agenta pre extrahovanie metadát
    z logov.

    Ide o implenetáciu Extraktora metadát (kapitola 3.2.2).

    Tento agent analyzuje linuxové logy a extrahuje z nich metadáta -
    službu, IP adresu útočníka a trvanie podozrivej aktivity.

    Parametre:
        llm_client (BaseChatModel): LLM tvoriaci základ agenta

    Návratová hodnota:
        Runnable: Nakonfigurovaný agent pre extrahovanie metadát

    Štruktúrovaný výstup:
        LogsMetadata - obsahuje polia 'service' (string), 'attacker' (string)
        a 'duration' (string) s metadátami extrahovanými z logov
    """
    # Šablóna pre systémovú inštrukciu agenta
    template = """
        You are **Metadata-Extractor**, an AI agent that turns a batch of
        Linux logs into a single metadata record.

        ## YOUR INPUT
        A batch of logs:
        {input}

        ## GUARDRAILS

        You MUST reply **only** with a valid JSON object. No explanations,
        no extra text, no formatting outside the JSON.

        1. Based on the provided log entries, identify which network service
            they indicate activity for.
            - Respond with one of the following labels: SSH, Telnet, SMB,
              Other.
            - Choose the label that best represents the dominant or most
            clearly indicated service.
        2. What is the total duration of suspicious or security-relevant
            activity in the provided log entries?
            - Respond with the duration in ISO 8601 format (e.g., PT15M30S).
            If no suspicious activity is found, respond with "None".
        3. What is the IP address of the attacker or source of suspicious
            activity in the provided log entries?
            - If no such IP can be identified, respond with "None".

        ## OUTPUT SCHEMA (strict)

        Example output:
        {{
        "duration": string,
        "attacker": string,
        "service": string,
        }}

        - **Replace all** placeholders with REAL extracted values from
        the input.
        - **Never leave** placeholder text in the output.
        - **No Hallucination**: NEVER invent IPs, ports, protocols, or
        timestamps. Only use information present in the logs.

        Remember: **ONLY reply with a valid JSON**, no comments, no
        explanations.
        """

    # Vytvorenie systémovej inštrukcie pre agenta
    system_prompt = PromptTemplate.from_template(template)

    # Vrátenie nakonfigurovaného agenta
    return system_prompt | llm_client.with_structured_output(LogsMetadata)


@retry_on_failure(max_retries=2)
def spawn_logs_descriptor_agent(llm_client: BaseChatModel) -> Runnable:
    """
    Vytvorí nakonfigurovanú inštanciu agenta pre popis aktivity v logoch.

    Ide o implementáciu Popisovača logov (kapitola 3.2.2).

    Tento agent pripravuje detailné správy o aktivite v logoch
    pre bezpečnostných analytikov. Analyzuje neúspešné a úspešné
    prihlásenia a vytvára komplexnú správu o aktivitách.

    Parametre:
        llm_client (BaseChatModel): LLM tvoriaci základ agenta

    Návratová hodnota:
        Runnable: Nakonfigurovaný agent pre analýzu aktivity

    Štruktúrovaný výstup:
        LogsDescription - obsahuje pole 'activity' s detailnou správou
        o aktivitách v logoch rozdelených do troch odsekov
    """
    # Šablóna pre systémovú inštrukciu agenta
    template = """
        You are **Logs-Activity-Analyst**, an AI agent preparing report about
        log events for cybersecurity analyst.

        ## YOUR INPUT
        A batch of logs:
        {input}

        ## GUARDRAILS

        1. Write a long and comprehensive in-depth report that will
            **summarize** the notable activity in provided logs.
        - You should provide as much detail and information as possible.
        - Output should be divided into three paragraphs:
            - **First paragraph**: Describe the activity in the logs,
            including
            - the type of activity, the involved parties, present users
            and the context.
            - **Second paragraph**: Describe the nature of **failed**
            logins,
            - including the number of attempts, the time frame, and any
            patterns.
            - **Third paragraph**: Describe the nature of **successful**
            logins,
            - including the number of attempts, the time frame, and any
            patterns.
        - **BE PRECISE**: It is crucial to use exact numbers and figures,
        your answer **cannot** contain general talk like "multiple" or
        "several".

        ## OUTPUT FORMAT (strict)
        Reply only with JSON in exactly this schema (no extra keys, no prose):
        {{
        "description": string,
        }}
        """

    # Vytvorenie systémovej inštrukcie pre agenta
    system_prompt = PromptTemplate.from_template(template)

    # Vrátenie nakonfigurovaného agenta
    return system_prompt | llm_client.with_structured_output(LogsDescription)


@retry_on_failure(max_retries=2)
def spawn_logs_classifier_agent(llm_client: BaseChatModel) -> Runnable:
    """
    Vytvorí nakonfigurovanú inštanciu agenta pre klasifikáciu hrozieb v logoch.

    Ide o implementáciu Klasifikátora logov (kapitola 3.2.2).

    Tento agent rozhoduje na základe metadát a popisu aktivít v logoch,
    či došlo k narušeniu systému. Analyzuje indikátory brute force útokov
    a určuje, či bol systém kompromitovaný pomocí viacstupňovej analýzy.

    Parametre:
        llm_client (BaseChatModel): LLM tvoriaci základ agenta

    Návratová hodnota:
        Runnable: Nakonfigurovaný agent pre klasifikáciu hrozieb

    Štruktúrovaný výstup:
        LogsAnalysisResult - obsahuje polia 'bruteforce' (boolean),
        'system_compromised' (boolean) a 'reason' (string) s odôvodnením
    """
    # Šablóna pre systémovú inštrukciu agenta
    template = """
        You are **AI Guardian**, an AI agent protecting system from breaches.
        Based on the data provided by other agents, decide whether system has
        been compromised.

        ## GUARDRAILS

        You will:

        1. **Inspect the logs metadata:**
        **Logs metadata:**
        {logs_metadata}

        2. **Inspect the logs description:**
        **Logs description:**
        {logs_description}

        3. Think step by step through each of these guardrails:
        a. Suspiciously high number of failed login attempts followed by
        **successful** login?
        b. High volume of attempts in a short time?
        c. Short duration of the session?
        d. Use of non-specific usernames like "root" or "admin"?
        set "bruteforce" to **true** if at least two of the above
        indicators are present.

        4. Think step by step through each of these guardrails:
        a. "bruteforce" is **true**?
        b. successful login after bruteforce activity?
        set "system_compromised" to **true** if above indicators are
        present.

        5. Explain your reasoning:
        - Set "reason" to your reasoning.

        ## OUTPUT FORMAT (strict)
        Reply only with JSON in exactly this schema (no extra keys, no prose):
        {{"bruteforce": boolean, "system_compromised": boolean,
        "reason": string}}
        """

    # Vytvorenie systémovej inštrukcie pre agenta
    system_prompt = PromptTemplate.from_template(template)

    # Vrátenie nakonfigurovaného agenta
    return (system_prompt |
            llm_client.with_structured_output(LogsAnalysisResult))


@retry_on_failure(max_retries=2)
def spawn_flow_classifier_agent(llm_client: BaseChatModel) -> Runnable:
    """
    Vytvorí nakonfigurovanú inštanciu agenta pre klasifikáciu sieťových tokov.

    Tento agent analyzuje sieťové toky a rozhoduje, či indikujú
    brute force útok. Posudzuje protokol, porty, počet paketov,
    množstvo dát a trvanie spojenia na základe špecifických kritérií.

    Parametre:
        llm_client (BaseChatModel): LLM tvoriaci základ agenta

    Návratová hodnota:
        Runnable: Nakonfigurovaný agent pre klasifikáciu sieťových tokov

    Štruktúrovaný výstup:
        FlowAnalysisResult - obsahuje polia 'bruteforce' (boolean)
        a 'reason' (string) s odôvodnením analýzy toku
    """
    # Šablóna pre systémovú inštrukciu agenta
    template = """
        You are **AI Guardian**, an AI agent protecting system from breaches.
        Based on the data provided by other agents, decide whether system has
        been under brute-force attack.

        ## GUARDRAILS

        You will:

        1. **Inspect the network-flow:**
        {flow_data}

        2. Think step by step through each of these guardrails:
        a. protocol = TCP ?
        b. source port > 1024 ?
        c. destination port = 22 ?
        d. packets > 10 and < 30 ?
        e. bytes > 1400 and < 5000 ?
        f. duration < 5s ?
        set "bruteforce" to **true** if at least four of the above
        indicators is present.

        3. Explain your reasoning:
        - Set "reason" to your reasoning.

        ## OUTPUT FORMAT (strict)
        Reply **only** with JSON that fulfils the exact schema below:

        {{"bruteforce": boolean, "reason": string}}
        """

    # Vytvorenie systémovej inštrukcie pre agenta
    system_prompt = PromptTemplate.from_template(template)

    # Vrátenie nakonfigurovaného agenta
    return (system_prompt |
            llm_client.with_structured_output(FlowAnalysisResult))
