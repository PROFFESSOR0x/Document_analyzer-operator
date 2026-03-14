# Settings Management System

Comprehensive settings management system for configuring all environment variables and application settings through the UI.

## Overview

The Settings Management System allows administrators to:
- View and modify all application settings through a user-friendly interface
- Organize settings by category (LLM, Database, Security, etc.)
- Track all changes with a complete audit log
- Export/import settings for backup and migration
- Encrypt sensitive values (API keys, passwords)
- Validate settings before applying changes

## Architecture

### Backend Components

#### Models (`backend/app/models/`)

**ApplicationSetting**
- `id` (UUID) - Primary key
- `key` (string) - Unique setting key (e.g., "llm.default_provider")
- `value` (text) - Setting value
- `value_type` (enum) - Type: string, integer, float, boolean, json, secret
- `category` (string) - Category: llm, database, redis, security, application, ui
- `description` (text) - Human-readable description
- `is_secret` (boolean) - Whether value should be encrypted
- `is_editable` (boolean) - Whether UI can modify it
- `validation_schema` (JSONB) - Pydantic schema for validation
- `default_value` (text) - Default value
- `updated_by_id` (UUID) - Foreign key to User
- `created_at`, `updated_at` (timestamps)

**SettingAuditLog**
- `id` (UUID) - Primary key
- `setting_id` (UUID) - Foreign key to ApplicationSetting
- `old_value` (text) - Previous value
- `new_value` (text) - New value
- `changed_by_id` (UUID) - Foreign key to User
- `change_reason` (text) - Reason for change
- `created_at` (timestamp)

#### Service Layer (`backend/app/services/settings_service.py`)

**SettingsService** provides:
- `get_setting(key)` - Get single setting
- `get_settings_by_category(category)` - Get settings by category
- `get_all_settings()` - Get all settings
- `update_setting(key, value, user_id, reason)` - Update with audit logging
- `bulk_update_settings(settings_dict, user_id, reason)` - Bulk update
- `reset_setting_to_default(key)` - Reset to default
- `validate_setting(key, value)` - Validate against schema
- `encrypt_value(value)` - Encrypt secret values
- `decrypt_value(value)` - Decrypt secret values
- `get_audit_log(setting_id, limit)` - Get audit log
- `export_settings()` - Export as JSON
- `import_settings(settings_json, user_id)` - Import from JSON
- `get_categories()` - Get all categories with counts

#### API Routes (`backend/app/api/v1/routes/settings.py`)

```
GET    /api/v1/settings                    # List all settings
GET    /api/v1/settings/categories         # List categories
GET    /api/v1/settings/category/{category} # Get settings by category
GET    /api/v1/settings/{key}              # Get specific setting
PUT    /api/v1/settings/{key}              # Update setting
PUT    /api/v1/settings/bulk               # Bulk update settings
POST   /api/v1/settings/{key}/reset        # Reset to default
GET    /api/v1/settings/{key}/audit        # Get audit log
POST   /api/v1/settings/export             # Export settings
POST   /api/v1/settings/import             # Import settings
GET    /api/v1/settings/schema/{category}  # Get validation schema
```

All endpoints require **admin** or **superadmin** role.

#### Runtime Settings (`backend/app/core/runtime_settings.py`)

**RuntimeSettings** singleton provides:
- In-memory caching of settings
- Type conversion helpers (get_string, get_int, get_bool, get_json)
- Automatic decryption of secrets
- Fallback to environment variables

### Frontend Components

#### Types (`frontend/src/types/settings.ts`)

```typescript
interface ApplicationSetting {
  id: string
  key: string
  value: string | null
  value_type: 'string' | 'integer' | 'float' | 'boolean' | 'json' | 'secret'
  category: string
  description: string | null
  is_secret: boolean
  is_editable: boolean
  validation_schema?: Record<string, unknown>
  default_value: string | null
  updated_at: string
  updated_by?: User
}
```

#### API Client (`frontend/src/lib/settings-api.ts`)

