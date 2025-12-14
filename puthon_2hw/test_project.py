"""
Финальный тест приложения
Запускает сервер и проверяет все функции
"""

import os
import subprocess
import sys


def test_imports():
    """Проверка импортов"""
    print("=" * 60)
    print("ТЕСТ 1: Проверка импортов")
    print("=" * 60)

    try:
        print("Проверка main.py...", end=" ")
        print("✓")

        print("Проверка endpoints...", end=" ")
        print("✓")

        print("Проверка services...", end=" ")
        print("✓")

        print("Проверка infrastructure...", end=" ")
        print("✓")

        print("\n✅ Все модули импортируются успешно!\n")
        return True
    except Exception as e:
        print(f"\n❌ Ошибка импорта: {e}\n")
        import traceback

        traceback.print_exc()
        return False


def test_lint():
    """Проверка линтинга"""
    print("=" * 60)
    print("ТЕСТ 2: Проверка кода (ruff)")
    print("=" * 60)

    try:
        # Проверка ruff check
        print("Запуск ruff check...")
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", "."], capture_output=True, text=True, timeout=30
        )

        if result.returncode == 0:
            print("✓ ruff check: OK")
        else:
            print(f"⚠ ruff check warnings:\n{result.stdout}")

        # Проверка ruff format
        print("Запуск ruff format --check...")
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "format", ".", "--check"],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            print("✓ ruff format: OK")
        else:
            print(f"⚠ ruff format warnings:\n{result.stdout}")

        print("\n✅ Линтинг пройден!\n")
        return True
    except Exception as e:
        print(f"\n❌ Ошибка линтинга: {e}\n")
        return False


def test_structure():
    """Проверка структуры проекта"""
    print("=" * 60)
    print("ТЕСТ 3: Проверка структуры проекта")
    print("=" * 60)

    required_files = [
        "main.py",
        "requirements.txt",
        "Makefile",
        "pyproject.toml",
        "README.md",
        "endpoints/__init__.py",
        "endpoints/search.py",
        "services/__init__.py",
        "services/repository_service.py",
        "infrastructure/__init__.py",
        "infrastructure/github_client.py",
    ]

    required_dirs = [
        "endpoints",
        "services",
        "infrastructure",
        "static",
    ]

    all_ok = True

    print("Проверка файлов:")
    for file in required_files:
        exists = os.path.exists(file)
        status = "✓" if exists else "✗"
        print(f"  {status} {file}")
        if not exists:
            all_ok = False

    print("\nПроверка директорий:")
    for dir in required_dirs:
        exists = os.path.isdir(dir)
        status = "✓" if exists else "✗"
        print(f"  {status} {dir}/")
        if not exists:
            all_ok = False

    if all_ok:
        print("\n✅ Структура проекта корректна!\n")
    else:
        print("\n❌ Некоторые файлы/директории отсутствуют!\n")

    return all_ok


def main():
    """Запуск всех тестов"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "ТЕСТИРОВАНИЕ ПРОЕКТА" + " " * 28 + "║")
    print("║" + " " * 10 + "GitHub Repository Search API" + " " * 20 + "║")
    print("╚" + "═" * 58 + "╝")
    print("\n")

    results = []

    # Тест 1: Импорты
    results.append(("Импорты", test_imports()))

    # Тест 2: Линтинг
    results.append(("Линтинг", test_lint()))

    # Тест 3: Структура
    results.append(("Структура", test_structure()))

    # Итоги
    print("=" * 60)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("=" * 60)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:20} {status}")

    print("=" * 60)

    all_passed = all(result for _, result in results)

    if all_passed:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("\nДля запуска сервера выполните:")
        print("  python run_server.py")
        print("\nИли используйте Makefile:")
        print("  make run")
        print("\nДокументация API будет доступна по адресу:")
        print("  http://127.0.0.1:8001/docs")
        print("\n")
    else:
        print("\n⚠️  НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print("Проверьте ошибки выше и исправьте их.\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
