class PendulumSimulation {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');

        // Pendulum properties (default)
        this.length = 1.0;
        this.angle = Math.PI / 4; // 45 degrees
        this.initialAngle = this.angle;
        this.angularVelocity = 0;
        this.damping = 0.01;
        this.gravity = 9.81;
        this.mass = 1.0;

        // Shape properties
        this.shape = 'point'; // 'point', 'disk', 'sphere', 'rod'
        this.bobSize = 0.05; // radius for disk/sphere, length for rod

        // Derived inertia
        this.I_cm = this.computeIcm();
        this.I_total = Math.max(1e-12, this.I_cm + this.mass * this.length * this.length);

        // Visualization properties
        this.pivotX = this.canvas.width / 2;
        this.pivotY = 100;
        this.scale = 180; // pixels per meter
        this.bobRadiusVisual = 25;

        // Trail for visual effect
        this.trail = [];
        this.maxTrailLength = 50;

        // Control state
        this.isPaused = false;
        this.useApi = false;
        this.lastTime = performance.now();
        this.t_elapsed = 0;

        // Measurement state (for averaging match percent over N oscillations)
        this.measuring = false;
        this.measureTargetOscillations = 0;
        this.peakCount = 0;
        this.prevAngularVelocity = 0;
        this.measureSamples = 0;
        this.measureSum = 0;

        // Try to connect to Python API
        this.checkApiConnection();

