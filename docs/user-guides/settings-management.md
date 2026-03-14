# Settings Management Quick Start Guide

## 🎯 Overview

The Document-Analyzer-Operator Platform now features a comprehensive **UI-based settings management system** that allows admin users to configure all environment variables and application settings directly from the dashboard.

---

## ✨ Features

- 🔐 **Encrypted Storage** - All secrets encrypted with Fernet
- 📝 **Audit Logging** - Complete history of all changes
- 🔍 **Search & Filter** - Find settings quickly
- 📤 **Export/Import** - Backup and restore settings
- 🔄 **Bulk Operations** - Update multiple settings at once
- ✅ **Validation** - Client and server-side validation
- 👥 **Admin Only** - Role-based access control
- 📊 **Categories** - Organized by function

---

## 🚀 Quick Start

### 1. Generate Encryption Key

```bash
# Generate encryption key for secrets
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Save this key!** You'll need it for the `.env` file.

### 2. Update Environment

Edit `backend/.env`:

```bash
# Add the encryption key
ENCRYPTION_KEY=<your_generated_key_here>
```

### 3. Run Migration

```bash
cd backend
poetry run alembic upgrade head
```

This creates:
- `application_settings` table
- `setting_audit_logs` table
- Seeds default settings from environment

### 4. Restart Backend

```bash
poetry run uvicorn app.main:app --reload
```

### 5. Access Settings UI

Navigate to: **http://localhost:3000/dashboard/settings/management**

(Requires admin or superadmin role)

---

## 📋 Using the Settings UI

### View Settings by Category

1. Go to **Settings → Management**
2. Click on a category card:
   - 🧠 **LLM Providers** - LLM configuration
   - 💾 **Database** - Database settings
   - 🔴 **Redis** - Redis configuration
   - 🔒 **Security** - Security settings
   - ⚙️ **Application** - App configuration
   - 🎨 **UI** - UI preferences

### Edit a Setting

1. Navigate to the category
2. Find the setting you want to change
3. Click **Edit** button
4. Enter new value
5. (Optional) Add reason for change
6. Click **Save**
7. Confirm if it's a critical setting

### View Audit Log

1. Go to **Settings → Audit Log**
2. See timeline of all changes
3. Filter by:
   - Setting key
   - User who made change
   - Date range
4. Click on entry to see details

### Export Settings

1. Go to **Settings → Management**
2. Click **Export** button
3. Download JSON file
4. Store securely (contains secrets!)

### Import Settings

1. Go to **Settings → Management**
2. Click **Import** button
3. Select JSON file
4. Choose import mode:
   - **Merge** - Only import missing settings
   - **Overwrite** - Replace existing settings
5. Click **Import**
6. Review changes
7. Confirm

---

## 🔧 Available Settings

### LLM Providers Category

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `llm.default_provider` | string | openai | Default LLM provider |
| `llm.openai_api_key` | secret | - | OpenAI API key |
| `llm.openai_base_url` | string | https://api.openai.com/v1 | OpenAI base URL |
| `llm.anthropic_api_key` | secret | - | Anthropic API key |
| `llm.groq_api_key` | secret | - | Groq API key |
| `llm.temperature` | float | 0.7 | Default temperature |
| `llm.max_tokens` | integer | 4096 | Default max tokens |

### Database Category

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `database.pool_size` | integer | 5 | Connection pool size |
| `database.pool_timeout` | integer | 30 | Pool timeout (seconds) |
| `database.echo_sql` | boolean | false | Echo SQL queries |

### Redis Category

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `redis.db` | integer | 0 | Redis database number |
| `redis.ttl` | integer | 3600 | Default TTL (seconds) |

### Security Category

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `security.jwt_expiry_minutes` | integer | 30 | JWT token expiry |
| `security.max_login_attempts` | integer | 5 | Max login attempts |
| `security.session_timeout_minutes` | integer | 60 | Session timeout |
| `security.cors_origins` | json | ["http://localhost:3000"] | CORS origins |

### Application Category

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `app.debug` | boolean | false | Debug mode |
| `app.log_level` | string | INFO | Log level |
| `app.workers` | integer | 4 | Number of workers |
| `app.max_upload_size_mb` | integer | 10 | Max upload size (MB) |

### UI Category

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `ui.theme` | string | system | Default theme |
| `ui.page_size` | integer | 20 | Default page size |
| `ui.enable_websocket` | boolean | true | Enable WebSocket |

---

## 🔐 Security Features

### Encryption

All secret values are encrypted using **Fernet encryption** (symmetric encryption).

```python
# Encryption happens automatically in SettingsService
setting = await service.update_setting(
    key="llm.openai_api_key",
    value="sk-...",  # Automatically encrypted
    user_id=user_id,
    reason="Updated API key"
)
```

### Access Control

- Only users with **admin** or **superadmin** role can access settings
- Secret values are **masked** in API responses
- All changes are **logged** with user ID and timestamp
- Critical settings require **confirmation dialog**

### Audit Trail

Every change creates an audit log entry:

```json
{
  "id": "uuid",
  "setting_key": "llm.temperature",
  "old_value": "0.7",
  "new_value": "0.8",
  "changed_by": {
    "id": "uuid",
    "email": "admin@example.com"
  },
  "change_reason": "Testing higher temperature",
  "created_at": "2026-03-13T10:00:00Z"
}
```

---

## 📊 API Reference

### Get All Settings

```http
GET /api/v1/settings
Authorization: Bearer <token>
```

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "key": "llm.temperature",
      "value": "0.7",
      "value_type": "float",
      "category": "llm",
      "description": "Default temperature",
      "is_secret": false,
      "is_editable": true,
      "updated_at": "2026-03-13T10:00:00Z"
    }
  ],
  "total": 25
}
```

