# LLM Net Analyzer

Systém detekcie útokov hrubou silou pomocou veľkých jazykových modelov (LLM). Aplikácia analyzuje Linux logy a sieťové toky na identifikáciu bezpečnostných hrozieb.

## Štruktúra repozitára

```
├── requirements.txt              # Python závislosti
├── README.md                     # Dokumentácia projektu
├── net_analyzer/                 # Hlavná aplikácia
│   ├── __main__.py               # Vstupný bod aplikácie
│   └── src/                      # Zdrojový kód
│       ├── data_processing/      # Spracovanie dát
│       ├── llm/                  # LLM agenti a toky
│       ├── log_tools/            # Nástroje pre analýzu logov
│       └── system_core/          # Základná funkčnosť systému
├── flow_input/                   # Vstupné súbory pre analýzu tokov
│   ├── CIC_IDS2017.pcap_ISCX.csv # Dataset (treba stiahnuť)
│   └── README.md                 # inštrukcie pre stiahnutie
├── log_input/                    # Vstupné log súbory pre analýzu
│   ├── BENIGN_*.txt              # Neškodné logy
│   └── MALICIOUS_*.txt           # Škodlivé logy
├── logs_dataset/                 # Náš vlastný dataset logov
│   ├── benign/                   # Neškodné logy
│   └── malicious/                # Škodlivé logy
├── fine_tuning/                  # Ladenie LLM modelov
│   ├── tuning_script.ipynb       # Colab skript pre ladenie
│   ├── bruteLlama3B/             # Dáta pre BruteLlama3B model
│   ├── secLlama3B/               # Dáta pre SecLlama3B model
│   └── seed_examples/            # Referenčné príklady pre ladenie
└── example_output/               # Ukážkové výstupy
```

## Požiadavky na systém

- **Operačný systém**: Linux (alebo Windows s WSL)
- **Python**: verzia 3.12.3 alebo vyššia
- **Git**: pre klonovanie repozitára
- **Ollama**: pre spustenie LLM modelov lokálne

## Inštalácia

### 1. Príprava systému

Nainštalujte si Python z oficiálnej stránky:
```
https://www.python.org/downloads/
```

Nainštalujte si Git:
```
https://git-scm.com/downloads
```

### 2. Inštalácia Ollama

1. Stiahnite si aplikáciu Ollama pre vaše prostredie:
   ```
   https://ollama.com/download
   ```

2. Nainštalujte aplikáciu Ollama podľa pokynov inštalátora.

3. Stiahnite si priečinok obsahujúci LLM modely `secLlama3B` a `bruteLlama3B`:
   ```
   https://stubask-my.sharepoint.com/:f:/g/personal/xhnila_stuba_sk/EhHr3Ms69IZNugK5s-xhFi0BRrozbaegBtVrm5QWLdg-iQ?e=3QLuty
   ```

