# TermScan Deployment Info

## 🌐 Live URLs

| Environment | URL |
|-------------|-----|
| **Production** | http://72.61.76.62:8000 |
| **Web UI** | http://72.61.76.62:8000 |
| **API Docs** | http://72.61.76.62:8000/docs |
| **Health Check** | http://72.61.76.62:8000/health |

## 🖥️ Server Details

| Item | Value |
|------|-------|
| **Host** | Hostinger VPS (KVM 2) |
| **IP Address** | 72.61.76.62 |
| **Port** | 8000 |
| **Path** | /var/www/termscan |
| **Service** | termscan.service (systemd) |

## 📦 Tech Stack

- **Framework:** FastAPI (Python)
- **AI Provider:** Groq (Llama 3.3 70B)
- **Process Manager:** systemd

## 🔧 Management Commands

```bash
# SSH into server
ssh root@72.61.76.62

# Check service status
systemctl status termscan

# Restart service
systemctl restart termscan

# View logs
journalctl -u termscan -f

# Update code
cd /var/www/termscan && git pull origin main && systemctl restart termscan
```

## 🔑 Environment

Config file: `/var/www/termscan/.env`

Required variables:
- `AI_PROVIDER` (groq, openai, anthropic, gemini)
- `GROQ_API_KEY` (if using Groq)

## 📅 Deployed

- **Date:** December 12, 2025
- **By:** Cascade AI

## 🔗 Future Domain

When ready, point your domain to `72.61.76.62` and update nginx config.
