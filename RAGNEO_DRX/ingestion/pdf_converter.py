from pathlib import Path
from multiprocessing import Pool, cpu_count
from typing import List
import traceback

from pdfminer.high_level import extract_text

from utils.config import config
from utils.logger import logger
from utils.helpers import ensure_dir


class PDFConverter:
    """
    Конвертер PDF → TXT
    """

    def __init__(self):

        self.pdf_dir = config.PDF_DIR
        self.txt_dir = config.TXT_DIR

        ensure_dir(self.txt_dir)

    # =====================================
    # SINGLE FILE CONVERSION
    # =====================================

    def convert_pdf(self, pdf_path: Path) -> Path:
        """
        Конвертация одного PDF в TXT
        """

        try:

            txt_path = self.txt_dir / f"{pdf_path.stem}.txt"

            if txt_path.exists():
                logger.info(f"TXT уже существует: {txt_path.name}")
                return txt_path

            logger.info(f"Конвертация PDF: {pdf_path.name}")

            text = extract_text(str(pdf_path))

            if not text:
                logger.warning(f"Пустой текст в файле {pdf_path.name}")

            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(text)

            logger.info(f"TXT сохранен: {txt_path.name}")

            return txt_path

        except Exception as e:

            logger.error(f"Ошибка конвертации {pdf_path.name}")
            logger.error(traceback.format_exc())

            return None

    # =====================================
    # MULTIPROCESS CONVERSION
    # =====================================

    def _worker(self, pdf_path: Path):

        return self.convert_pdf(pdf_path)

    def convert_all(self) -> List[Path]:
        """
        Конвертация всех PDF
        """

        pdf_files = list(self.pdf_dir.glob("*.pdf"))

        if not pdf_files:
            logger.warning("PDF файлы не найдены")
            return []

        logger.info(f"Найдено PDF файлов: {len(pdf_files)}")

        workers = max(cpu_count() - 1, 1)

        logger.info(f"Используем процессов: {workers}")

        with Pool(workers) as pool:

            results = pool.map(self._worker, pdf_files)

        results = [r for r in results if r is not None]

        logger.info(f"Конвертировано файлов: {len(results)}")

        return results


# =====================================
# QUICK RUN
# =====================================

def run_pdf_conversion():

    converter = PDFConverter()

    txt_files = converter.convert_all()

    logger.info("Конвертация завершена")

    return txt_files