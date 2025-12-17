"""
Модель Изинга 2D - М10Б: Ферромагнетизм
"""

import numpy as np
from typing import Dict, List, Tuple


class IsingModel2D:
    """
    2D модель Изинга с алгоритмом Метрополиса
    """

    def __init__(self, size: int = 30, T: float = 1.0, J: float = 1.0, B: float = 0.0):
        self.size = size
        self.T = T
        self.J = J
        self.B = B
        self.kB = 1.0

        # Инициализация решетки случайными спинами
        self.spins = np.random.choice([-1, 1], size=(size, size))

    def set_spins(self, spins: List[List[int]]):
        """Установить конфигурацию спинов"""
        self.spins = np.array(spins)

    def get_spins(self) -> List[List[int]]:
        """Получить текущую конфигурацию"""
        return self.spins.tolist()

    def flip_spin(self, i: int, j: int):
        """Перевернуть спин в позиции (i, j)"""
        self.spins[i, j] *= -1

    def local_energy(self, i: int, j: int) -> float:
        """
        Локальная энергия спина в позиции (i, j)
        с периодическими граничными условиями
        """
        spin = self.spins[i, j]
        N = self.size

        # Энергия во внешнем поле
        E = -self.B * spin

        # Взаимодействие с 4 соседями (периодические условия)
        neighbors = [
            self.spins[(i + 1) % N, j],  # снизу
            self.spins[(i - 1) % N, j],  # сверху
            self.spins[i, (j + 1) % N],  # справа
            self.spins[i, (j - 1) % N],  # слева
        ]

        E -= self.J * spin * sum(neighbors)

        return E

    def metropolis_step(self) -> bool:
        """
        Один шаг алгоритма Метрополиса
        Возвращает True если спин был перевернут
        """
        # Случайный спин
        i = np.random.randint(0, self.size)
        j = np.random.randint(0, self.size)

        # Энергия до переворота
        E_before = self.local_energy(i, j)

        # Переворачиваем
        self.spins[i, j] *= -1

        # Энергия после
        E_after = self.local_energy(i, j)

        # Изменение энергии
        dE = E_after - E_before

        # Критерий Метрополиса
        if dE <= 0 or np.random.random() < np.exp(-dE / (self.kB * self.T)):
            return True  # Принимаем
        else:
            # Отклоняем - возвращаем обратно
            self.spins[i, j] *= -1
            return False

    def run_steps(self, n_steps: int) -> Tuple[int, List[List[int]]]:
        """
        Выполнить n_steps шагов Монте-Карло
        Возвращает (количество принятых, финальная конфигурация)
        """
        accepted = 0
        for _ in range(n_steps):
            if self.metropolis_step():
                accepted += 1

        return accepted, self.get_spins()

    def calculate_magnetization(self) -> float:
        """Намагниченность системы (нормированная)"""
        return float(np.sum(self.spins) / (self.size * self.size))

    def calculate_energy(self) -> float:
        """Полная энергия системы (оптимизированная векторизованная версия)"""
        # Энергия поля
        E_field = -self.B * np.sum(self.spins)

        # Энергия обменного взаимодействия (векторизованная)
        # Правые соседи
        E_right = -self.J * np.sum(self.spins * np.roll(self.spins, -1, axis=1))
        # Нижние соседи
        E_down = -self.J * np.sum(self.spins * np.roll(self.spins, -1, axis=0))

        return float(E_field + E_right + E_down)

    def get_state(self) -> Dict:
        """Получить состояние системы"""
        return {
            "spins": self.get_spins(),
            "magnetization": self.calculate_magnetization(),
            "energy": self.calculate_energy(),
            "size": self.size,
            "T": self.T,
            "J": self.J,
            "B": self.B,
        }


# Глобальное хранилище моделей (по session_id)
_models: Dict[str, IsingModel2D] = {}


