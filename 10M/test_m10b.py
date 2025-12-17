"""
Тестовый скрипт для задачи М10Б (Ферромагнетизм)
"""

import matplotlib.pyplot as plt
from ising_model import scan_temperature_ferromagnetic, find_critical_temperature

print("=" * 70)
print("М10Б: ФЕРРОМАГНЕТИЗМ - Демонстрация")
print("=" * 70)

# ============================================================================
# Тест 1: Сканирование ⟨M⟩(T) для ферромагнетика
# ============================================================================

print("\n1️⃣ Сканирование ⟨M⟩(T) для ферромагнетика (J=1.0)")
print("-" * 70)

result = scan_temperature_ferromagnetic(
    size=20,  # 20×20 = 400 спинов
    J=1.0,
    B=0.0,
    T_min=0.5,
    T_max=4.0,
    T_steps=25,
    equilibration_steps=2000,
    measurement_steps=1000,
)

print(f"{'T':<10} {'⟨|M|⟩':<15} {'χ':<15} {'⟨E⟩':<15}")
print("-" * 70)

for i in range(0, len(result["temperatures"]), 3):
    T = result["temperatures"][i]
    M_abs = result["M_abs_avg"][i]
    chi = result["susceptibility"][i]
    E = result["energy_avg"][i]
    print(f"{T:<10.2f} {M_abs:<15.4f} {chi:<15.6f} {E:<15.4f}")

# График M(T)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Намагниченность
ax1.plot(result["temperatures"], result["M_abs_avg"], "o-", linewidth=2, markersize=6)
ax1.axvline(x=2.269, color="r", linestyle="--", label="T_c теория ≈ 2.269")
ax1.set_xlabel("Температура T", fontsize=12)
ax1.set_ylabel("⟨|M|⟩ (абсолютная)", fontsize=12)
ax1.set_title("М10Б: Намагниченность ферромагнетика", fontsize=13, fontweight="bold")
ax1.grid(True, alpha=0.3)
ax1.legend()

# Восприимчивость
ax2.plot(
    result["temperatures"], result["susceptibility"], "s-", linewidth=2, markersize=6
)
ax2.axvline(x=2.269, color="r", linestyle="--", label="T_c теория ≈ 2.269")
ax2.set_xlabel("Температура T", fontsize=12)
ax2.set_ylabel("Восприимчивость χ", fontsize=12)
ax2.set_title("Восприимчивость (пик при T_c)", fontsize=13, fontweight="bold")
ax2.grid(True, alpha=0.3)
ax2.legend()

plt.tight_layout()
plt.savefig("m10b_magnetization.png", dpi=150)
print("\n✅ График сохранен: m10b_magnetization.png")

# ============================================================================
# Тест 2: Определение T_c (T₀)
# ============================================================================

print("\n2️⃣ Определение температуры фазового перехода T₀ (T_c)")
print("-" * 70)

tc_result = find_critical_temperature(size=20, J=1.0, T_min=1.5, T_max=3.5, T_steps=30)

print("\n📊 Результаты определения T_c:")
print(f"   Метод 1 (макс χ):     T_c = {tc_result['T_c_susceptibility']:.3f}")
print(f"   Максимум χ:           χ_max = {tc_result['chi_max']:.6f}")

if tc_result["T_c_magnetization"]:
    print(f"   Метод 2 (⟨|M|⟩=0.5):  T_c = {tc_result['T_c_magnetization']:.3f}")
else:
    print("   Метод 2 (⟨|M|⟩=0.5):  T_c = не найдено (M не пересекает 0.5)")

print(f"   Теория (2D Изинг):    T_c = {tc_result['T_c_theoretical']:.3f}")

# Расчет ошибки
T_c_exp = tc_result["T_c_susceptibility"]
T_c_theory = tc_result["T_c_theoretical"]
error = abs(T_c_exp - T_c_theory) / T_c_theory * 100

print(f"\n   Относительная ошибка: {error:.2f}%")

# График с пиком χ
scan_data = tc_result["scan_result"]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

