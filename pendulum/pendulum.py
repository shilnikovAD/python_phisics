"""
Pendulum Physics Simulation Module
Модуль симуляции физики маятника
"""
import math
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

class Pendulum:
    """Class representing a simple pendulum / Класс простого маятника"""
    
    def __init__(self, length=1.0, mass=1.0, angle=0.5, angular_velocity=0.0, gravity=9.81):
        """
        Initialize pendulum with given parameters
        
        Args:
            length: Length of pendulum in meters
            mass: Mass of pendulum bob in kg
            angle: Initial angle in radians
            angular_velocity: Initial angular velocity in rad/s
            gravity: Gravitational acceleration in m/s^2
        """
        self.length = length
        self.mass = mass
        self.angle = angle
        self.angular_velocity = angular_velocity
        self.gravity = gravity
        self.damping = 0.01  # Small damping factor
        
    def get_angular_acceleration(self):
        """Calculate angular acceleration based on current state"""
        return -(self.gravity / self.length) * math.sin(self.angle) - self.damping * self.angular_velocity
    
    def _get_acceleration_at(self, angle, angular_velocity):
        """Calculate angular acceleration for given angle and velocity"""
        return -(self.gravity / self.length) * math.sin(angle) - self.damping * angular_velocity
    
    def update(self, dt=0.016):
        """
        Update pendulum state using RK4 (Runge-Kutta 4th order) method
        
        Args:
            dt: Time step in seconds
        """
        # RK4 integration for better accuracy and energy conservation
        # k1 - derivative at current state
        k1_angle = self.angular_velocity
        k1_velocity = self._get_acceleration_at(self.angle, self.angular_velocity)
        
        # k2 - derivative at midpoint using k1
        temp_angle = self.angle + 0.5 * dt * k1_angle
        temp_velocity = self.angular_velocity + 0.5 * dt * k1_velocity
        k2_angle = temp_velocity
        k2_velocity = self._get_acceleration_at(temp_angle, temp_velocity)
        
        # k3 - derivative at midpoint using k2
        temp_angle = self.angle + 0.5 * dt * k2_angle
        temp_velocity = self.angular_velocity + 0.5 * dt * k2_velocity
        k3_angle = temp_velocity
        k3_velocity = self._get_acceleration_at(temp_angle, temp_velocity)
        
        # k4 - derivative at endpoint using k3
        temp_angle = self.angle + dt * k3_angle
        temp_velocity = self.angular_velocity + dt * k3_velocity
        k4_angle = temp_velocity
        k4_velocity = self._get_acceleration_at(temp_angle, temp_velocity)
        
        # Weighted average of all derivatives
        self.angle += (dt / 6.0) * (k1_angle + 2*k2_angle + 2*k3_angle + k4_angle)
        self.angular_velocity += (dt / 6.0) * (k1_velocity + 2*k2_velocity + 2*k3_velocity + k4_velocity)
        
    def get_position(self):
        """Get (x, y) position of pendulum bob"""
        x = self.length * math.sin(self.angle)
        y = self.length * math.cos(self.angle)
        return (x, y)
    
    def get_state(self):
        """Get current state as dictionary"""
        x, y = self.get_position()
        return {
            "angle": self.angle,
            "angularVelocity": self.angular_velocity,
            "x": x,
            "y": y,
            "length": self.length,
            "mass": self.mass
        }


class PendulumAPIHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler for Pendulum API"""
    
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
            # Update and return current state
            self.pendulum.update()
            self._set_headers()
            self.wfile.write(json.dumps(self.pendulum.get_state()).encode())
            
        elif parsed_path.path == '/api/reset':
            # Reset pendulum with optional parameters
            query = parse_qs(parsed_path.query)
            try:
                angle = float(query.get('angle', [0.8])[0])
                length = float(query.get('length', [1.0])[0])
                # Validate parameters
                angle = max(-math.pi, min(math.pi, angle))  # Clamp angle to [-π, π]
                length = max(0.1, min(10.0, length))  # Clamp length to [0.1, 10.0]
            except (ValueError, TypeError):
                angle = 0.8
                length = 1.0
            self.pendulum = Pendulum(length=length, angle=angle)
            PendulumAPIHandler.pendulum = self.pendulum
            self._set_headers()
            self.wfile.write(json.dumps({"status": "reset", "state": self.pendulum.get_state()}).encode())
            
        elif parsed_path.path == '/api/info':
            self._set_headers()
            info = {
                "name": "Pendulum Physics API",
                "version": "1.0.0",
                "endpoints": ["/api/state", "/api/reset", "/api/info"]
            }
            self.wfile.write(json.dumps(info).encode())
            
        else:
            self.send_response(404)
            self.end_headers()


def run_server(port=8000):
    """Run the pendulum API server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, PendulumAPIHandler)
    print(f'Pendulum API server running on http://localhost:{port}')
    print('Endpoints: /api/state, /api/reset, /api/info')
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
