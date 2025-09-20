# Scripts Directory

This directory contains utility scripts for managing the NeuraCRM application.

## Security Notice 🔒

**All scripts now use secure environment variables instead of hardcoded credentials.**

### Setup

1. Copy `.env.example` to `.env` in the project root:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your actual database credentials:
   ```env
   RAILWAY_DB_HOST=your-railway-host.rlwy.net
   RAILWAY_DB_DATABASE=railway
   RAILWAY_DB_USER=postgres
   RAILWAY_DB_PASSWORD=your-railway-password
   RAILWAY_DB_PORT=your-railway-port
   ```

3. Install required dependencies:
   ```bash
   pip install python-dotenv psycopg2-binary
   ```

### Running Scripts

All scripts automatically load environment variables from the `.env` file:

```bash
python scripts/check_railway_customer_segments.py
```

### Database Configuration

Scripts use the `db_config.py` module to securely load database credentials:

- `get_railway_db_config()` - Returns Railway database configuration
- `get_local_db_config()` - Returns local database configuration  
- `validate_config()` - Validates all required environment variables are set

### Script Categories

- **Check Scripts**: Verify data and schema (`check_*`)
- **Seed Scripts**: Populate database with sample data (`seed_*`)
- **Fix Scripts**: Repair data or schema issues (`fix_*`)
- **Test Scripts**: Test functionality (`test_*`)
- **Deploy Scripts**: Deploy changes (`deploy_*`, `railway_*`)

### Security Features

- ✅ No hardcoded credentials in source code
- ✅ Environment variables for all sensitive data
- ✅ `.env` file excluded from version control
- ✅ Template file (`.env.example`) for easy setup
- ✅ Validation of required environment variables
