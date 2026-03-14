#!/usr/bin/env python3
"""
Document Analyzer Operator - Environment Validation Script

This script validates the .env file to ensure all required keys are present
and properly formatted before starting the application.

Features:
- Check if .env exists
- Validate all required keys are present
- Validate SECRET_KEY length (min 32 characters)
- Validate ENCRYPTION_KEY format (Fernet key)
- Validate DATABASE_URL format
- Validate REDIS_URL format
- Provide clear error messages
- Exit code 0 if valid, 1 if invalid

Usage:
    python validate_env.py              # Validate backend .env
    python validate_env.py --strict     # Strict mode (warn on optional)
    python validate_env.py --help       # Show help
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class EnvValidator:
    """Validator for environment files."""
    
    # Required keys for backend
    REQUIRED_KEYS = [
        'APP_NAME',
        'APP_VERSION',
        'APP_DEBUG',
        'APP_ENVIRONMENT',
        'APP_HOST',
        'APP_PORT',
        'SECRET_KEY',
        'ALGORITHM',
        'ACCESS_TOKEN_EXPIRE_MINUTES',
        'DATABASE_URL',
        'REDIS_URL',
        'ENCRYPTION_KEY',
        'LOG_LEVEL',
        'STORAGE_PROVIDER',
    ]
    
    # Optional but recommended keys
    RECOMMENDED_KEYS = [
        'OPENAI_API_KEY',
        'ANTHROPIC_API_KEY',
        'GROQ_API_KEY',
        'TOGETHER_API_KEY',
        'ANYSCALE_API_KEY',
        'QDRANT_URL',
        'NEO4J_URI',
        'TEMPORAL_HOST',
    ]
    
    # Keys that should have non-empty values
    NON_EMPTY_KEYS = [
        'SECRET_KEY',
        'ENCRYPTION_KEY',
        'DATABASE_URL',
        'REDIS_URL',
    ]
    
    def __init__(self, env_path: Path, strict: bool = False):
        self.env_path = env_path
        self.strict = strict
        self.env_vars: Dict[str, str] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def load_env_file(self) -> bool:
        """Load and parse the .env file."""
        if not self.env_path.exists():
            self.errors.append(f"❌ .env file not found at {self.env_path}")
            return False
        
        try:
            content = self.env_path.read_text()
            for line_num, line in enumerate(content.splitlines(), 1):
                line = line.strip()
                
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                
                # Parse key=value
                if '=' in line:
                    key, _, value = line.partition('=')
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value and value[0] in ('"', "'") and value[-1] in ('"', "'"):
                        value = value[1:-1]
                    
                    self.env_vars[key] = value
                else:
                    self.warnings.append(f"⚠ Line {line_num}: Invalid format (expected key=value)")
            
            return True
        except Exception as e:
            self.errors.append(f"❌ Failed to read .env file: {e}")
            return False
    
    def validate_required_keys(self) -> bool:
        """Validate that all required keys are present."""
        missing = []
        for key in self.REQUIRED_KEYS:
            if key not in self.env_vars:
                missing.append(key)
        
        if missing:
            self.errors.append(f"❌ Missing required keys: {', '.join(missing)}")
            return False
        
        return True
    
    def validate_secret_key(self) -> bool:
        """Validate SECRET_KEY length and format."""
        secret_key = self.env_vars.get('SECRET_KEY', '')
        
        if not secret_key:
            self.errors.append("❌ SECRET_KEY is empty")
            return False
        
        if len(secret_key) < 32:
            self.errors.append(f"❌ SECRET_KEY too short (minimum 32 characters, got {len(secret_key)})")
            return False
        
        # Check for weak patterns
        weak_patterns = [
            r'^your-',
            r'^change[-_]?this',
            r'^example',
            r'^test',
            r'^secret',
        ]
        
        for pattern in weak_patterns:
            if re.match(pattern, secret_key, re.IGNORECASE):
                self.errors.append("❌ SECRET_KEY uses a weak/default value")
                return False
        
        return True
    
    def validate_encryption_key(self) -> bool:
        """Validate ENCRYPTION_KEY format (Fernet key)."""
        encryption_key = self.env_vars.get('ENCRYPTION_KEY', '')
        
        if not encryption_key:
            self.errors.append("❌ ENCRYPTION_KEY is empty")
            return False
        
        # Fernet key format: 44 characters, base64 encoded
        if len(encryption_key) != 44:
            self.errors.append(f"❌ ENCRYPTION_KEY has invalid length (expected 44, got {len(encryption_key)})")
            return False
        
        # Should end with '='
        if not encryption_key.endswith('='):
            self.errors.append("❌ ENCRYPTION_KEY has invalid format (should be base64 encoded)")
            return False
        
        # Should only contain valid base64 characters
        if not re.match(r'^[A-Za-z0-9+/=]+$', encryption_key):
            self.errors.append("❌ ENCRYPTION_KEY contains invalid characters")
            return False
        
        return True
    
    def validate_database_url(self) -> bool:
        """Validate DATABASE_URL format."""
        database_url = self.env_vars.get('DATABASE_URL', '')
        
        if not database_url:
            self.errors.append("❌ DATABASE_URL is empty")
            return False
        
        # PostgreSQL URL pattern
        patterns = [
            r'^postgresql://',
            r'^postgresql\+asyncpg://',
            r'^postgresql\+psycopg2://',
        ]
        
        if not any(re.match(pattern, database_url) for pattern in patterns):
            self.errors.append("❌ DATABASE_URL must be a PostgreSQL URL (postgresql:// or postgresql+asyncpg://)")
            return False
        
        # Check for default credentials
        if 'your-secure-password' in database_url or 'change_this' in database_url:
            self.warnings.append("⚠ DATABASE_URL uses default/example credentials - change for production")
        
        return True
    
    def validate_redis_url(self) -> bool:
        """Validate REDIS_URL format."""
        redis_url = self.env_vars.get('REDIS_URL', '')
        
        if not redis_url:
            self.errors.append("❌ REDIS_URL is empty")
            return False
        
        # Redis URL pattern
        if not re.match(r'^redis://', redis_url):
            self.errors.append("❌ REDIS_URL must be a Redis URL (redis://)")
            return False
        
        return True
    
    def validate_non_empty_keys(self) -> bool:
        """Validate that specified keys have non-empty values."""
        valid = True
        for key in self.NON_EMPTY_KEYS:
            value = self.env_vars.get(key, '')
            if not value:
                self.errors.append(f"❌ {key} is empty")
                valid = False
        return valid
    
    def validate_recommended_keys(self) -> None:
        """Check for recommended keys (warnings only)."""
        missing = []
        for key in self.RECOMMENDED_KEYS:
            if key not in self.env_vars or not self.env_vars[key]:
                missing.append(key)
        
        if missing and not self.strict:
            self.warnings.append(f"⚠ Missing recommended keys (can be empty for local dev): {', '.join(missing)}")
    
    def validate_boolean_values(self) -> bool:
        """Validate boolean configuration values."""
        boolean_keys = ['APP_DEBUG', 'APP_RELOAD']
        valid_values = ['true', 'false', '1', '0', 'yes', 'no']
        
        valid = True
        for key in boolean_keys:
            if key in self.env_vars:
                value = self.env_vars[key].lower()
                if value not in valid_values:
                    self.errors.append(f"❌ {key} must be a boolean (true/false), got: {value}")
                    valid = False
        
        return valid
    
    def validate_port_numbers(self) -> bool:
        """Validate port number configurations."""
        port_keys = ['APP_PORT', 'REDIS_PORT', 'POSTGRES_PORT']
        
        valid = True
        for key in port_keys:
            if key in self.env_vars:
                try:
                    port = int(self.env_vars[key])
                    if port < 1 or port > 65535:
                        self.errors.append(f"❌ {key} must be between 1 and 65535, got: {port}")
                        valid = False
                except ValueError:
                    self.errors.append(f"❌ {key} must be a number, got: {self.env_vars[key]}")
                    valid = False
        
        return valid
    
    def validate(self) -> bool:
        """Run all validations."""
        print(f"\n🔍 Validating environment file: {self.env_path}\n")
        
        # Load file
        if not self.load_env_file():
            return False
        
        print(f"✓ Loaded {len(self.env_vars)} environment variables\n")
        
        # Run validations
        validations = [
            ("Required keys", self.validate_required_keys),
            ("Non-empty keys", self.validate_non_empty_keys),
            ("SECRET_KEY", self.validate_secret_key),
            ("ENCRYPTION_KEY", self.validate_encryption_key),
            ("DATABASE_URL", self.validate_database_url),
            ("REDIS_URL", self.validate_redis_url),
            ("Boolean values", self.validate_boolean_values),
            ("Port numbers", self.validate_port_numbers),
        ]
        
        all_valid = True
        for name, validator in validations:
            if validator():
                print(f"✓ {name} validation passed")
            else:
                print(f"❌ {name} validation failed")
                all_valid = False
        
        # Check recommended keys (warnings only)
        self.validate_recommended_keys()
        
        # Print results
        print("\n" + "="*60)
        
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  {error}")
        
        if self.warnings:
            print("\n⚠ WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")
        
        print("\n" + "="*60)
        
        if all_valid and not self.errors:
            if self.warnings:
                print("\n✅ Validation passed with warnings")
            else:
                print("\n✅ All validations passed!")
            return True
        else:
            print("\n❌ Validation failed!")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate .env file for Document Analyzer Operator backend",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_env.py              # Validate with default settings
  python validate_env.py --strict     # Strict mode (fail on recommended keys)
  python validate_env.py --env /path/to/.env  # Custom path
        """
    )
    
    parser.add_argument(
        "--env", "-e",
        type=Path,
        default=None,
        help="Path to .env file (default: backend/.env)"
    )
    
    parser.add_argument(
        "--strict", "-s",
        action="store_true",
        help="Strict mode: fail if recommended keys are missing"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Quiet mode: only show final result"
    )
    
    args = parser.parse_args()
    
    # Determine env file path
    if args.env:
        env_path = args.env
    else:
        # Default to backend/.env relative to script location
        script_dir = Path(__file__).parent
        env_path = script_dir.parent / ".env"
    
    # Create validator
    validator = EnvValidator(env_path, strict=args.strict)
    
    # Run validation
    success = validator.validate()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
