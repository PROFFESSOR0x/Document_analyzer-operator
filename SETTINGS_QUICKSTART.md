# Settings Management - Quick Start Guide

## Overview
Complete settings management system for configuring all application settings through the UI with encryption, audit logging, and validation.

## Quick Start

### 1. Generate Encryption Key (Required for Secrets)
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Set the key in your environment:
```bash
# Windows
set ENCRYPTION_KEY=<generated_key>

# Linux/Mac
export ENCRYPTION_KEY=<generated_key>
```

Or add to `.env`:
```
ENCRYPTION_KEY=your-generated-key-here
```

### 2. Run Database Migration
```bash
cd backend
alembic upgrade head
```

This creates:
- `application_settings` table
- `setting_audit_logs` table
- Seeds 23 default settings

### 3. Restart Backend
```bash
# Development
cd backend
python -m uvicorn app.main:app --reload

# Or use the startup scripts
.\start.bat  # Windows
./start.sh   # Linux/Mac
```

### 4. Access Settings UI
Navigate to: `http://localhost:3000/dashboard/settings/management`

**Note**: Requires admin or superadmin role

## Features

### ✅ Setting Categories
- **LLM**: Provider configuration, API keys, model settings
- **Database**: Connection pool, timeout, SQL logging
- **Redis**: Database number, TTL
- **Security**: JWT expiry, login attempts, CORS
- **Application**: Debug mode, log level, workers
- **UI**: Theme, page size, WebSocket

### ✅ Security
- Fernet encryption for secrets (API keys, passwords)
- Admin-only access control
- Complete audit trail with user attribution
- Server-side validation

### ✅ Operations
- View/edit individual settings
- Bulk edit multiple settings
- Search settings by key/description
- Export settings to JSON
- Import settings from JSON
- Reset to defaults
- View audit log timeline

## API Endpoints

```
GET    /api/v1/settings                    # List all settings
GET    /api/v1/settings/categories         # List categories  
GET    /api/v1/settings/category/{category} # Get by category
GET    /api/v1/settings/{key}              # Get specific setting
PUT    /api/v1/settings/{key}              # Update setting
PUT    /api/v1/settings/bulk               # Bulk update
POST   /api/v1/settings/{key}/reset        # Reset to default
GET    /api/v1/settings/{key}/audit        # Get audit log
POST   /api/v1/settings/export             # Export settings
POST   /api/v1/settings/import             # Import settings
```

All endpoints require `Authorization: Bearer <admin_token>`

## Usage Examples

### Update Setting (UI)
1. Navigate to Settings Management
2. Select category (e.g., "LLM")
3. Click "Edit" on a setting
4. Change value
5. Optionally add change reason
6. Click "Save"

### Update Setting (API)
```bash
curl -X PUT http://localhost:8000/api/v1/settings/llm.temperature \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"value": "0.8", "change_reason": "More creative"}'
```

### Bulk Update
```bash
curl -X PUT http://localhost:8000/api/v1/settings/bulk \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "settings": {
      "app.debug": "false",
      "app.log_level": "WARNING"
    },
    "change_reason": "Production deployment"
  }'
```

### Export/Import
```bash
# Export
curl -X POST http://localhost:8000/api/v1/settings/export \
  -H "Authorization: Bearer <token>" \
  -o settings-backup.json

# Import
curl -X POST "http://localhost:8000/api/v1/settings/import?overwrite=false" \
  -H "Authorization: Bearer <token>" \
  -F "file=@settings-backup.json"
```

## Runtime Settings (Backend Code)

Use runtime settings in your code instead of environment variables:

```python
from app.core.runtime_settings import get_runtime_settings

settings = get_runtime_settings()

# Get typed values
temperature = settings.get_float("llm.temperature", 0.7)
debug = settings.get_bool("app.debug", False)
max_tokens = settings.get_int("llm.max_tokens", 4096)
api_key = settings.get_string("llm.openai_api_key")
cors = settings.get_json("security.cors_origins", [])
```

## Frontend Usage

### Using API Client
```typescript
import { getSettings, updateSetting } from '@/lib/settings-api'

// Get settings
const settings = await getSettings('llm')

// Update setting
await updateSetting('llm.temperature', '0.8', 'More creative')
```

### Using Store
```typescript
import { useSettingsStore } from '@/stores/settings-store'

const { settings, fetchSettings, updateSetting } = useSettingsStore()

// Load
await fetchSettings('llm')

// Update
await updateSetting('llm.temperature', '0.8', 'More creative')
```

## Troubleshooting

### Encryption Key Error
```
SettingsEncryptionError: ENCRYPTION_KEY environment variable is not set
```
**Solution**: Generate and set `ENCRYPTION_KEY` (see step 1)

### Permission Denied
```
HTTP 403: Admin privileges required
```
**Solution**: Ensure user has `admin` or `superadmin` role

### Setting Not Found
```
HTTP 404: Setting 'key' not found
```
**Solution**: Run migration: `alembic upgrade head`

### Validation Failed
```
HTTP 400: Validation failed for 'key'
```
**Solution**: Check value type matches setting type (integer, boolean, etc.)

## Default Settings

### LLM Settings
| Key | Default | Type |
|-----|---------|------|
| llm.default_provider | openai | string |
| llm.openai_api_key | - | secret |
| llm.temperature | 0.7 | float |
| llm.max_tokens | 4096 | integer |

### Database Settings
| Key | Default | Type |
|-----|---------|------|
| database.pool_size | 10 | integer |
| database.pool_timeout | 30 | integer |
| database.echo_sql | false | boolean |

### Security Settings
| Key | Default | Type |
|-----|---------|------|
| security.jwt_expiry_minutes | 30 | integer |
| security.max_login_attempts | 5 | integer |
| security.cors_origins | [...] | json |

See `backend/docs/SETTINGS_MANAGEMENT.md` for complete list.

## Next Steps

1. ✅ Run migration
2. ✅ Set encryption key
3. ✅ Restart backend
4. ✅ Test UI at `/dashboard/settings/management`
5. ⏭️ Update existing services to use runtime settings
6. ⏭️ Add WebSocket events for real-time updates
7. ⏭️ Configure approval workflow for critical settings

## Support

- Full documentation: `backend/docs/SETTINGS_MANAGEMENT.md`
- Implementation summary: `SETTINGS_IMPLEMENTATION_SUMMARY.md`
- API reference: See OpenAPI docs at `http://localhost:8000/docs`
