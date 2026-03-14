/**
 * Document Analyzer Operator - Backend PM2 Configuration
 * PM2 process manager configuration for production deployment.
 * 
 * Usage:
 *   npm install -g pm2
 *   pm2 start ecosystem.config.js --only backend
 */

module.exports = {
  apps: [
    {
      name: 'document-analyzer-backend',
      cwd: './backend',
      script: '.venv/bin/uvicorn',
      args: 'app.main:app --host 0.0.0.0 --port 8000 --workers 4',
      interpreter: 'none',
      instances: 1,
      exec_mode: 'fork',
      
      // Environment variables
      env: {
        NODE_ENV: 'production',
        APP_ENV: 'production',
        APP_DEBUG: 'false',
        APP_RELOAD: 'false',
      },
      
      // Error handling
      error_file: '../logs/pm2-backend-error.log',
      out_file: '../logs/pm2-backend-out.log',
      log_file: '../logs/pm2-backend-combined.log',
      time: true,
      merge_logs: true,
      
      // Restart policy
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s',
      restart_delay: 4000,
      
      // Resource limits
      max_memory_restart: '1G',
      
      // Health check
      health_check: {
        protocol: 'http',
        hostname: 'localhost',
        port: 8000,
        path: '/api/v1/health',
        timeout: 5000,
        interval: 30000,
      },
      
      // Logging
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      
      // Advanced features
      kill_timeout: 3000,
      listen_timeout: 3000,
      
      // Cluster mode settings (if using cluster instead of fork)
      // instances: 4,
      // exec_mode: 'cluster',
    },
  ],
};
