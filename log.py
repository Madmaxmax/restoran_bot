import logging
from colorama import init, Fore, Style

logger = logging.getLogger(__name__)


def start_log():
    # Инициализация colorama
    init(autoreset=True)

    # Настройка форматирования логов
    log_format = '[%(asctime)s] %(levelname)s | %(name)s | %(message)s'

    # Настройка обработчика для уровня ERROR
    error_format = logging.Formatter('[%(asctime)s] ERROR | %(name)s | ERROR | %(message)s')
    error_handler = logging.StreamHandler()  # Можете использовать другой обработчик, если необходимо
    error_handler.setFormatter(error_format)
    error_handler.setLevel(logging.ERROR)

    logging.basicConfig(format=log_format, level=logging.INFO)

    # Измените цвет для INFO и WARNING
    logging.addLevelName(logging.INFO, f"{Fore.CYAN}{logging.getLevelName(logging.INFO)}{Style.RESET_ALL}")
    logging.addLevelName(logging.WARNING, f"{Fore.MAGENTA}{logging.getLevelName(logging.WARNING)}{Style.RESET_ALL}")
    logging.addLevelName(logging.ERROR, f"{Fore.RED}{logging.getLevelName(logging.ERROR)}{Style.RESET_ALL}")