### Get Settings by Category

```http
GET /api/v1/settings/category/llm
Authorization: Bearer <token>
```

### Update Setting

```http
PUT /api/v1/settings/llm.temperature
Authorization: Bearer <token>
Content-Type: application/json

{
  "value": "0.8",
  "reason": "Testing higher temperature"
}
```

### Bulk Update Settings

```http
PUT /api/v1/settings/bulk
Authorization: Bearer <token>
Content-Type: application/json

{
  "settings": {
    "llm.temperature": 0.8,
    "llm.max_tokens": 2048,
    "app.debug": false
  },
  "reason": "Production configuration"
}
```

### Reset Setting to Default

```http
POST /api/v1/settings/llm.temperature/reset
Authorization: Bearer <token>
```

### Get Audit Log

```http
GET /api/v1/settings/llm.temperature/audit?limit=50
Authorization: Bearer <token>
```

### Export Settings

```http
POST /api/v1/settings/export
Authorization: Bearer <token>
```

**Response:** JSON file download

### Import Settings

```http
POST /api/v1/settings/import
Authorization: Bearer <token>
Content-Type: multipart/form-data

FormData:
  file: <settings.json>
  overwrite: false
```

---

## 🔧 Advanced Usage

### Using Settings in Code

```python
from app.core.runtime_settings import get_runtime_settings

# Get runtime settings instance
settings = get_runtime_settings()

# Access settings with type safety
temperature = settings.get_float("llm.temperature", default=0.7)
debug_mode = settings.get_bool("app.debug", default=False)
api_key = settings.get_secret("llm.openai_api_key")
cors_origins = settings.get_json("security.cors_origins")

# Settings are cached in Redis for performance
# Auto-reload on changes (if enabled)
```

### Programmatic Updates

```python
from app.services.settings_service import SettingsService

service = SettingsService()

# Update single setting
await service.update_setting(
    key="llm.temperature",
    value="0.8",
    user_id=current_user.id,
    reason="Adjusting for better creativity"
)

# Bulk update
updates = {
    "llm.temperature": "0.8",
    "llm.max_tokens": "2048",
    "app.debug": "false"
}
await service.bulk_update_settings(
    settings_dict=updates,
    user_id=current_user.id,
    reason="Production deployment"
)

# Export settings
export_data = await service.export_settings(user_id=current_user.id)

# Import settings
results = await service.import_settings(
    settings_json=export_data,
    user_id=current_user.id,
    overwrite=False
)
```

### Validation

```python
from app.services.settings_service import SettingsService

service = SettingsService()

# Validate before saving
try:
    is_valid = await service.validate_setting(
        key="llm.temperature",
        value="1.5"  # Out of range
    )
except ValueError as e:
    print(f"Validation error: {e}")
```

---

## ⚠️ Important Notes

### Settings Requiring Restart

Some settings require a backend restart to take effect:

- `app.workers` - Number of workers
- `database.pool_size` - Connection pool size
- `database.pool_timeout` - Pool timeout
- `app.log_level` - Log level

The UI will show a **⚠️ Restart Required** badge for these settings.

### Critical Settings

Some settings are critical and require confirmation:

- `security.jwt_expiry_minutes` - Token expiry
- `security.cors_origins` - CORS allowed origins
- `app.debug` - Debug mode (security risk if enabled in production)

### Best Practices

1. **Always add a reason** when changing settings
2. **Export settings** before making bulk changes
3. **Test in development** before production
4. **Review audit log** regularly
5. **Rotate secrets** periodically
6. **Backup encryption key** securely

---

## 🐛 Troubleshooting

### Issue: "Cannot access settings page"

**Solution:**
- Verify you have admin or superadmin role
- Check authentication token is valid
- Ensure backend is running

### Issue: "Encryption key not set"

**Solution:**
```bash
# Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Add to .env
echo "ENCRYPTION_KEY=<generated_key>" >> backend/.env

# Restart backend
```

### Issue: "Settings not saving"

**Solution:**
- Check database connection
- Verify migration ran: `alembic current`
- Check logs for errors: `tail -f backend/logs/app.log`

### Issue: "Secret values showing as plain text"

**Solution:**
- This is normal in database (encrypted)
- API responses mask secrets automatically
- UI shows •••••• for secret fields

---

## 📚 Additional Resources

- **Full Documentation**: [backend/docs/SETTINGS_MANAGEMENT.md](backend/docs/SETTINGS_MANAGEMENT.md)
- **Implementation Summary**: [docs/SETTINGS_IMPLEMENTATION_SUMMARY.md](docs/SETTINGS_IMPLEMENTATION_SUMMARY.md)
- **API Documentation**: http://localhost:8000/docs
- **Audit Log Guide**: [docs/SETTINGS_AUDIT_GUIDE.md](docs/SETTINGS_AUDIT_GUIDE.md)

---

## 🎯 Next Steps

1. ✅ **Configure LLM Providers** - Set up your API keys
2. ✅ **Adjust Security Settings** - Customize token expiry, CORS
3. ✅ **Optimize Database** - Tune pool size and timeout
4. ✅ **Customize UI** - Set theme and preferences
5. ✅ **Export Backup** - Save your configuration
6. ✅ **Review Audit Log** - Monitor changes

---

**Version:** 1.0.0  
**Last Updated:** 2026-03-13  
**Status:** ✅ Production Ready  
**Access:** Admin/Superadmin Only