4. Otvorte stiahnutý priečinok s LLM a spustite skript `install.sh`:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```
   **Poznámka**: Skript funguje iba v prostredí Linux alebo WSL.

5. Overte úspešnosť zavedenia modelov:
   ```bash
   ollama ls
   ```
   Výstup by mal obsahovať:
   - 10 rôznych modelov `secLlama3B`
   - 10 rôznych modelov `bruteLlama3B`
   - model `llama3.2:3B`

6. Spustite lokálny Ollama server:
   ```bash
   ollama serve
   ```

### 3. Inštalácia LLM Net Analyzer

1. Klonujte repozitár:
   ```bash
   git clone https://github.com/BHnila/bp.git
   cd bp
   ```

2. Vytvorte virtuálne prostredie Python:
   ```bash
   python3 -m venv venv
   ```

3. Aktivujte virtuálne prostredie:
   ```bash
   source ./venv/bin/activate
   ```

4. Nainštalujte závislosti:
   ```bash
   pip install -r requirements.txt
   ```

### 4. Inštalácia datasetu CIC-IDS2017

1. Stiahnite si dataset CIC-IDS2017:
   ```
   https://stubask-my.sharepoint.com/:f:/g/personal/xhnila_stuba_sk/EtJE88VLngxHpoEwjxMHVDYB5Y0T9bY44pV7HTS-hLHXAg?e=axIoiG
   ```

2. Vložte stiahnutý súbor do priečinka `bp/flow_input/`.

## Spustenie aplikácie

1. Uistite sa, že je Ollama server spustený:
   ```bash
   ollama serve
   ```

2. Aktivujte virtuálne prostredie (ak nie je aktívne):
   ```bash
   source ./venv/bin/activate
   ```

3. Spustite aplikáciu:
   ```bash
   cd net_analyzer
   python3 -m net_analyzer
   ```
   alebo
   ```bash
   python3 -m net_analyzer.__main__
   ```

## Použitie

Po spustení aplikácie sa zobrazí interaktívne menu:

```
Vyberte typ analýzy:
[1] Analýza Linux logov
[2] Analýza sieťových tokov
[3] Ukončiť program
```

### Analýza Linux logov (režim 1)

- Analyzuje log súbory v priečinku `log_input/`
- Detekuje útoky hrubou silou na základe vzorcov v logoch
- Používa špecializované LLM agenty pre extrakciu metadát, popis aktivít a klasifikáciu

### Analýza sieťových tokov (režim 2)

- Analyzuje dataset CIC-IDS2017 v priečinku `flow_input/`
- Detekuje útoky hrubou silou na základe charakteristík sieťových tokov
- Poskytuje výkonnostné metriky (presnosť, citlivosť, F1 skóre)

### Nastavenie počtu epoch

Po výbere typu analýzy budete požiadaní o zadanie počtu epoch ladenia (0-10):
- **0 epoch**: Použije sa základný model Llama 3.2 3B
- **1-10 epoch**: Použije sa príslušný ladený model (bruteLlama3B pre logy, secLlama3B pre toky)

## Výstup aplikácie

Aplikácia poskytuje:
- Priebežné informácie o stave spracovania
- Výkonnostné metriky (presnosť, citlivosť, F1 skóre)
- Detailné výsledky klasifikácie
- Čas trvania analýzy

## Funkcie aplikácie

### Hlavné komponenty

- **LLM agenti**: Špecializované agenty pre rôžne úlohy analýzy
- **Detekčné toky**: Orchestrácia procesu detekcie útokov
- **Spracovanie dát**: Predspracovanie a transformácia vstupných dát
- **Vyhodnotenie**: Výpočet výkonnostných metrík

### Podporované typy útokov

- Brute force útoky na SSH
- Brute force útoky na SMB
- Brute force útoky na Telnet
- Analýza kompromitácie systému

## Riešenie problémov

### Časté problémy

1. **Ollama server nebeží**:
   ```bash
   ollama serve
   ```

2. **Chýbajúce modely**:
   ```bash
   ollama ls
   ```
   Overte, že sú nainštalované všetky potrebné modely.

3. **Chýbajúci dataset**:
   Uistite sa, že je súbor `CIC_IDS2017.pcap_ISCX.csv` v priečinku `flow_input/`.

4. **Python závislosti**:
   ```bash
   pip install -r requirements.txt
   ```

### Logy aplikácie

Aplikácia používa Python logging modul. Úroveň logovania je nastavená na INFO.

## Technické informácie

### Architektúra

- **Modulárny dizajn**: Rozdelenie na logické komponenty
- **Ošetrenie chýb**: Robustné spracovanie výnimiek
- **Konfigurovateľnosť**: Nastaviteľné parametre pre ladenie modelov

### Závislosti

Pozrite `requirements.txt` pre kompletný zoznam Python závislostí:
- pandas: Spracovanie dát
- langchain: LLM framework
- langchain_ollama: Ollama integrácia
- python-dotenv: Správa environment premenných

## Autor

**Boris Hnila**  
© 2025

Implementácia systému detekcie útokov hrubou silou pre bakalársku prácu.

---

**Poznámka**: Táto aplikácia je súčasťou akademického výskumu a je určená na vzdelávacie a výskumné účely.
