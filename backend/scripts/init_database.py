#!/usr/bin/env python3
"""
Document Analyzer Operator - Database Initialization Script
This Python script initializes the PostgreSQL database for the application.
"""

import os
import sys
import asyncio
import hashlib
import secrets
from pathlib import Path
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import asyncpg
    from dotenv import load_dotenv
except ImportError as e:
    print(f"[ERROR] Missing dependency: {e}")
    print("Please run: poetry install")
    sys.exit(1)

# Load environment variables
load_dotenv()


class DatabaseInitializer:
    """Initialize PostgreSQL database for Document Analyzer Operator."""
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        user: str = None,
        password: str = None,
        database: str = None
    ):
        self.host = host or os.getenv("POSTGRES_HOST", "localhost")
        self.port = int(port or os.getenv("POSTGRES_PORT", 5432))
        self.user = user or os.getenv("POSTGRES_USER", "document_analyzer")
        self.password = password or os.getenv("POSTGRES_PASSWORD")
        self.database = database or os.getenv("POSTGRES_DB", "document_analyzer")
        
        if not self.password:
            print("[ERROR] POSTGRES_PASSWORD not set")
            sys.exit(1)
        
        self.admin_user = "postgres"
        self.admin_password = os.getenv("POSTGRES_ADMIN_PASSWORD", "postgres")
        self.conn: Optional[asyncpg.Connection] = None
    
    async def connect_admin(self) -> None:
        """Connect as postgres admin user."""
        print(f"[INFO] Connecting to PostgreSQL as admin...")
        try:
            self.conn = await asyncpg.connect(
                host=self.host,
                port=self.port,
                user=self.admin_user,
                password=self.admin_password,
                database="postgres"
            )
            print("[INFO] Connected to PostgreSQL ✓")
        except Exception as e:
            print(f"[ERROR] Failed to connect: {e}")
            print("[ERROR] Ensure PostgreSQL is running and credentials are correct")
            sys.exit(1)
    
    async def disconnect(self) -> None:
        """Disconnect from database."""
        if self.conn:
            await self.conn.close()
            print("[INFO] Disconnected from PostgreSQL")
    
    async def create_user(self) -> None:
        """Create application database user."""
        print(f"[INFO] Creating user: {self.user}...")
        
        try:
            # Check if user exists
            exists = await self.conn.fetchval(
                "SELECT 1 FROM pg_roles WHERE rolname = $1",
                self.user
            )
            
            if exists:
                print(f"[WARN] User {self.user} already exists")
                # Update password
                await self.conn.execute(
                    f"ALTER USER {self.user} WITH PASSWORD $1",
                    self.password
                )
                print(f"[INFO] Updated password for user {self.user} ✓")
            else:
                await self.conn.execute(
                    f"CREATE USER {self.user} WITH PASSWORD $1",
                    self.password
                )
                print(f"[INFO] User {self.user} created ✓")
        except Exception as e:
            print(f"[ERROR] Failed to create user: {e}")
            raise
    
    async def create_database(self) -> None:
        """Create application database."""
        print(f"[INFO] Creating database: {self.database}...")
        
        try:
            # Check if database exists
            exists = await self.conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1",
                self.database
            )
            
            if exists:
                print(f"[WARN] Database {self.database} already exists")
            else:
                await self.conn.execute(
                    f"CREATE DATABASE {self.database} OWNER {self.user}"
                )
                print(f"[INFO] Database {self.database} created ✓")
        except Exception as e:
            print(f"[ERROR] Failed to create database: {e}")
            raise
    
    async def grant_permissions(self) -> None:
        """Grant permissions to application user."""
        print("[INFO] Granting permissions...")
        
        try:
            await self.conn.execute(
                f"GRANT ALL PRIVILEGES ON DATABASE {self.database} TO {self.user}"
            )
            
            # Connect to the database to grant schema permissions
            db_conn = await asyncpg.connect(
                host=self.host,
                port=self.port,
                user=self.admin_user,
                password=self.admin_password,
                database=self.database
            )
            
            await db_conn.execute(
                "GRANT ALL ON SCHEMA public TO $1",
                self.user
            )
            
            await db_conn.close()
            print("[INFO] Permissions granted ✓")
        except Exception as e:
            print(f"[ERROR] Failed to grant permissions: {e}")
            raise
    
    async def run_migrations(self) -> None:
        """Run Alembic migrations."""
        print("[INFO] Running database migrations...")
        
        try:
            import subprocess
            
            # Set environment variable for migration
            env = os.environ.copy()
            env["DATABASE_URL"] = f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
            
            result = subprocess.run(
                ["poetry", "run", "alembic", "upgrade", "head"],
                cwd=Path(__file__).parent.parent,
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("[INFO] Migrations completed ✓")
            else:
                print(f"[WARN] Migration output: {result.stdout}")
                print(f"[ERROR] Migration errors: {result.stderr}")
        except Exception as e:
            print(f"[ERROR] Failed to run migrations: {e}")
    
    async def initialize(self) -> None:
        """Run full database initialization."""
        print("=" * 50)
        print("Document Analyzer Operator - Database Initialization")
        print("=" * 50)
        print()
        
        await self.connect_admin()
        
        try:
            await self.create_user()
            await self.create_database()
            await self.grant_permissions()
            await self.run_migrations()
            
            # Generate connection string
            connection_string = f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
            
            print()
            print("=" * 50)
            print("Database Initialization Complete!")
            print("=" * 50)
            print()
            print(f"Connection String:")
            print(f"  {connection_string}")
            print()
            print("Update your .env file with:")
            print(f"  POSTGRES_USER={self.user}")
            print(f"  POSTGRES_PASSWORD={self.password}")
            print(f"  POSTGRES_HOST={self.host}")
            print(f"  POSTGRES_PORT={self.port}")
            print(f"  POSTGRES_DB={self.database}")
            print(f"  DATABASE_URL={connection_string}")
            print()
            print("=" * 50)
            
        finally:
            await self.disconnect()


async def main():
    """Main entry point."""
    initializer = DatabaseInitializer()
    await initializer.initialize()


if __name__ == "__main__":
    asyncio.run(main())
