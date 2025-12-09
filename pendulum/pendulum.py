import math
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

EPS = 1e-12


class Pendulum:

    def __init__(self, length=1.0, mass=1.0, angle=0.5, angular_velocity=0.0, gravity=9.81,
                 damping=0.01, shape='point', bob_size=0.05):
        self.length = length
        self.mass = mass
        self.angle = angle
        self.angular_velocity = angular_velocity
        self.gravity = gravity
        self.damping = damping
        self.shape = shape
        self.bob_size = bob_size

        self.t_elapsed = 0.0
        self.initial_angle = angle
        self.I_cm = self._compute_I_cm()
        self.I_total = max(EPS, self.I_cm + self.mass * (self.length ** 2))

    def _compute_I_cm(self):
        if self.shape == 'point':
            return 0.0
        elif self.shape == 'disk':
            r = max(EPS, self.bob_size)
            return 0.5 * self.mass * r * r
        elif self.shape == 'sphere':
            r = max(EPS, self.bob_size)
            return 0.4 * self.mass * r * r
        elif self.shape == 'rod':
            Lrod = max(EPS, self.bob_size)
            return (1.0 / 12.0) * self.mass * (Lrod ** 2)
        else:
            return 0.0

    def recompute_inertia(self):
        self.I_cm = self._compute_I_cm()
        self.I_total = max(EPS, self.I_cm + self.mass * (self.length ** 2))

    def get_angular_acceleration(self):
        # Используем sin(angle) для большей точности
        torque_gravity = -self.mass * self.gravity * self.length * math.sin(self.angle)
        angular_acc = torque_gravity / self.I_total
        angular_acc -= self.damping * self.angular_velocity
        return angular_acc

    def update(self, dt=0.005):
        if dt <= 0:
            return

        # Symplectic Euler (leapfrog) - хорошее сохранение энергии для гамильтоновых систем
        # с правильной обработкой демпфирования
        
        # Вычисляем гравитационный момент
        torque_gravity = -self.mass * self.gravity * self.length * math.sin(self.angle)
        angular_acc_gravity = torque_gravity / self.I_total
        
        # Обновляем скорость: сначала гравитация, затем демпфирование
        # Для демпфирования используем аналитическое решение: v(t+dt) = v(t)*exp(-damping*dt)
        # что более точно, чем v(t+dt) = v(t)*(1-damping*dt)
        if self.damping > 0:
            # Сначала применяем гравитацию
            self.angular_velocity += angular_acc_gravity * dt
            # Затем демпфирование (точная формула)
            self.angular_velocity *= math.exp(-self.damping * dt)
        else:
            # Без демпфирования - просто обновляем от гравитации
            self.angular_velocity += angular_acc_gravity * dt
        
        # Обновляем угол с обновленной скоростью (симплектический шаг)
        self.angle += self.angular_velocity * dt

        self.t_elapsed += dt

    def analytic_solution(self, t=None):
        if t is None:
            t = self.t_elapsed

        # Для аналитического решения используем линеаризацию (sinθ ≈ θ)
        # но с поправкой на амплитуду для лучшего совпадения с нелинейной динамикой
        omega0_linear = math.sqrt(max(EPS, (self.mass * self.gravity * self.length) / self.I_total))
        
        # Поправка частоты для больших амплитуд (приближение для нелинейного маятника)
        # omega_nonlinear ≈ omega_linear * (1 - (1/16)*theta0^2) для малых углов
        # Используем более точную формулу через эллиптический интеграл (приближение)
        amplitude = abs(self.initial_angle)
        if amplitude > 1e-6:
            # Приближенная поправка на нелинейность
            # Для точной формулы нужны эллиптические интегралы, используем разложение
            # Поправочный множитель к частоте (приближение 3-го порядка)
            freq_correction = 1.0 + (1.0/16.0)*amplitude**2 + (11.0/3072.0)*amplitude**4
            omega0 = omega0_linear / freq_correction
        else:
            omega0 = omega0_linear
        
        beta = 0.5 * self.damping

        # Проверка режима
        discriminant = omega0 * omega0 - beta * beta

        if discriminant <= 0:
            # Апериодический режим
            gamma1 = -beta + math.sqrt(beta * beta - omega0 * omega0)
            gamma2 = -beta - math.sqrt(beta * beta - omega0 * omega0)
            A = self.initial_angle * gamma2 / (gamma2 - gamma1)
            B = self.initial_angle * gamma1 / (gamma1 - gamma2)
            theta_analytic = A * math.exp(gamma1 * t) + B * math.exp(gamma2 * t)
            omega_analytic = A * gamma1 * math.exp(gamma1 * t) + B * gamma2 * math.exp(gamma2 * t)
            return theta_analytic, omega_analytic, omega0

        # Колебательный режим
        omega = math.sqrt(max(EPS, discriminant))
        decay = math.exp(-beta * t)

        theta_analytic = self.initial_angle * decay * math.cos(omega * t)
        omega_analytic = -self.initial_angle * decay * (beta * math.cos(omega * t) + omega * math.sin(omega * t))

        return theta_analytic, omega_analytic, omega0

    def match_percent(self):
        theta_analytic, _, _ = self.analytic_solution()
        amplitude_ref = max(abs(self.initial_angle), 1e-3)
        error = abs(self.angle - theta_analytic)
        norm_error = error / amplitude_ref
        similarity = max(0.0, 100.0 * (1.0 - norm_error))
        return min(100.0, similarity)

    def get_state(self):
        x, y = self.get_position()
        theta_analytic, omega_analytic, omega0 = self.analytic_solution()
        return {
            "angle": self.angle,
            "angularVelocity": self.angular_velocity,
            "x": x,
            "y": y,
            "length": self.length,
            "mass": self.mass,
            "damping": self.damping,
            "shape": self.shape,
            "bobSize": self.bob_size,
            "I_cm": self.I_cm,
            "I_total": self.I_total,
            "analyticAngle": theta_analytic,
            "analyticAngularVelocity": omega_analytic,
            "analyticOmega0": omega0,
            "matchPercent": self.match_percent(),
            "time": self.t_elapsed,
            "initialAngle": self.initial_angle
        }

    def get_position(self):
        x = self.length * math.sin(self.angle)
        y = self.length * math.cos(self.angle)
        return (x, y)


