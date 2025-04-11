import sys
import os
from PyQt5.uic import compileUi


def convert_ui_to_py(input_ui_file, output_py_file=None):
    """
    Конвертирует .ui файл Qt Designer в Python-код
    :param input_ui_file: Путь к .ui файлу
    :param output_py_file: Путь к выходному .py файлу (если None, будет использовано то же имя)
    """
    if not os.path.exists(input_ui_file):
        raise FileNotFoundError(f"UI файл не найден: {input_ui_file}")

    if output_py_file is None:
        output_py_file = os.path.splitext(input_ui_file)[0] + '.py'

    with open(output_py_file, 'w', encoding='utf-8') as f:
        compileUi(input_ui_file, f)

    print(f"Успешно сконвертировано: {input_ui_file} -> {output_py_file}")


if __name__ == '__main__':
    # Если нужно конвертировать конкретный файл по умолчанию
    default_ui_file = "rezerv/windows_add.ui"

    if len(sys.argv) < 2:
        # Пробуем конвертировать файл по умолчанию
        if os.path.exists(default_ui_file):
            try:
                convert_ui_to_py(default_ui_file)
                sys.exit(0)
            except Exception as e:
                print(f"Ошибка при конвертации {default_ui_file}: {str(e)}")

        print("Использование: python convert_ui.py file.ui [output.py]")
        print("Пример: python convert_ui.py myform.ui ui_myform.py")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        convert_ui_to_py(input_file, output_file)
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        sys.exit(1)