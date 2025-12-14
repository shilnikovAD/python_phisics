import matplotlib.pyplot as plt
from pendulum import Pendulum


def measure_period(
    pend: Pendulum, dt: float, n_periods: int = 5, max_time: float = 50.0
) -> float:
    t_first = None
    t_last = None
    prev_angle = pend.angle

    while pend.t_elapsed < max_time:
        pend.update(dt)
        if prev_angle > 0 and pend.angle <= 0 and pend.angular_velocity < 0:
            if t_first is None:
                t_first = pend.t_elapsed
            else:
                t_last = pend.t_elapsed
                if t_last - t_first > (n_periods - 1) * 0.5 * dt:
                    break
        prev_angle = pend.angle

    if t_first is not None and t_last is not None:
        return (t_last - t_first) / (n_periods - 1)
    return float("nan")


def simulate_period_vs_amplitude():
    L = 1.0
    g = 9.81
    damping = 0.0
    dt = 0.001
    n_periods = 6

    amplitudes = [0.1 * i for i in range(1, 16)]
    periods = []
    energy_drifts = []

    for theta0 in amplitudes:
        pend = Pendulum(
            length=L,
            mass=1.0,
            angle=theta0,
            angular_velocity=0.0,
            gravity=g,
            damping=damping,
            shape="point",
            bob_size=0.05,
        )

        T = measure_period(pend, dt, n_periods=n_periods, max_time=40.0)
        periods.append(T)

        energy_drifts.append(pend.energy_violation * 100.0)

    plt.figure(figsize=(7, 4))
    plt.plot(amplitudes, periods, "o-b", label="T(θ₀)")
    plt.xlabel("Амплитуда, рад")
    plt.ylabel("Период, с")
    plt.title("Период vs амплитуда (без трения)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(7, 4))
    plt.plot(amplitudes, energy_drifts, "o-r")
    plt.xlabel("Амплитуда, рад")
    plt.ylabel("Отклонение энергии, %")
    plt.title("Сохранение энергии (damping = 0)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def simulate_period_vs_damping():
    L = 1.0
    g = 9.81
    theta0 = 0.5
    dt = 0.001
    n_periods = 6

    dampings = [0.01 * i for i in range(0, 13)]
    periods = []

    for damping in dampings:
        pend = Pendulum(
            length=L,
            mass=1.0,
            angle=theta0,
            angular_velocity=0.0,
            gravity=g,
            damping=damping,
            shape="point",
            bob_size=0.05,
        )

        T = measure_period(pend, dt, n_periods=n_periods, max_time=60.0)
        periods.append(T)

    plt.figure(figsize=(7, 4))
    plt.plot(dampings, periods, "o-r", label="T(γ)")
    plt.xlabel("Коэффициент трения u")
    plt.ylabel("Период, с")
    plt.title("Период vs коэффициент трения (θ = 0.5 рад)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    simulate_period_vs_amplitude()
    simulate_period_vs_damping()