        // Start animation
        this.animate();
    }

    computeIcm() {
        if (this.shape === 'point') return 0;
        if (this.shape === 'disk') {
            // solid cylinder about center axis
            return 0.5 * this.mass * this.bobSize * this.bobSize;
        }
        if (this.shape === 'sphere') {
            return 0.4 * this.mass * this.bobSize * this.bobSize;
        }
        if (this.shape === 'rod') {
            // thin rod about center perpendicular to length
            return (1/12) * this.mass * this.bobSize * this.bobSize;
        }
        return 0;
    }

    updateInertia() {
        this.I_cm = this.computeIcm();
        this.I_total = Math.max(1e-12, this.I_cm + this.mass * this.length * this.length);
    }

    async checkApiConnection() {
        try {
            const response = await fetch('/api/info');
            if (response.ok) {
                this.useApi = true;
                this.updateModeIndicator(true);
                console.log('Connected to Python API');
            }
        } catch (e) {
            console.log('Python API not available, using local simulation');
            this.useApi = false;
            this.updateModeIndicator(false);
        }
    }

    updateModeIndicator(usingApi) {
        const indicator = document.getElementById('modeIndicator');
        if (usingApi) {
            indicator.className = 'mode-indicator mode-api';
            indicator.textContent = 'Режим Python API';
        } else {
            indicator.className = 'mode-indicator mode-local';
            indicator.textContent = 'Локальная симуляция';
        }
    }

    // Physics calculation (local simulation) - physical pendulum
    update(dt) {
        if (this.isPaused) return;

        // Ensure inertia up-to-date
        this.updateInertia();

        // angular acceleration: α = torque / I_total
        const torque_gravity = - this.mass * this.gravity * this.length * Math.sin(this.angle);
        const angularAcceleration = torque_gravity / this.I_total - this.damping * this.angularVelocity;

        // Euler integration
        this.angularVelocity += angularAcceleration * dt;
        this.angle += this.angularVelocity * dt;
        this.t_elapsed += dt;
    }

    // Analytic (linearized) solution for small angles: θ(t) = θ0 * cos(ω0 * t)
    analyticSolution(t = null) {
        if (t === null) t = this.t_elapsed;
        this.updateInertia();
        const omega0 = Math.sqrt(Math.max(1e-12, (this.mass * this.gravity * this.length) / this.I_total));
        const theta_analytic = this.initialAngle * Math.cos(omega0 * t);
        const omega_analytic = - this.initialAngle * omega0 * Math.sin(omega0 * t);
        return { theta_analytic, omega_analytic, omega0 };
    }

    matchPercent() {
        // New: normalize error by initial amplitude (initialAngle) to avoid instability near theta_analytic ~ 0
        const { theta_analytic } = this.analyticSolution();
        const amplitudeRef = Math.max(Math.abs(this.initialAngle), 1e-3);
        const error = Math.abs(this.angle - theta_analytic);
        const normError = error / amplitudeRef;
        let similarity = Math.max(0, 100 * (1 - normError));
        similarity = Math.max(0, Math.min(100, similarity));
        return similarity;
    }

    async updateFromApi() {
        if (this.isPaused) return;

        try {
            const response = await fetch('/api/state');
            if (response.ok) {
                const state = await response.json();
                // Use server-side values
                this.angle = state.angle;
                this.angularVelocity = state.angularVelocity;
                this.length = state.length;
                this.mass = state.mass !== undefined ? state.mass : this.mass;
                this.damping = state.damping !== undefined ? state.damping : this.damping;
                this.shape = state.shape || this.shape;
                this.bobSize = state.bobSize !== undefined ? state.bobSize : this.bobSize;
                this.t_elapsed = state.time !== undefined ? state.time : this.t_elapsed;
                this.initialAngle = state.analyticAngle !== undefined ? state.analyticAngle : this.initialAngle;
                this.updateInertia();
            }
        } catch (e) {
            // Fallback to local simulation
            this.useApi = false;
            this.updateModeIndicator(false);
        }
    }

    getPosition() {
        const x = this.length * Math.sin(this.angle);
        const y = this.length * Math.cos(this.angle);
        return { x, y };
    }

    getCanvasPosition() {
        const pos = this.getPosition();
        return {
            x: this.pivotX + pos.x * this.scale,
            y: this.pivotY + pos.y * this.scale
        };
    }

    draw() {
        const ctx = this.ctx;
        const { x: bobX, y: bobY } = this.getCanvasPosition();

        // Clear canvas with fade effect for trail
        ctx.fillStyle = 'rgba(15, 15, 26, 0.3)';
        ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Update trail
        this.trail.push({ x: bobX, y: bobY });
        if (this.trail.length > this.maxTrailLength) {
            this.trail.shift();
        }

        // Draw trail
        if (this.trail.length > 1) {
            ctx.beginPath();
            ctx.moveTo(this.trail[0].x, this.trail[0].y);
            for (let i = 1; i < this.trail.length; i++) {
                ctx.lineTo(this.trail[i].x, this.trail[i].y);
            }
            ctx.strokeStyle = 'rgba(76, 175, 80, 0.5)';
            ctx.lineWidth = 2;
            ctx.stroke();
        }

        // Draw pivot point
        ctx.beginPath();
        ctx.arc(this.pivotX, this.pivotY, 10, 0, Math.PI * 2);
        ctx.fillStyle = '#888';
        ctx.fill();
        ctx.strokeStyle = '#aaa';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Draw rod / line
        ctx.beginPath();
        ctx.moveTo(this.pivotX, this.pivotY);
        ctx.lineTo(bobX, bobY);
        ctx.strokeStyle = '#ccc';
        ctx.lineWidth = 3;
        ctx.stroke();

        // Draw bob according to shape
        if (this.shape === 'rod') {
            // Draw a thin rectangle (rod) centered at bob position, oriented along rod
            const rodLen = this.bobSize * this.scale; // visualize using bobSize as rod length
            const rodWidth = Math.max(4, this.bobRadiusVisual / 3);
            const angle = this.angle + Math.PI / 2; // align rod perpendicular to radius for visual
            ctx.save();
            ctx.translate(bobX, bobY);
            ctx.rotate(angle);
            ctx.fillStyle = '#8BC34A';
            ctx.fillRect(-rodLen / 2, -rodWidth / 2, rodLen, rodWidth);
            ctx.strokeStyle = '#1B5E20';
            ctx.lineWidth = 2;
            ctx.strokeRect(-rodLen / 2, -rodWidth / 2, rodLen, rodWidth);
            ctx.restore();
        } else {
            // disk / sphere / point drawn as circle
            const radiusPixels = Math.max(6, this.bobSize * this.scale);
            const gradient = ctx.createRadialGradient(bobX - 8, bobY - 8, 0, bobX, bobY, radiusPixels);
            gradient.addColorStop(0, '#8BC34A');
            gradient.addColorStop(0.5, '#4CAF50');
            gradient.addColorStop(1, '#2E7D32');

            ctx.beginPath();
            ctx.arc(bobX, bobY, radiusPixels, 0, Math.PI * 2);
            ctx.fillStyle = gradient;
            ctx.fill();
            ctx.strokeStyle = '#1B5E20';
            ctx.lineWidth = 2;
            ctx.stroke();
        }

        // Draw angle arc
        ctx.beginPath();
        ctx.moveTo(this.pivotX, this.pivotY);
        ctx.arc(this.pivotX, this.pivotY, 40, Math.PI / 2 - this.angle, Math.PI / 2, this.angle > 0);
        ctx.closePath();
        ctx.fillStyle = 'rgba(33, 150, 243, 0.3)';
        ctx.fill();

        // Update stats display
        this.updateStats();
    }

    updateStats() {
        const pos = this.getPosition();
        document.getElementById('currentAngle').textContent =
            (this.angle * 180 / Math.PI).toFixed(1) + '°';
        document.getElementById('currentVelocity').textContent =
            this.angularVelocity.toFixed(2) + ' rad/s';
        document.getElementById('currentX').textContent =
            pos.x.toFixed(3) + ' m';
        document.getElementById('currentY').textContent =
            pos.y.toFixed(3) + ' m';

        const analytic = this.analyticSolution();
        document.getElementById('analyticAngle').textContent =
            (analytic.theta_analytic * 180 / Math.PI).toFixed(1) + '°';
        document.getElementById('matchPercent').textContent =
            this.matchPercent().toFixed(1) + '%';

        // Measurement UI update
        if (this.measuring) {
            const status = document.getElementById('measurementStatus');
            const resultBox = document.getElementById('measurementResult');
            const oscDone = Math.floor(this.peakCount / 2);
            status.textContent = `Measuring... ${oscDone} / ${this.measureTargetOscillations} oscillations`;
            resultBox.textContent = `${(this.measureSum / Math.max(1, this.measureSamples)).toFixed(2)}% (in progress)`;
        }
    }

    animate() {
        const currentTime = performance.now();
        const dt = Math.min((currentTime - this.lastTime) / 1000, 0.05);
        this.lastTime = currentTime;

        if (this.useApi) {
            this.updateFromApi()
        } else {
            this.update(dt);
        }

        this._measurementStep();

        this.draw();
        requestAnimationFrame(() => this.animate());
    }

    _measurementStep() {
        if (!this.measuring || this.isPaused) {
            this.prevAngularVelocity = this.angularVelocity;
            return;
        }

        const analytic = this.analyticSolution();
        const theta_analytic = analytic.theta_analytic;
        const theta0 = Math.max(Math.abs(this.initialAngle), 1e-3);
        const sampleThreshold = 0.05 * theta0;

        if (Math.abs(theta_analytic) >= sampleThreshold) {
            const mp = this.matchPercent();
            this.measureSum += mp;
            this.measureSamples += 1;
        }

        if (this.prevAngularVelocity > 0 && this.angularVelocity <= 0) {
            this.peakCount += 1;
        }
        this.prevAngularVelocity = this.angularVelocity;

        const completedOscillations = Math.floor(this.peakCount / 2);
        if (completedOscillations >= this.measureTargetOscillations && this.measureTargetOscillations > 0) {
            this.measuring = false;
            const avg = this.measureSum / Math.max(1, this.measureSamples);
            const status = document.getElementById('measurementStatus');
            const resultBox = document.getElementById('measurementResult');
            status.textContent = `Done — measured over ${completedOscillations} oscillations`;
            resultBox.textContent = `${avg.toFixed(2)}% average match`;
        }
    }

    reset(angle, length, damping, shape, bobSize, mass) {
        this.angle = angle;
        this.initialAngle = angle;
        this.length = length;
        this.damping = damping;
        this.angularVelocity = 0;
        this.trail = [];
        this.shape = shape || this.shape;
        this.bobSize = bobSize !== undefined ? bobSize : this.bobSize;
        this.mass = mass !== undefined ? mass : this.mass;
        this.t_elapsed = 0;
        this.updateInertia();

        this.measuring = false;
        this.peakCount = 0;
        this.prevAngularVelocity = 0;
        this.measureSamples = 0;
        this.measureSum = 0;
        this.measureTargetOscillations = 0;
        document.getElementById('measurementStatus').textContent = 'Статус: ожидание';
        document.getElementById('measurementResult').textContent = '—';

        // Also reset on API if connected
        if (this.useApi) {
            fetch(`/api/reset?angle=${angle}&length=${length}&damping=${damping}&shape=${shape}&bobSize=${this.bobSize}&mass=${this.mass}`)
                .catch(err => console.warn('Failed to reset via API:', err));
        }
    }

    startMeasurement(nOscillations) {
        this.measuring = true;
        this.measureTargetOscillations = Math.max(1, Math.floor(nOscillations));
        this.peakCount = 0;
        this.prevAngularVelocity = this.angularVelocity;
        this.measureSamples = 0;
        this.measureSum = 0;
        const status = document.getElementById('measurementStatus');
        const resultBox = document.getElementById('measurementResult');
        status.textContent = `Measuring... 0 / ${this.measureTargetOscillations} oscillations`;
        resultBox.textContent = 'starting...';
    }

    stopMeasurement() {
        this.measuring = false;
        const status = document.getElementById('measurementStatus');
        const resultBox = document.getElementById('measurementResult');
        status.textContent = `Measurement cancelled`;
        resultBox.textContent = '—';
    }

    togglePause() {
        this.isPaused = !this.isPaused;
        return this.isPaused;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const simulation = new PendulumSimulation('pendulumCanvas');

    const lengthInput = document.getElementById('lengthInput');
    const angleInput = document.getElementById('angleInput');
    const dampingInput = document.getElementById('dampingInput');
    const shapeSelect = document.getElementById('shapeSelect');
    const bobSizeInput = document.getElementById('bobSizeInput');
    const resetBtn = document.getElementById('resetBtn');
    const pauseBtn = document.getElementById('pauseBtn');

    const oscCountInput = document.getElementById('oscCountInput');
    const measureBtn = document.getElementById('measureBtn');

    // Validate and clamp input values
    function validateInput(input, min, max) {
        let value = parseFloat(input.value);
        if (isNaN(value)) value = parseFloat(input.defaultValue);
        value = Math.max(min, Math.min(max, value));
        input.value = value;
        return value;
    }

    resetBtn.addEventListener('click', () => {
        const length = validateInput(lengthInput, 0.01, 10);
        const angleDeg = validateInput(angleInput, -180, 180);
        const damping = validateInput(dampingInput, 0, 1);
        const shape = shapeSelect.value;
        const bobSize = validateInput(bobSizeInput, 0.001, 5);
        const angle = angleDeg * Math.PI / 180;
        simulation.reset(angle, length, damping, shape, bobSize);
    });

    pauseBtn.addEventListener('click', () => {
        const isPaused = simulation.togglePause();
        pauseBtn.textContent = isPaused ? 'Воспроизвести' : 'Пауза';
    });

    measureBtn.addEventListener('click', () => {
        // If currently measuring, stop
        if (simulation.measuring) {
            simulation.stopMeasurement();
            measureBtn.textContent = 'Начать измерение';
            return;
        }
        const n = Math.max(1, Math.floor(parseInt(oscCountInput.value) || 1));
        simulation.startMeasurement(n);
        measureBtn.textContent = 'Остановить';
    });
});