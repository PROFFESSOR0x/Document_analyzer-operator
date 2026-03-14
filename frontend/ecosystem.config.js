/**
 * Document Analyzer Operator - Frontend PM2 Configuration
 * PM2 process manager configuration for production deployment.
 * 
 * Usage:
 *   npm install -g pm2
 *   pm2 start ecosystem.config.js --only frontend
 */

module.exports = {
  apps: [
    {
      name: 'document-analyzer-frontend',
      cwd: './frontend',
      script: 'npm',
      args: 'run start',
      instances: 1,
      exec_mode: 'fork',
      
      // Environment variables
      env: {
        NODE_ENV: 'production',
        PORT: 3000,
        NEXT_PUBLIC_API_URL: 'http://localhost:8000',
        NEXT_PUBLIC_WS_URL: 'ws://localhost:8000',
      },
      
      // Error handling
      error_file: '../logs/pm2-frontend-error.log',
      out_file: '../logs/pm2-frontend-out.log',
      log_file: '../logs/pm2-frontend-combined.log',
      time: true,
      merge_logs: true,
      
      // Restart policy
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s',
      restart_delay: 4000,
      
      // Resource limits
      max_memory_restart: '500M',
      
      // Health check
      health_check: {
        protocol: 'http',
        hostname: 'localhost',
        port: 3000,
        path: '/',
        timeout: 5000,
        interval: 30000,
      },
      
      // Logging
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      
      // Advanced features
      kill_timeout: 3000,
      listen_timeout: 3000,
    },
  ],
};