- `getSettings(category?)` - Get settings
- `getSetting(key)` - Get single setting
- `updateSetting(key, value, reason?)` - Update setting
- `bulkUpdateSettings(settings, reason?)` - Bulk update
- `resetSetting(key)` - Reset to default
- `getAuditLog(key, limit?)` - Get audit log
- `exportSettings()` - Export as blob
- `importSettings(file, overwrite?)` - Import from file
- `getCategories()` - Get categories

#### Store (`frontend/src/stores/settings-store.ts`)

Zustand store for state management with actions for all API operations.

#### UI Components (`frontend/src/components/settings/`)

- **SettingCard.tsx** - Individual setting card with edit/reset
- **CategorySelector.tsx** - Category navigation tabs
- **SettingSearch.tsx** - Search component
- **BulkEditor.tsx** - Bulk edit interface
- **AuditLogTimeline.tsx** - Audit log display
- **ExportImportButtons.tsx** - Export/Import actions

#### Pages (`frontend/src/app/dashboard/settings/`)

- **management/page.tsx** - Main settings dashboard
- **category/[category]/page.tsx** - Category detail page
- **audit/page.tsx** - Audit log page

## Setting Categories

### LLM Settings
| Key | Type | Description | Default |
|-----|------|-------------|---------|
| llm.default_provider | string | Default LLM provider | openai |
| llm.openai_api_key | secret | OpenAI API key | - |
| llm.openai_base_url | string | OpenAI API base URL | https://api.openai.com/v1 |
| llm.anthropic_api_key | secret | Anthropic API key | - |
| llm.groq_api_key | secret | Groq API key | - |
| llm.temperature | float | Default temperature (0-2) | 0.7 |
| llm.max_tokens | integer | Default max tokens | 4096 |

### Database Settings
| Key | Type | Description | Default |
|-----|------|-------------|---------|
| database.pool_size | integer | Connection pool size (1-100) | 10 |
| database.pool_timeout | integer | Pool timeout seconds (1-300) | 30 |
| database.echo_sql | boolean | Echo SQL queries | false |

### Redis Settings
| Key | Type | Description | Default |
|-----|------|-------------|---------|
| redis.db | integer | Database number (0-15) | 0 |
| redis.ttl | integer | Default TTL seconds | 3600 |

### Security Settings
| Key | Type | Description | Default |
|-----|------|-------------|---------|
| security.jwt_expiry_minutes | integer | JWT token expiry | 30 |
| security.max_login_attempts | integer | Max login attempts | 5 |
| security.session_timeout_minutes | integer | Session timeout | 60 |
| security.cors_origins | json | CORS allowed origins | [...] |

### Application Settings
| Key | Type | Description | Default |
|-----|------|-------------|---------|
| app.debug | boolean | Debug mode | false |
| app.log_level | string | Log level (DEBUG/INFO/WARNING/ERROR) | INFO |
| app.workers | integer | Number of workers | 1 |
| app.max_upload_size_mb | integer | Max upload size MB | 10 |

### UI Settings
| Key | Type | Description | Default |
|-----|------|-------------|---------|
| ui.theme | string | Default theme (light/dark/system) | system |
| ui.page_size | integer | Default page size | 20 |
| ui.enable_websocket | boolean | Enable WebSocket | true |

## Security Considerations

### Encryption
- All secret values are encrypted using Fernet encryption
- Encryption key must be set via `ENCRYPTION_KEY` environment variable
- Generate key: `cryptography.fernet.Fernet.generate_key()`
- Secrets are masked in API responses (e.g., `sk_•••••••••••••••••••••`)
- Secrets are only decrypted when explicitly requested

### Access Control
- Only users with `admin` or `superadmin` role can access settings
- All changes are logged with user ID and timestamp
- Change reason is optional but recommended for audit trail

### Validation
- Server-side validation for all inputs
- Type validation (integer, float, boolean, json)
- Schema validation using JSON Schema
- Range validation (min/max values)
- Enum validation for predefined values

