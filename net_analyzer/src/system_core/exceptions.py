"""
Tento modul definuje špecifické výnimky používané v rôznych častiach
aplikácie.
"""


class AgentInitializationError(Exception):
    """
    Výnimka vyvolaná pri neúspešnej inicializácii LLM agenta.
    """

    def __init__(self, message="Inicializácia LLM agenta zlyhala", *args):
        """
        Inicializuje výnimku AgentInitializationError.

        Parametre:
            message (str): Správa popisujúca chybu
            *args: Ďalšie argumenty pre základnú Exception triedu
        """
        super().__init__(message, *args)


class ApiClientInitializationError(Exception):
    """
    Výnimka vyvolaná pri neúspešnej inicializácii API klienta.
    """

    def __init__(self, message="Inicializácia API klienta zlyhala", *args):
        """
        Inicializuje výnimku ApiClientInitializationError.

        Parametre:
            message (str): Správa popisujúca chybu
            *args: Ďalšie argumenty pre základnú Exception triedu
        """
        super().__init__(message, *args)


class DatasetLoadError(Exception):
    """
    Výnimka vyvolaná pri chybe počas načítavania datasetu.
    """

    def __init__(self, message="Načítanie datasetu zlyhalo", *args):
        """
        Inicializuje výnimku DatasetLoadError.

        Parametre:
            message (str): Správa popisujúca chybu
            *args: Ďalšie argumenty pre základnú Exception triedu
        """
        super().__init__(message, *args)


class MissingApiKeyError(Exception):
    """
    Výnimka vyvolaná pri chýbajúcom API kľúči.

    Táto výnimka sa používa keď API kľúč nie je nastavený alebo
    je neplatný pre príslušný API klient.
    """

    def __init__(self, message="API kľúč nie je nastavený alebo je neplatný",
                 *args):
        """
        Inicializuje výnimku MissingApiKeyError.

        Parametre:
            message (str): Správa popisujúca chybu
            *args: Ďalšie argumenty pre základnú Exception triedu
        """
        super().__init__(message, *args)


class EnvFileNotFoundError(Exception):
    """
    Výnimka vyvolaná pri chýbajúcom .env súbore.

    Táto výnimka sa používa keď .env súbor s konfiguráciou
    aplikácie nie je nájdený v očakávanom umiestnení.
    """

    def __init__(self, message=".env súbor nebol nájdený", *args):
        """
        Inicializuje výnimku EnvFileNotFoundError.

        Parametre:
            message (str): Správa popisujúca chybu
            *args: Ďalšie argumenty pre základnú Exception triedu
        """
        super().__init__(message, *args)
