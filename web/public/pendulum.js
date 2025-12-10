class PendulumSimulation {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.graphCanvas = document.getElementById('graphCanvas');
        this.graphCtx = this.graphCanvas.getContext('2d');
        this.timeStep = 0.002;
        this.historyTime = [];
        this.historyEnergy = [];
        this.historyNum = [];
        this.historyAnalytic = [];
        this.maxHistoryPoints = 2000;
        
        this.MIN_Y_RANGE = 0.02;
        this.ANGLE_SCALE_FACTOR = 0.1;
        
        this.length = 1.0;
        this.angle = Math.PI / 4;
        this.initialAngle = this.angle;
        this.angularVelocity = 0;
        this.damping = 0.01;
        this.gravity = 9.81;
        this.mass = 1.0;

        this.shape = 'point';
        this.bobSize = 0.05;

        this.I_cm = this.computeIcm();
        this.I_total = Math.max(1e-12, this.I_cm + this.mass * this.length * this.length);

        this.pivotX = this.canvas.width / 2;
        this.pivotY = 100;
        this.scale = 180;
        this.bobRadiusVisual = 25;

        this.trail = [];
        this.maxTrailLength = 50;

        // State
        this.isPaused = false;
        this.useApi = false;
        this.lastTime = performance.now();
        this.t_elapsed = 0;

        this.checkApiConnection();
        this.periodAmplitudeChart = null;
        this.periodDampingChart = null;
        this.periodRefreshInterval = 2.0;
        this.periodAccumulator = 0.0;
        this.initPeriodCharts();
        this.updatePeriodCurves();
        this.renderPeriodCharts();
        this.animate();
    }

    initPeriodCharts() {
        if (!window.Chart) return;
        const ampCtx = document.getElementById('periodAmplitudeChart');
        const dampCtx = document.getElementById('periodDampingChart');
        if (ampCtx) {
            this.periodAmplitudeChart = new Chart(ampCtx, {
                type: 'line',
                data: {labels: [], datasets: [{label: 'T(θ₀)', data: [], borderColor: '#1976d2', fill: false}]},
                options: {responsive: true,
                    scales: {
                        x: {title: {text: 'Амплитуда, рад', display: true}},
                        y: {title: {text: 'Период, с', display: true}}
                    }
                }
            });
        }
        if (dampCtx) {
            this.periodDampingChart = new Chart(dampCtx, {
                type: 'line',
                data: {labels: [], datasets: [{label: 'T(γ)', data: [], borderColor: '#c62828', fill: false}]},
                options: {responsive: true,
                    scales: {
                        x: {title: {text: 'Коэффициент трения', display: true}},
                        y: {title: {text: 'Период, с', display: true}}
                    }
                }
            });
        }
    }

    measurePeriod(angle0, damping) {
        const dt = 0.0005;
        const maxTime = 40.0;
        let angle = angle0;
        let omega = 0.0;
        let prevSign = Math.sign(angle);
        let zeroCrossings = 0;
        const I = this.I_total;
        for (let t = dt; t <= maxTime; t += dt) {
            const torque = -this.mass * this.gravity * this.length * Math.sin(angle);
            const alpha = torque / I - damping * omega;
            omega += alpha * dt;
            angle += omega * dt;
            const sign = Math.sign(angle);
            if (sign === 0 || sign !== prevSign) {
                zeroCrossings++;
                prevSign = sign || prevSign;
                if (zeroCrossings === 2) {
                    return t;
                }
            }
        }
        return NaN;
    }

    updatePeriodCurves() {
        const ampLabels = [];
        const ampData = [];
        for (let a = 0.1; a <= 1.6; a += 0.1) {
            const T = this.measurePeriod(a, this.damping);
            if (isFinite(T)) {
                ampLabels.push(a.toFixed(2));
                ampData.push(T);
            }
        }
        const dampLabels = [];
        const dampData = [];
        for (let d = 0.0; d <= 0.12; d += 0.01) {
            const T = this.measurePeriod(this.initialAngle || 0.5, d);
            if (isFinite(T)) {
                dampLabels.push(d.toFixed(2));
                dampData.push(T);
            }
        }
        this.periodAmplitudeSeries = { labels: ampLabels, data: ampData };
        this.periodDampingSeries = { labels: dampLabels, data: dampData };
    }

    renderPeriodCharts() {
        if (this.periodAmplitudeChart && this.periodAmplitudeSeries) {
            this.periodAmplitudeChart.data.labels = this.periodAmplitudeSeries.labels;
            this.periodAmplitudeChart.data.datasets[0].data = this.periodAmplitudeSeries.data;
            this.periodAmplitudeChart.update('none');
        }
        if (this.periodDampingChart && this.periodDampingSeries) {
            this.periodDampingChart.data.labels = this.periodDampingSeries.labels;
            this.periodDampingChart.data.datasets[0].data = this.periodDampingSeries.data;
            this.periodDampingChart.update('none');
        }
    }
    computeIcm() {
        if (this.shape === 'point') return 0;
        if (this.shape === 'disk')  return 0.5 * this.mass * this.bobSize * this.bobSize;
        if (this.shape === 'sphere') return 0.4 * this.mass * this.bobSize * this.bobSize;
        if (this.shape === 'rod')    return (1/12) * this.mass * this.bobSize * this.bobSize;
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
        if (!indicator) return;
        if (usingApi) {
            indicator.className = 'mode-indicator mode-api';
            indicator.textContent = 'Режим Python API';
        } else {
            indicator.className = 'mode-indicator mode-local';
            indicator.textContent = 'Локальная симуляция';
        }
    }

    update(dt) {
        if (this.isPaused || dt <= 0) return;

        this.updateInertia();

        const torque_gravity = -this.mass * this.gravity * this.length * Math.sin(this.angle);
        const angular_acc_gravity = torque_gravity / this.I_total;

        if (this.damping > 0) {
            this.angularVelocity += angular_acc_gravity * dt;
            this.angularVelocity *= Math.exp(-this.damping * dt);
        } else {
            this.angularVelocity += angular_acc_gravity * dt;
        }

        this.angle += this.angularVelocity * dt;
        this.t_elapsed += dt;
        this.checkEnergyConservation();
        this.periodAccumulator += dt;
        if (this.periodAccumulator >= this.periodRefreshInterval) {
            this.periodAccumulator = 0.0;
            this.updatePeriodCurves();
            this.renderPeriodCharts();
        }
    }

    analyticSolution(t = null) {
        if (t === null) t = this.t_elapsed;
        this.updateInertia();
        const omega0_linear = Math.sqrt(Math.max(1e-12,
            (this.mass * this.gravity * this.length) / this.I_total));
        let omega0;
        const amplitude = Math.abs(this.initialAngle);
        if (amplitude > 1e-6) {
            const freq_correction = 1.0 + (1.0/16.0)*amplitude**2 + (11.0/3072.0)*amplitude**4;
            omega0 = omega0_linear / freq_correction;
        } else {
            omega0 = omega0_linear;
        }

        const beta = 0.5 * this.damping;
        const omega = Math.sqrt(Math.max(1e-12, omega0*omega0 - beta*beta));

        if (omega0*omega0 - beta*beta <= 0) {
            const gamma1 = -beta + Math.sqrt(beta*beta - omega0*omega0);
            const gamma2 = -beta - Math.sqrt(beta*beta - omega0*omega0);
            const A = this.initialAngle * gamma2 / (gamma2 - gamma1);
            const B = this.initialAngle * gamma1 / (gamma1 - gamma2);
            const theta_analytic = A * Math.exp(gamma1 * t) + B * Math.exp(gamma2 * t);
            const omega_analytic = A * gamma1 * Math.exp(gamma1 * t) + B * gamma2 * Math.exp(gamma2 * t);

            return { theta_analytic, omega_analytic, omega0: omega0 };
        }

        const decay = Math.exp(-beta * t);
        const theta_analytic = this.initialAngle * decay * Math.cos(omega * t);
        const omega_analytic =
            - this.initialAngle * decay *
            (beta * Math.cos(omega * t) + omega * Math.sin(omega * t));

        return { theta_analytic, omega_analytic, omega0: omega };
    }

    matchPercent() {
        const { theta_analytic } = this.analyticSolution();
        const amplitudeRef = Math.max(Math.abs(this.initialAngle), 1e-3);
        const error = Math.abs(this.angle - theta_analytic);
        const norm = error / amplitudeRef;

        if (norm <= 0.1) return 100;
        const clipped = Math.min(norm, 0.5);
        const similarity = 100 * (1 - (clipped - 0.1) / 0.4);
        return Math.max(0, similarity);
    }

    async updateFromApi() {
        if (this.isPaused) return;

        try {
            const response = await fetch('/api/state');
            if (response.ok) {
                const state = await response.json();
                this.angle = state.angle;
                this.angularVelocity = state.angularVelocity;
                this.length = state.length;
                this.mass = state.mass !== undefined ? state.mass : this.mass;
                this.damping = state.damping !== undefined ? state.damping : this.damping;
                this.shape = state.shape || this.shape;
                this.bobSize = state.bobSize !== undefined ? state.bobSize : this.bobSize;
                this.t_elapsed = state.time !== undefined ? state.time : this.t_elapsed;
                this.initialAngle = state.initialAngle !== undefined ? state.initialAngle : this.initialAngle;
                this.updateInertia();
            }
        } catch (e) {
            this.useApi = false;
            this.updateModeIndicator(false);
        }
    }

    getPosition() {
        const x = this.length * Math.sin(this.angle);
        const y = this.length * Math.cos(this.angle);
        return { x, y };
    }

    computeEnergy() {
    this.updateInertia();
    const Ek = 0.5 * this.I_total * this.angularVelocity * this.angularVelocity;
    const Ep = this.mass * this.gravity * this.length * (1 - Math.cos(this.angle));
    return Ek + Ep;
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

        ctx.fillStyle = 'rgba(15, 15, 26, 0.3)';
        ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        this.trail.push({ x: bobX, y: bobY });
        if (this.trail.length > this.maxTrailLength) this.trail.shift();

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

        ctx.beginPath();
        ctx.arc(this.pivotX, this.pivotY, 10, 0, Math.PI * 2);
        ctx.fillStyle = '#888';
        ctx.fill();
        ctx.strokeStyle = '#aaa';
        ctx.lineWidth = 2;
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(this.pivotX, this.pivotY);
        ctx.lineTo(bobX, bobY);
        ctx.strokeStyle = '#ccc';
        ctx.lineWidth = 3;
        ctx.stroke();

        if (this.shape === 'rod') {
            const rodLen = this.bobSize * this.scale;
            const rodWidth = Math.max(4, this.bobRadiusVisual / 3);
            const angle = this.angle + Math.PI / 2;
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

        ctx.beginPath();
        ctx.moveTo(this.pivotX, this.pivotY);
        ctx.arc(this.pivotX, this.pivotY, 40,
                Math.PI / 2 - this.angle, Math.PI / 2,
                this.angle > 0);
        ctx.closePath();
        ctx.fillStyle = 'rgba(33, 150, 243, 0.3)';
        ctx.fill();

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

        const { theta_analytic } = this.analyticSolution();
        if (Math.random() < 0.01) {
            console.log('angle=', this.angle, 'analytic=', theta_analytic);
        }
        const energyElem = document.getElementById('energyDeviation');
        if (energyElem) {
            energyElem.textContent = (this.energyViolation * 100).toFixed(3) + '%';
        }
    }

    checkEnergyConservation() {
        const energy = this.computeEnergy();
        if (!isFinite(this.initialEnergy) || this.initialEnergy <= 0) {
            this.initialEnergy = energy;
        }
        const deviation = Math.abs(energy - this.initialEnergy) / Math.max(1e-12, this.initialEnergy);
        this.energyViolation = deviation;
        if (deviation > this.energyTolerance) {
            console.warn(`Energy drift ${(deviation * 100).toFixed(3)}%`);
        }
        this.lastEnergy = energy;
        return energy;
    }

    animate() {
        const currentTime = performance.now();
        const delta = currentTime - this.lastTime;
        this.lastTime = currentTime;

        if (this.useApi) {
            this.updateFromApi();
        } else {
            const fixedTimeStep = this.timeStep;

            let accumulatedTime = delta / 1000;
            const maxSteps = 10;

            let steps = 0;
            while (accumulatedTime > 0 && steps < maxSteps) {
                const dt = Math.min(fixedTimeStep, accumulatedTime);
                this.update(dt);
                accumulatedTime -= dt;
                steps++;
            }
        }
        const { theta_analytic } = this.analyticSolution();
        this.historyTime.push(this.t_elapsed);
        this.historyNum.push(this.angle);
        this.historyAnalytic.push(theta_analytic);
        this.historyEnergy.push(this.lastEnergy || this.computeEnergy());

        if (this.historyTime.length > this.maxHistoryPoints) {
            this.historyTime.shift();
            this.historyNum.shift();
            this.historyAnalytic.shift();
            this.historyEnergy.shift();

        }

        this.draw();
        this.drawGraphs();
        requestAnimationFrame(() => this.animate());
    }

    drawGraphs() {
        const ctx = this.graphCtx;
        const w = this.graphCanvas.width;
        const h = this.graphCanvas.height;

        ctx.clearRect(0, 0, w, h);

        if (this.historyTime.length < 2) return;

        const t0 = this.historyTime[0];
        const t1 = this.historyTime[this.historyTime.length - 1];
        const dt = t1 - t0 || 1;

        const allY = this.historyNum.concat(this.historyAnalytic);
        const ymin = Math.min(...allY);
        const ymax = Math.max(...allY);
        
        const minRange = Math.max(this.MIN_Y_RANGE, Math.abs(this.initialAngle) * this.ANGLE_SCALE_FACTOR);
        const dy = Math.max(ymax - ymin, minRange);
        
        const center = (ymin + ymax) / 2;
        const yminAdjusted = center - dy / 2;

        const toX = t => ((t - t0) / dt) * w;
        const toY = y => h - ((y - yminAdjusted) / dy) * h;

        // Численное (зелёное)
        ctx.beginPath();
        this.historyNum.forEach((y, i) => {
            const x = toX(this.historyTime[i]);
            const yy = toY(y);
            if (i === 0) ctx.moveTo(x, yy); else ctx.lineTo(x, yy);
        });
        ctx.strokeStyle = '#4CAF50';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Аналитическое (синее)
        ctx.beginPath();
        this.historyAnalytic.forEach((y, i) => {
            const x = toX(this.historyTime[i]);
            const yy = toY(y);
            if (i === 0) ctx.moveTo(x, yy); else ctx.lineTo(x, yy);
        });
        ctx.strokeStyle = '#2196F3';
        ctx.lineWidth = 2;
        ctx.stroke();
    }

    computeAccuracy() {
        const n = this.historyNum.length;
        if (n < 10) return null;

        const amp = Math.max(Math.abs(this.initialAngle), 1e-3);

        let sumSq = 0;
        let maxError = 0;
        let validPoints = 0;

        for (let i = 0; i < n; i++) {
            if (!isNaN(this.historyAnalytic[i])) {
                const err = (this.historyNum[i] - this.historyAnalytic[i]) / amp;
                sumSq += err * err;
                maxError = Math.max(maxError, Math.abs(err));
                validPoints++;
            }
        }

        if (validPoints < 5) return null;

        const rms = Math.sqrt(sumSq / validPoints);
        const similarity = Math.max(0, 100 * (1 - Math.min(rms, 1)));

        return {
            rms,
            similarity,
            maxError,
            points: validPoints
        };
    }

    reset(angle, length, damping, shape, bobSize, mass) {
        this.angle = angle;
        this.initialAngle = angle;
        this.length = length;
        this.damping = damping;
        this.angularVelocity = 0;
        this.trail = [];
        this.historyEnergy = [];
        this.shape = shape || this.shape;
        this.bobSize = bobSize !== undefined ? bobSize : this.bobSize;
        this.mass = mass !== undefined ? mass : this.mass;
        this.t_elapsed = 0;
        this.updateInertia();

        this.initialEnergy = this.computeEnergy();
        this.lastEnergy = this.initialEnergy;
        this.energyViolation = 0;

        this.historyTime = [];
        this.historyNum = [];
        this.historyAnalytic = [];

        if (this.useApi) {
            fetch(`/api/reset?angle=${angle}&length=${length}&damping=${damping}` +
                  `&shape=${shape}&bobSize=${this.bobSize}&mass=${this.mass}`)
                .catch(err => console.warn('Failed to reset via API:', err));
        }
    }

    togglePause() {
        this.isPaused = !this.isPaused;
        return this.isPaused;
    }
}