### Audit Trail
- Every change is logged in `setting_audit_logs` table
- Logs include: old value, new value, user, timestamp, reason
- Audit logs are immutable (no delete/update)
- Export audit logs for compliance

## Usage Examples

### Update a Setting (API)

```bash
curl -X PUT http://localhost:8000/api/v1/settings/llm.temperature \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "value": "0.8",
    "change_reason": "Increasing temperature for more creative responses"
  }'
```

### Bulk Update Settings

```bash
curl -X PUT http://localhost:8000/api/v1/settings/bulk \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "settings": {
      "app.debug": "false",
      "app.log_level": "WARNING"
    },
    "change_reason": "Production deployment configuration"
  }'
```

### Export Settings

```bash
curl -X POST http://localhost:8000/api/v1/settings/export \
  -H "Authorization: Bearer <token>" \
  -o settings-backup.json
```

### Import Settings

```bash
curl -X POST "http://localhost:8000/api/v1/settings/import?overwrite=false" \
  -H "Authorization: Bearer <token>" \
  -F "file=@settings-backup.json"
```

### Get Audit Log

```bash
curl http://localhost:8000/api/v1/settings/llm.temperature/audit?limit=50 \
  -H "Authorization: Bearer <token>"
```

### Use Runtime Settings (Backend)

```python
from app.core.runtime_settings import get_runtime_settings

settings = get_runtime_settings()

# Get typed values
temperature = settings.get_float("llm.temperature", 0.7)
debug = settings.get_bool("app.debug", False)
max_tokens = settings.get_int("llm.max_tokens", 4096)
cors = settings.get_json("security.cors_origins", [])

# Refresh cache after changes
await settings.refresh()
```

## Migration

Run the migration to create settings tables:

```bash
cd backend
alembic upgrade head
```

This will:
1. Create `application_settings` table
2. Create `setting_audit_logs` table
3. Seed default settings from environment variables

## Integration Points

### Existing Services

Update services to use runtime settings instead of environment variables:

```python
# Before
from app.core.settings import get_settings
settings = get_settings()
temperature = settings.llm_temperature

# After
from app.core.runtime_settings import get_runtime_settings
runtime_settings = get_runtime_settings()
temperature = runtime_settings.get_float("llm.temperature", 0.7)
```

### WebSocket Events

Emit events when settings change:

```python
# In settings_service.py after update
await websocket_manager.broadcast({
    "type": "settings_updated",
    "setting_key": key,
    "updated_by": user_id,
    "timestamp": datetime.now(timezone.utc).isoformat(),
})
```

## Best Practices

1. **Always provide change reasons** - Helps with audit trail and debugging
2. **Test in development first** - Never change production settings without testing
3. **Export before bulk changes** - Create backup before making multiple changes
4. **Review audit logs regularly** - Monitor for unauthorized changes
5. **Rotate encryption key** - Periodically rotate `ENCRYPTION_KEY`
6. **Use validation schemas** - Define validation rules for all settings
7. **Document custom settings** - Add descriptions for all custom settings

## Troubleshooting

### Encryption Key Not Set
```
SettingsEncryptionError: ENCRYPTION_KEY environment variable is not set
```
**Solution**: Generate key and set in environment:
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

### Setting Not Found
```
HTTP 404: Setting 'key' not found
```
**Solution**: Check key spelling, ensure migration has run

### Permission Denied
```
HTTP 403: Admin privileges required
```
**Solution**: Ensure user has admin or superadmin role

### Validation Failed
```
HTTP 400: Validation failed for 'key'
```
**Solution**: Check value type and constraints match validation schema

## Future Enhancements

- [ ] Real-time WebSocket updates for setting changes
- [ ] Setting versioning and rollback
- [ ] Approval workflow for critical settings
- [ ] Scheduled setting changes
- [ ] Setting templates/environments
- [ ] Multi-tenant settings
- [ ] Setting dependencies and constraints
- [ ] Health checks for setting validation
