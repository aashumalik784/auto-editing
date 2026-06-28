# Deployment Guide

## Frontend Deployment (Cloudflare Pages)

### 1. Push to GitHub
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Connect to Cloudflare Pages

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com)
2. Navigate to **Workers & Pages**
3. Click **Create**
4. Select **Pages**
5. Click **Connect to Git**
6. Select your GitHub repository
7. Configure build settings:
   - **Build command:** (leave empty)
   - **Build output directory:** `frontend`
8. Click **Save and Deploy**

### 3. Custom Domain (Optional)

1. Go to your Pages project
2. Click **Custom domains**
3. Click **Set up a custom domain**
4. Enter your domain (e.g., `auto-editing.com`)
5. Follow DNS configuration instructions

## Backend Deployment

### Option 1: VPS (DigitalOcean, AWS, etc.)

#### 1. Setup Server

```bash
# SSH into server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Install Python and dependencies
apt install python3-pip python3-venv ffmpeg git -y

# Clone repository
git clone https://github.com/yourusername/auto-editing.gitcd auto-editing/backend
```

#### 2. Setup Application

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env
# Add your configuration
```

#### 3. Setup Systemd Service

```bash
nano /etc/systemd/system/auto-editing.service
```

Add:
```ini
[Unit]
Description=Auto-Editing Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/auto-editing/backend
Environment="PATH=/root/auto-editing/backend/venv/bin"
ExecStart=/root/auto-editing/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
systemctl daemon-reload
systemctl enable auto-editing
systemctl start auto-editing
systemctl status auto-editing
```
#### 4. Setup Nginx Reverse Proxy

```bash
apt install nginx -y
nano /etc/nginx/sites-available/auto-editing
```

Add:
```nginx
server {
    listen 80;
    server_name api.auto-editing.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        client_max_body_size 500M;
    }
}
```

Enable:
```bash
ln -s /etc/nginx/sites-available/auto-editing /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

#### 5. Setup SSL (Let's Encrypt)

```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d api.auto-editing.com
```

### Option 2: Docker Deployment

#### 1. Build Image

```bash
cd backend
docker build -t auto-editing-backend .
```

#### 2. Run Container

```bash
docker run -d \  --name auto-editing \
  -p 8000:8000 \
  -v $(pwd)/storage:/app/storage \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  auto-editing-backend
```

#### 3. Docker Compose (Recommended)

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/storage:/app/storage
      - ./backend/logs:/app/logs
    environment:
      - HOST=0.0.0.0
      - PORT=8000
      - DEBUG=False
    restart: unless-stopped
```

Run:
```bash
docker-compose up -d
```

### Option 3: Cloudflare Workers (Lightweight Tasks)

```bash
cd workers

# Install Wrangler
npm install -g wrangler

# Login to Cloudflare
wrangler login

# Deploy
wrangler deploy
```

## Database Deployment
### PostgreSQL Setup

```bash
# Install PostgreSQL
apt install postgresql postgresql-contrib -y

# Create database and user
sudo -u postgres psql

CREATE DATABASE auto_editing;
CREATE USER auto_editing_user WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE auto_editing TO auto_editing_user;
\q

# Run schema
psql -U auto_editing_user -d auto_editing -f database/schema.sql
```

## Environment Variables

Update your `.env` file with production values:

```env
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Update API URL in frontend
# frontend/js/api.js: API_BASE_URL = 'https://api.auto-editing.com'
```

## Monitoring

### Check Logs

```bash
# Backend logs
journalctl -u auto-editing -f

# Application logs
tail -f backend/logs/app.log

# Docker logs
docker logs -f auto-editing
```

### Health Check

```bashcurl https://api.auto-editing.com/
```

## Security Checklist

- [ ] Change DEBUG to False
- [ ] Use strong passwords
- [ ] Enable HTTPS/SSL
- [ ] Set up firewall (ufw)
- [ ] Regular backups
- [ ] Update dependencies regularly
- [ ] Monitor logs for errors
- [ ] Set up rate limiting
- [ ] Configure CORS properly

## Backup Strategy

```bash
# Backup storage
tar -czf backup-$(date +%Y%m%d).tar.gz backend/storage/

# Backup database (if using PostgreSQL)
pg_dump auto_editing > backup-$(date +%Y%m%d).sql

# Automate with cron
crontab -e
# Add: 0 2 * * * /path/to/backup/script.sh
```

## Scaling

### Horizontal Scaling

1. Use load balancer (Nginx, HAProxy)
2. Run multiple backend instances
3. Use shared storage (S3, NFS)
4. Use external database

### Vertical Scaling

1. Increase server resources (CPU, RAM)
2. Optimize FFmpeg settings
3. Use faster storage (SSD)

## Troubleshooting

### Service won't start
```bash
journalctl -u auto-editing -n 50
```
### High memory usage
```bash
# Check processes
htop

# Restart service
systemctl restart auto-editing
```

### Disk full
```bash
# Check disk usage
df -h

# Clean up old files
find backend/storage/temp -type f -mtime +7 -delete
```

## Support

For issues, check:
1. Application logs
2. System logs
3. Documentation
4. GitHub Issues