//  UI
document.addEventListener('DOMContentLoaded', () => {
    const simulation = new PendulumSimulation('pendulumCanvas');

    const measureBtn = document.getElementById('measureBtn');
    const measurementStatus = document.getElementById('measurementStatus');
    const measurementResult = document.getElementById('measurementResult');
    const lengthInput = document.getElementById('lengthInput');
    const angleInput = document.getElementById('angleInput');
    const dampingInput = document.getElementById('dampingInput');
    const shapeSelect = document.getElementById('shapeSelect');
    const bobSizeInput = document.getElementById('bobSizeInput');
    const resetBtn = document.getElementById('resetBtn');
    const pauseBtn = document.getElementById('pauseBtn');
    const oscillationCountInput = document.getElementById('oscillationCountInput');

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

        measurementStatus.textContent = 'Статус: ожидание измерений';
        measurementResult.textContent = '—';
    });

    pauseBtn.addEventListener('click', () => {
        const isPaused = simulation.togglePause();
        pauseBtn.textContent = isPaused ? 'Воспроизвести' : 'Пауза';
    });

    measureBtn.addEventListener('click', () => {
        const nOscillations = parseInt(oscillationCountInput.value) || 5;

        setTimeout(() => {
            const accuracy = simulation.computeAccuracy();

            if (!accuracy) {
                measurementStatus.textContent = 'Статус: недостаточно данных';
                measurementResult.textContent = '—';
                return;
            }

            measurementStatus.textContent = `Статус: измерено по ${nOscillations} колебаниям`;
            measurementResult.textContent =
                `${accuracy.similarity.toFixed(2)}% (RMS ошибка = ${accuracy.rms.toFixed(6)})`;

            if (accuracy.similarity > 95) {
                measurementResult.style.color = '#2E7D32';
            } else if (accuracy.similarity > 80) {
                measurementResult.style.color = '#FF9800';
            } else {
                measurementResult.style.color = '#D32F2F';
            }
        }, 100);
    });
});