# M(T) с отметкой T_c
ax1.plot(scan_data["temperatures"], scan_data["M_abs_avg"], "b-o", linewidth=2)
ax1.axvline(
    x=T_c_exp, color="g", linestyle="--", linewidth=2, label=f"T_c эксп = {T_c_exp:.3f}"
)
ax1.axvline(
    x=T_c_theory,
    color="r",
    linestyle=":",
    linewidth=2,
    label=f"T_c теория = {T_c_theory:.3f}",
)
ax1.axhline(y=0.5, color="gray", linestyle="--", alpha=0.5, label="Порог = 0.5")
ax1.set_xlabel("Температура T", fontsize=12)
ax1.set_ylabel("⟨|M|⟩", fontsize=12)
ax1.set_title("Определение T_c: Намагниченность", fontsize=13, fontweight="bold")
ax1.grid(True, alpha=0.3)
ax1.legend()

# χ(T) с пиком
ax2.plot(scan_data["temperatures"], scan_data["susceptibility"], "r-s", linewidth=2)
ax2.axvline(
    x=T_c_exp,
    color="g",
    linestyle="--",
    linewidth=2,
    label=f"Макс χ при T = {T_c_exp:.3f}",
)
ax2.axvline(
    x=T_c_theory,
    color="r",
    linestyle=":",
    linewidth=2,
    label=f"T_c теория = {T_c_theory:.3f}",
)
ax2.set_xlabel("Температура T", fontsize=12)
ax2.set_ylabel("Восприимчивость χ", fontsize=12)
ax2.set_title("Определение T_c: Пик восприимчивости", fontsize=13, fontweight="bold")
ax2.grid(True, alpha=0.3)
ax2.legend()

plt.tight_layout()
plt.savefig("m10b_critical_temperature.png", dpi=150)
print("✅ График сохранен: m10b_critical_temperature.png")

# ============================================================================
# Тест 3: Энергия системы
# ============================================================================

print("\n3️⃣ Энергия системы E(T)")
print("-" * 70)

print(f"{'T':<10} {'⟨E⟩/N':<15} {'σ_E/N':<15}")
print("-" * 70)

for i in range(0, len(result["temperatures"]), 5):
    T = result["temperatures"][i]
    E_avg = result["energy_avg"][i]
    E_std = result["energy_std"][i]
    print(f"{T:<10.2f} {E_avg:<15.4f} {E_std:<15.4f}")

# График энергии
plt.figure(figsize=(10, 6))
plt.errorbar(
    result["temperatures"],
    result["energy_avg"],
    yerr=result["energy_std"],
    fmt="o-",
    capsize=5,
    linewidth=2,
)
plt.axvline(x=2.269, color="r", linestyle="--", label="T_c ≈ 2.269")
plt.xlabel("Температура T", fontsize=12)
plt.ylabel("Энергия на спин ⟨E⟩/N", fontsize=12)
plt.title("Энергия ферромагнетика", fontsize=14, fontweight="bold")
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig("m10b_energy.png", dpi=150)
print("\n✅ График сохранен: m10b_energy.png")

# ============================================================================
# Итоги
# ============================================================================

print("\n" + "=" * 70)
print("✅ М10Б: ВСЕ ТЕСТЫ ВЫПОЛНЕНЫ")
print("=" * 70)

print("\n📊 Что продемонстрировано:")
print("   1. ✅ Система взаимодействующих спинов (J=1.0)")
print("   2. ✅ Энергия E = -J·∑ sᵢ·sⱼ (по соседям)")
print("   3. ✅ Метод Монте-Карло (алгоритм Метрополиса)")
print("   4. ✅ Равновесие при разных температурах")
print("   5. ✅ Функция ⟨M⟩(T)")
print("   6. ✅ Фазовый переход при T_c ≈ 2.269")
print("   7. ✅ Определение T₀ экспериментально:")
print(f"      - Метод максимума χ: T_c = {T_c_exp:.3f}")
print(f"      - Теория:             T_c = {T_c_theory:.3f}")
print(f"      - Ошибка:             {error:.2f}%")

print("\n📁 Сохраненные файлы:")
print("   - m10b_magnetization.png      (M(T) и χ(T))")
print("   - m10b_critical_temperature.png (определение T_c)")
print("   - m10b_energy.png             (энергия)")

print("\n🎓 Задание М10Б ВЫПОЛНЕНО!")
print("=" * 70)