def get_model(session_id: str) -> IsingModel2D:
    """Получить или создать модель для сессии"""
    if session_id not in _models:
        _models[session_id] = IsingModel2D()
    return _models[session_id]


def cleanup_old_sessions():
    """Очистка старых сессий"""
    if len(_models) > 100:
        keys = list(_models.keys())
        for key in keys[: len(keys) // 2]:
            del _models[key]


# ============================================================================
# М10Б: Ферромагнетизм - функции для анализа
# ============================================================================


def scan_temperature_ferromagnetic(
    size: int = 20,
    J: float = 1.0,
    B: float = 0.0,
    T_min: float = 0.5,
    T_max: float = 4.0,
    T_steps: int = 25,
    equilibration_steps: int = 2000,
    measurement_steps: int = 1000,
) -> Dict:
    """
    М10Б: Сканирование ферромагнетика (J>0) по температурам

    Возвращает:
    - temperatures: список температур
    - M_abs_avg: средняя абсолютная намагниченность ⟨|M|⟩
    - susceptibility: магнитная восприимчивость χ
    - energy_avg: средняя энергия
    """
    temperatures = np.linspace(T_min, T_max, T_steps)
    N_total = size * size

    results = {
        "temperatures": [],
        "M_abs_avg": [],
        "M_std": [],
        "susceptibility": [],
        "energy_avg": [],
    }

    for T in temperatures:
        # Создаем модель ФЕРРОМАГНЕТИКА (J>0!)
        model = IsingModel2D(size=size, T=T, J=J, B=B)

        # Термализация (достижение равновесия)
        for _ in range(equilibration_steps):
            model.metropolis_step()

        # Измерения
        magnetizations = []
        energies = []

        for _ in range(measurement_steps):
            model.metropolis_step()
            M = np.sum(model.spins)
            E = model.calculate_energy()
            magnetizations.append(M)
            energies.append(E)

        magnetizations = np.array(magnetizations)

        # Статистика
        M_abs_avg = np.mean(np.abs(magnetizations))  # ⟨|M|⟩
        M_std = np.std(magnetizations)

        # Восприимчивость: χ = (⟨M²⟩ - ⟨M⟩²) / T
        M_avg = np.mean(magnetizations)
        M_squared_avg = np.mean(magnetizations**2)
        chi = (M_squared_avg - M_avg**2) / (T * N_total) if T > 0 else 0

        # Энергия
        E_avg = np.mean(energies)

        results["temperatures"].append(float(T))
        results["M_abs_avg"].append(float(M_abs_avg / N_total))  # Нормируем
        results["M_std"].append(float(M_std / N_total))
        results["susceptibility"].append(float(chi))
        results["energy_avg"].append(float(E_avg / N_total))

    return results


def find_critical_temperature(
    size: int = 20,
    J: float = 1.0,
    T_min: float = 1.5,
    T_max: float = 3.5,
    T_steps: int = 30,
) -> Dict:
    """
    М10Б: Определение температуры фазового перехода T₀ (T_c)

    Метод: Максимум восприимчивости χ

    Теоретическое значение для 2D: T_c ≈ 2.269 * J
    """
    # Сканирование
    result = scan_temperature_ferromagnetic(
        size=size,
        J=J,
        B=0.0,
        T_min=T_min,
        T_max=T_max,
        T_steps=T_steps,
        equilibration_steps=3000,
        measurement_steps=1500,
    )

    # Максимум восприимчивости
    chi_values = np.array(result["susceptibility"])
    T_values = np.array(result["temperatures"])

    idx_max_chi = np.argmax(chi_values)
    T_c_exp = T_values[idx_max_chi]
    chi_max = chi_values[idx_max_chi]

    # Теория
    T_c_theory = 2.269 * J

    return {
        "T_c_experimental": float(T_c_exp),
        "chi_max": float(chi_max),
        "T_c_theoretical": float(T_c_theory),
        "error_percent": float(abs(T_c_exp - T_c_theory) / T_c_theory * 100),
        "scan_result": result,
    }
