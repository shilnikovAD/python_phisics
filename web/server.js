/**
 * Node.js Web Server for Pendulum Demo
 * Serves static files and proxies API requests to Python backend
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 3000;
const PYTHON_API_PORT = 8000;

// MIME types for static files
const mimeTypes = {
    '.html': 'text/html',
    '.js': 'text/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.svg': 'image/svg+xml'
};

// Serve static files
function serveStaticFile(filePath, res) {
    const extname = path.extname(filePath);
    const contentType = mimeTypes[extname] || 'application/octet-stream';
    
    fs.readFile(filePath, (err, content) => {
        if (err) {
            if (err.code === 'ENOENT') {
                res.writeHead(404);
                res.end('File not found');
            } else {
                res.writeHead(500);
                res.end('Server error');
            }
        } else {
            res.writeHead(200, { 'Content-Type': contentType });
            res.end(content);
        }
    });
}

// Proxy request to Python API
function proxyToApi(apiPath, res) {
    const options = {
        hostname: 'localhost',
        port: PYTHON_API_PORT,
        path: apiPath,
        method: 'GET'
    };
    
    const proxyReq = http.request(options, (proxyRes) => {
        res.writeHead(proxyRes.statusCode, proxyRes.headers);
        proxyRes.pipe(res);
    });
    
    proxyReq.on('error', (err) => {
        res.writeHead(503);
        res.end(JSON.stringify({ error: 'Python API not available', message: err.message }));
    });
    
    proxyReq.end();
}

// Create server
const server = http.createServer((req, res) => {
    const url = req.url;
    
    // API requests - proxy to Python backend
    if (url.startsWith('/api/')) {
        proxyToApi(url, res);
        return;
    }
    
    // Static files
    let filePath = path.join(__dirname, 'public', url === '/' ? 'index.html' : url);
    serveStaticFile(filePath, res);
});

server.listen(PORT, () => {
    console.log(`Web server running on http://localhost:${PORT}`);
    console.log(`Make sure Python API is running on port ${PYTHON_API_PORT}`);
    console.log('');
    console.log('To start the demo:');
    console.log('1. Run Python API: python ../pendulum/pendulum.py');
    console.log('2. Open browser: http://localhost:' + PORT);
});