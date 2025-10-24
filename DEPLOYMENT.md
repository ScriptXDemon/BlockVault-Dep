# BlockVault Deployment Guide

This repository contains the deployment-ready version of BlockVault for Render.com.

## Quick Deploy to Render

1. **Fork this repository** to your GitHub account
2. **Connect to Render**:
   - Go to [render.com](https://render.com)
   - Sign up/Login with your GitHub account
   - Click "New +" → "Web Service"
   - Connect your forked repository

3. **Configure the service**:
   - **Name**: `blockvault-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Instance Type**: `Free` (or upgrade as needed)

4. **Set Environment Variables**:
   - `FLASK_ENV`: `production`
   - `SECRET_KEY`: Generate a secure random string
   - `JWT_SECRET`: Generate a secure random string
   - `DB_PATH`: `blockvault.db` (SQLite database file)
   - `CORS_ALLOWED_ORIGINS`: `*` (or your specific domain)

5. **No Database Setup Required**: 
   - SQLite database is file-based and requires no external service
   - Database file will be created automatically on first run
   - No additional costs for database hosting!

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `FLASK_ENV` | Flask environment | Yes | `production` |
| `SECRET_KEY` | Flask secret key | Yes | - |
| `JWT_SECRET` | JWT signing secret | Yes | - |
| `DB_PATH` | SQLite database file path | No | `blockvault.db` |
| `CORS_ALLOWED_ORIGINS` | CORS allowed origins | No | `*` |
| `IPFS_ENABLED` | Enable IPFS integration | No | `false` |
| `IPFS_API_URL` | IPFS API URL | No | - |
| `ETH_RPC_URL` | Ethereum RPC URL (optional) | No | - |
| `ETH_PRIVATE_KEY` | Ethereum private key (optional) | No | - |
| `FILE_REGISTRY_ADDRESS` | File registry contract (optional) | No | - |

## Features

- **Full-stack application**: Backend API + React frontend
- **Encrypted file storage**: Client-side encryption with AES-256-GCM
- **JWT Authentication**: Web3 wallet signature verification
- **File sharing**: RSA-based encrypted passphrase sharing
- **SQLite Database**: File-based database with no external dependencies
- **IPFS Integration**: Optional decentralized storage
- **Blockchain anchoring**: Optional on-chain file hash recording
- **Zero Database Costs**: No MongoDB or external database required!

## API Endpoints

- `GET /` - Frontend application
- `GET /health` - Health check
- `GET /status` - System status and capabilities
- `POST /auth/get_nonce` - Get authentication nonce
- `POST /auth/login` - Login with wallet signature
- `GET /auth/me` - Get current user info
- `POST /files` - Upload encrypted file
- `GET /files` - List user files
- `GET /files/<id>` - Download file
- `DELETE /files/<id>` - Delete file
- `POST /files/<id>/share` - Share file with user
- `GET /files/shared` - Get shared files
- `POST /users/public_key` - Register RSA public key

## Local Development

```bash
# Clone the repository
git clone <your-fork-url>
cd BlockVault-Deploy

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp env.example .env
# Edit .env with your configuration

# Run the application
python app.py
```

## Troubleshooting

- **Build fails**: Check Python version compatibility (3.10+)
- **Database issues**: SQLite database is created automatically, check file permissions
- **CORS errors**: Update CORS_ALLOWED_ORIGINS
- **File upload fails**: Check storage permissions and file size limits

## Security Notes

- Always use strong, unique secrets in production
- Consider using environment-specific CORS origins
- Enable HTTPS in production
- Regularly rotate JWT secrets
- Monitor file storage usage and implement cleanup policies
