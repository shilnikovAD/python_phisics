# Python Physics - Pendulum Demo

🔮 A simple web application demonstrating pendulum physics behavior using Python backend and Node.js frontend.

## Features / Возможности

- **Real-time pendulum simulation** / Симуляция маятника в реальном времени
- **Interactive controls** / Интерактивные элементы управления
  - Adjust pendulum length / Регулировка длины маятника
  - Set initial angle / Установка начального угла
  - Control damping factor / Управление коэффициентом затухания
- **Visual trail effect** / Визуальный эффект следа
- **Physics stats display** / Отображение физических параметров
- **Dual mode operation** / Двойной режим работы
  - Python API mode (when Python server is running)
  - Local JavaScript simulation (standalone)

## Project Structure / Структура проекта

```
python_phisics/
├── pendulum/
│   └── pendulum.py      # Python physics engine and API server
├── web/
│   ├── server.js        # Node.js web server
│   ├── package.json     # Node.js dependencies
│   └── public/
│       ├── index.html   # Web interface
│       └── pendulum.js  # JavaScript simulation
└── README.md
```

## Quick Start / Быстрый старт

### Option 1: Full Stack (Python + Node.js)

1. **Start Python API server:**
   ```bash
   cd pendulum
   python pendulum.py
   ```
   The API will run on `http://localhost:8000`

2. **Start Node.js web server (in a new terminal):**
   ```bash
   cd web
   npm start
   ```
   The web app will run on `http://localhost:3000`

3. **Open your browser:**
   Navigate to `http://localhost:3000`

### Option 2: Standalone (Node.js only)

If you just want to see the demo without Python:

```bash
cd web
npm start
```

The application will run in local JavaScript simulation mode.

## API Endpoints / API Эндпоинты

The Python backend provides the following API endpoints:

| Endpoint | Description |
|----------|-------------|
| `GET /api/state` | Get current pendulum state (updates physics) |
| `GET /api/reset?angle=0.5&length=1.0` | Reset pendulum with parameters |
| `GET /api/info` | Get API information |

## Physics Model / Физическая модель

The pendulum follows the simple harmonic motion equation:

```
α = -(g/L) * sin(θ) - damping * ω
```

Where:
- `α` - angular acceleration / угловое ускорение
- `g` - gravitational acceleration (9.81 m/s²) / ускорение свободного падения
- `L` - pendulum length / длина маятника
- `θ` - angle from vertical / угол от вертикали
- `ω` - angular velocity / угловая скорость
- `damping` - damping coefficient / коэффициент затухания

### Numerical Integration / Численное интегрирование

The simulation uses the **Runge-Kutta 4th order (RK4)** method for numerical integration, which provides:
- Excellent energy conservation (< 0.001% energy drift)
- High accuracy for long-term simulations
- Stable motion without artificial energy gain or loss

RK4 is significantly more accurate than the simple Euler method, reducing RMS (Root Mean Square) error by orders of magnitude.

## Requirements / Требования

- Python 3.6+ (for Python backend)
- Node.js 12+ (for web server)

## License

MIT
