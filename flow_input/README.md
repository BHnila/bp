
# CIC-IDS2017 Dataset - Inštrukcie na stiahnutie a uloženie

Tento priečinok obsahuje vstupné dáta pre analýzu sieťových tokov. Dataset CIC-IDS2017 je potrebné stiahnuť samostatne.

## Požiadavky na dataset

- **Dataset**: CIC-IDS2017
- **Formát**: CSV súbor
- **Názov súboru**: `CIC_IDS2017.pcap_ISCX.csv`
- **Veľkosť**: ~128 MB

## Stiahnutie datasetu

1. Prejdite na nasledujúci SharePoint odkaz:
   ```
   https://stubask-my.sharepoint.com/:f:/g/personal/xhnila_stuba_sk/EtJE88VLngxHpoEwjxMHVDYB5Y0T9bY44pV7HTS-hLHXAg?e=axIoiG
   ```

2. Stiahnite súbor `CIC_IDS2017.pcap_ISCX.csv`

3. Vložte stiahnutý súbor do tohto priečinka (`bp/flow_input/`)


## Umiestnenie súboru

Dataset musí byť uložený v tomto priečinku s presným názvom:
```
bp/flow_input/CIC_IDS2017.pcap_ISCX.csv
```

## Riešenie problémov

### Chyba pri spustení aplikácie

Ak sa aplikácia nespúšťa kvôli chýbajúcemu datasetu:

1. Uistite sa, že súbor `CIC_IDS2017.pcap_ISCX.csv` existuje v tomto priečinku
2. Skontrolujte názov súboru (musí byť presne taký, ako je uvedený)
3. Overte oprávnenia na čítanie súboru:
   ```bash
   chmod 644 CIC_IDS2017.pcap_ISCX.csv
   ```

## Poznámky

- Súbor nie je súčasťou Git repozitára kvôli veľkosti
- Pre testovanie môžete použiť menšiu vzorku dát

---

**Dôležité**: Bez tohto datasetu nebude fungovať analýza sieťových tokov (režim 2) aplikácie.