class PendulumAPIHandler(BaseHTTPRequestHandler):
    pendulum = Pendulum(length=1.0, angle=0.8)

    def _set_headers(self, content_type='application/json'):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/api/state':
            # Обновляем состояние с малым шагом для точности
            self.pendulum.update(dt=0.002)
            self._set_headers()
            self.wfile.write(json.dumps(self.pendulum.get_state()).encode())

        elif parsed_path.path == '/api/reset':
            query = parse_qs(parsed_path.query)
            try:
                angle = float(query.get('angle', [0.8])[0])
                length = float(query.get('length', [1.0])[0])
                mass = float(query.get('mass', [1.0])[0])
                damping = float(query.get('damping', [0.01])[0])
                shape = query.get('shape', ['point'])[0]
                bob_size = float(query.get('bobSize', [0.05])[0])

                # Валидация параметров
                angle = max(-math.pi, min(math.pi, angle))
                length = max(0.01, min(10.0, length))
                mass = max(0.001, min(100.0, mass))
                damping = max(0.0, min(1.0, damping))
                if shape not in ('point', 'disk', 'rod', 'sphere'):
                    shape = 'point'
                bob_size = max(1e-4, min(10.0, bob_size))
            except (ValueError, TypeError):
                # Значения по умолчанию
                angle = 0.8
                length = 1.0
                mass = 1.0
                damping = 0.01
                shape = 'point'
                bob_size = 0.05

            # Создаем новый маятник
            self.pendulum = Pendulum(
                length=length, mass=mass, angle=angle,
                angular_velocity=0.0, damping=damping,
                shape=shape, bob_size=bob_size
            )
            self.pendulum.t_elapsed = 0.0
            self.pendulum.initial_angle = angle

            PendulumAPIHandler.pendulum = self.pendulum
            self._set_headers()
            self.wfile.write(json.dumps({"status": "reset", "state": self.pendulum.get_state()}).encode())

        elif parsed_path.path == '/api/info':
            self._set_headers()
            info = {
                "name": "Pendulum Physics API",
                "version": "1.1.2",
                "endpoints": ["/api/state", "/api/reset", "/api/info"],
                "notes": "Supports physical pendulum shapes with accurate physics simulation"
            }
            self.wfile.write(json.dumps(info).encode())

        else:
            self.send_response(404)
            self.end_headers()


def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, PendulumAPIHandler)
    print(f'Pendulum API server running on http://localhost:{port}')
    print('Endpoints: /api/state, /api/reset, /api/info')
    print('Press Ctrl+C to stop')
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()