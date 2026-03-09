import re
import unicodedata
from pathlib import Path
from typing import List

from utils.config import config
from utils.logger import logger
from utils.helpers import ensure_dir


class TextCleaner:
    """
    Очистка текста после PDF конвертации
    """

    def __init__(self):

        self.input_dir = config.TXT_DIR
        self.output_dir = config.TXT_DIR

        ensure_dir(self.output_dir)

    # =====================================
    # BASIC CLEANING
    # =====================================

    def normalize_unicode(self, text: str) -> str:
        """
        Unicode нормализация
        """

        return unicodedata.normalize("NFKC", text)

    def remove_page_numbers(self, text: str) -> str:
        """
        Удаление номеров страниц
        """

        patterns = [
            r"\n\d+\n",
            r"\nPage \d+\n",
            r"\nСтраница \d+\n",
            r"\n— \d+ —\n"
        ]

        for pattern in patterns:
            text = re.sub(pattern, "\n", text)

        return text

    def fix_hyphenated_words(self, text: str) -> str:
        """
        Исправление разорванных слов
        """

        return re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)

    def remove_extra_linebreaks(self, text: str) -> str:
        """
        Удаление лишних переносов строк
        """

        text = re.sub(r"\n{2,}", "\n", text)

        return text

    def fix_linebreaks_inside_sentences(self, text: str) -> str:
        """
        Объединение строк внутри предложений
        """

        text = re.sub(r"(?<![.!?])\n", " ", text)

        return text

    def remove_extra_spaces(self, text: str) -> str:
        """
        Удаление лишних пробелов
        """

        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # =====================================
    # FULL CLEAN PIPELINE
    # =====================================

    def clean_text(self, text: str) -> str:

        text = self.normalize_unicode(text)

        text = self.fix_hyphenated_words(text)

        text = self.remove_page_numbers(text)

        text = self.fix_linebreaks_inside_sentences(text)

        text = self.remove_extra_linebreaks(text)

        text = self.remove_extra_spaces(text)

        return text

    # =====================================
    # FILE PROCESSING
    # =====================================

    def clean_file(self, txt_path: Path) -> Path:

        try:

            logger.info(f"Очистка текста: {txt_path.name}")

            with open(txt_path, "r", encoding="utf-8") as f:
                text = f.read()

            clean_text = self.clean_text(text)

            output_path = self.output_dir / txt_path.name

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(clean_text)

            logger.info(f"Файл очищен: {output_path.name}")

            return output_path

        except Exception as e:

            logger.error(f"Ошибка очистки {txt_path.name}: {e}")

            return None

    # =====================================
    # CLEAN ALL FILES
    # =====================================

    def clean_all(self) -> List[Path]:

        txt_files = list(self.input_dir.glob("*.txt"))

        if not txt_files:

            logger.warning("TXT файлы не найдены")

            return []

        logger.info(f"Найдено TXT файлов: {len(txt_files)}")

        results = []

        for txt in txt_files:

            result = self.clean_file(txt)

            if result:
                results.append(result)

        logger.info(f"Очищено файлов: {len(results)}")

        return results


# =====================================
# QUICK RUN
# =====================================

def run_text_cleaning():

    cleaner = TextCleaner()

    return cleaner.clean_all()