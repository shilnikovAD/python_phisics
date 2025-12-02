/**
 * Pendulum Physics Simulation - JavaScript Frontend
 * Симуляция физики маятника - JavaScript фронтенд
 */

class PendulumSimulation {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        
        // Pendulum properties
        this.length = 1.0;
        this.angle = Math.PI / 4; // 45 degrees
        this.angularVelocity = 0;
        this.damping = 0.01;
        this.gravity = 9.81;
        
        // Visualization properties
        this.pivotX = this.canvas.width / 2;
        this.pivotY = 100;
        this.scale = 180; // pixels per meter
        this.bobRadius = 25;
        
        // Trail for visual effect
        this.trail = [];
        this.maxTrailLength = 50;
        
        // Control state
        this.isPaused = false;
        this.useApi = false;
        this.lastTime = performance.now();
        
        // Try to connect to Python API
        this.checkApiConnection();
        
        // Start animation
        this.animate();
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
            indicator.textContent = 'Python API Mode / Режим Python API';
        } else {
            indicator.className = 'mode-indicator mode-local';
            indicator.textContent = 'Local Simulation / Локальная симуляция';
        }
    }
    
    // Physics calculation (local simulation)
    update(dt) {
        if (this.isPaused) return;
        
        // Angular acceleration: α = -(g/L) * sin(θ) - damping * ω
        const angularAcceleration = -(this.gravity / this.length) * Math.sin(this.angle) 
                                    - this.damping * this.angularVelocity;
        
        // Euler integration
        this.angularVelocity += angularAcceleration * dt;
        this.angle += this.angularVelocity * dt;
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
        
        // Draw rod
        ctx.beginPath();
        ctx.moveTo(this.pivotX, this.pivotY);
        ctx.lineTo(bobX, bobY);
        ctx.strokeStyle = '#ccc';
        ctx.lineWidth = 3;
        ctx.stroke();
        
        // Draw bob with gradient
        const gradient = ctx.createRadialGradient(bobX - 8, bobY - 8, 0, bobX, bobY, this.bobRadius);
        gradient.addColorStop(0, '#8BC34A');
        gradient.addColorStop(0.5, '#4CAF50');
        gradient.addColorStop(1, '#2E7D32');
        
        ctx.beginPath();
        ctx.arc(bobX, bobY, this.bobRadius, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();
        ctx.strokeStyle = '#1B5E20';
        ctx.lineWidth = 2;
        ctx.stroke();
        
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
    }
    
    animate() {
        const currentTime = performance.now();
        const dt = Math.min((currentTime - this.lastTime) / 1000, 0.05); // Cap at 50ms
        this.lastTime = currentTime;
        
        if (this.useApi) {
            this.updateFromApi();
        } else {
            this.update(dt);
        }
        
        this.draw();
        requestAnimationFrame(() => this.animate());
    }
    
    reset(angle, length, damping) {
        this.angle = angle;
        this.length = length;
        this.damping = damping;
        this.angularVelocity = 0;
        this.trail = [];
        
        // Also reset on API if connected
        if (this.useApi) {
            fetch(`/api/reset?angle=${angle}&length=${length}`)
                .catch(err => console.warn('Failed to reset via API:', err));
        }
    }
    
    togglePause() {
        this.isPaused = !this.isPaused;
        return this.isPaused;
    }
}

// Initialize simulation when page loads
document.addEventListener('DOMContentLoaded', () => {
    const simulation = new PendulumSimulation('pendulumCanvas');
    
    // Control elements
    const lengthInput = document.getElementById('lengthInput');
    const angleInput = document.getElementById('angleInput');
    const dampingInput = document.getElementById('dampingInput');
    const resetBtn = document.getElementById('resetBtn');
    const pauseBtn = document.getElementById('pauseBtn');
    
    // Validate and clamp input values
    function validateInput(input, min, max) {
        let value = parseFloat(input.value);
        if (isNaN(value)) value = parseFloat(input.defaultValue);
        value = Math.max(min, Math.min(max, value));
        input.value = value;
        return value;
    }
    
    // Reset button
    resetBtn.addEventListener('click', () => {
        const length = validateInput(lengthInput, 0.1, 10);
        const angleDeg = validateInput(angleInput, -180, 180);
        const damping = validateInput(dampingInput, 0, 1);
        const angle = angleDeg * Math.PI / 180;
        simulation.reset(angle, length, damping);
    });
    
    // Pause button
    pauseBtn.addEventListener('click', () => {
        const isPaused = simulation.togglePause();
        pauseBtn.textContent = isPaused ? '▶️ Play / Воспроизвести' : '⏸️ Pause / Пауза';
    });
});
