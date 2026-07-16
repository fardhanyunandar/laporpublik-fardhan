"""
LaporPublik Backend v3.1 - Production Ready
============================================
Platform pengaduan masyarakat dengan autentikasi multi-provider
dan dashboard admin lengkap.

Features:
- Email/Password authentication
- Google OAuth 2.0
- Password reset flow (email)
- Rate limiting & security
- Audit logging
- In-app notifications
- File uploads with validation
- Real-time SOS alerts
- Interactive maps (Leaflet)

Author: LaporPublik Team
Version: 3.1.0 (whatsapp removed, UI overhaul)
"""

import os
import re
import uuid
import json
import math
import secrets
import logging
import datetime
import time
from functools import wraps
from collections import defaultdict
from typing import Optional, Dict, Any, List, Tuple

# --- CORE FLASK & SECURITY ---
from flask import (
    Flask, request, jsonify, session, send_from_directory,
    redirect, url_for, g, make_response
)
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# --- DATABASE ---
import mysql.connector
from mysql.connector import pooling, Error as MySQLError

# =====================================================================
# 🚀 TAMBAHAN WAJIB UNTUK FITUR LAPORPUBLIK V3.0
# =====================================================================

# 1. Environment Variables (Untuk membaca file .env)
from dotenv import load_dotenv

# 2. Google OAuth Verifier (Untuk memproses login Google di backend)
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

# 3. SMTP Mailer (Untuk fitur notifikasi email Gmail)
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables tepat setelah import selesai
load_dotenv()

# ─────────────────────────────────────────────
# LOAD .env FILE
# ─────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print('⚠️  python-dotenv belum terinstall — .env tidak akan otomatis dimuat. '
          'Jalankan: pip install python-dotenv')

# Optional dependencies
try:
    from google.oauth2 import id_token as google_id_token
    from google.auth.transport import requests as google_requests

    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False

try:
    import requests as http_requests

    HTTP_AVAILABLE = True
except ImportError:
    HTTP_AVAILABLE = False

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# ─────────────────────────────────────────────
# LOGGING CONFIGURATION
# ─────────────────────────────────────────────
LOG_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# LOG_LEVEL and LOG_FILE now come from .env instead of being hardcoded.
_LOG_LEVEL_NAME = os.environ.get('LOG_LEVEL', 'INFO').upper()
_LOG_LEVEL = getattr(logging, _LOG_LEVEL_NAME, logging.INFO)
_LOG_FILE = os.environ.get('LOG_FILE', 'laporpublik.log')

logging.basicConfig(
    level=_LOG_LEVEL,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT
)
logger = logging.getLogger('LaporPublik')

# File handler for production
if os.environ.get('FLASK_ENV') == 'production':
    file_handler = logging.FileHandler(_LOG_FILE)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    file_handler.setLevel(_LOG_LEVEL)
    logger.addHandler(file_handler)


# ─────────────────────────────────────────────
# APPLICATION CONFIGURATION
# ─────────────────────────────────────────────
class Config:
    """Application configuration container with robust fallback mechanisms."""

    # ─── Flask Core ───
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'
    ENV = os.environ.get('FLASK_ENV', 'development')

    # ─── Session Management ───
    try:
        SESSION_LIFETIME_HOURS = int(os.environ.get('SESSION_LIFETIME_HOURS', 12))
    except ValueError:
        SESSION_LIFETIME_HOURS = 12

    PERMANENT_SESSION_LIFETIME = datetime.timedelta(hours=SESSION_LIFETIME_HOURS)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = ENV == 'production' or os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_NAME = 'laporpublik_session'

    # ─── File Uploads ───
    try:
        MAX_UPLOAD_MB = int(os.environ.get('MAX_UPLOAD_MB', 16))
    except ValueError:
        MAX_UPLOAD_MB = 16

    MAX_CONTENT_LENGTH = MAX_UPLOAD_MB * 1024 * 1024

    # Menjamin path folder upload terbentuk secara absolut dan aman
    UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), 'static', 'uploads'))
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'mov', 'pdf'}

    # ─── Relational Database (MySQL) ───
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    try:
        DB_PORT = int(os.environ.get('DB_PORT', 3307))
    except ValueError:
        DB_PORT = 3307

    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASS = os.environ.get('DB_PASS', '')
    DB_NAME = os.environ.get('DB_NAME', 'laporpublik_db')

    # ─── Google Services Integration ───
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '').strip()
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '').strip()
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '').strip()

    # ─── Email / SMTP Server (Notification System) ───
    SMTP_HOST = os.environ.get('SMTP_HOST', '').strip()
    try:
        SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    except ValueError:
        SMTP_PORT = 587

    SMTP_USER = os.environ.get('SMTP_USER', '').strip()
    SMTP_PASS = os.environ.get('SMTP_PASS', '')
    SMTP_FROM = (os.environ.get('SMTP_FROM') or SMTP_USER or 'no-reply@laporpublik.id').strip()

    # ─── Cross-Origin Resource Sharing (CORS) ───
    raw_cors = os.environ.get('CORS_ORIGINS', '*')
    CORS_ORIGINS = [origin.strip() for origin in raw_cors.split(',')] if raw_cors else ['*']

    # ─── Redis Cache / Rate Limiting ───
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    RATE_LIMIT_DEFAULT = '100/hour'
    RATE_LIMIT_LOGIN = '10/minute'
    RATE_LIMIT_REGISTER = '3/hour'

    # ─── Security Settings & Lockout Policies ───
    try:
        MAX_LOGIN_ATTEMPTS = int(os.environ.get('MAX_LOGIN_ATTEMPTS', 5))
    except ValueError:
        MAX_LOGIN_ATTEMPTS = 5

    try:
        LOCKOUT_DURATION_MINUTES = int(os.environ.get('LOCKOUT_DURATION_MINUTES', 15))
    except ValueError:
        LOCKOUT_DURATION_MINUTES = 15


config = Config()

# ─────────────────────────────────────────────
# FLASK APP INITIALIZATION
# ─────────────────────────────────────────────
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config.from_object(config)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# CORS configuration
CORS(
    app,
    supports_credentials=True,
    origins=app.config['CORS_ORIGINS'],
    expose_headers=['Content-Type', 'Authorization'],
    max_age=3600
)


# ─────────────────────────────────────────────
# DATABASE CONNECTION POOL
# ─────────────────────────────────────────────
class DatabasePool:
    """MySQL connection pool manager."""

    def __init__(self):
        self.pool = None
        self._init_pool()

    def _init_pool(self):
        """Initialize connection pool."""
        try:
            self.pool = pooling.MySQLConnectionPool(
                pool_name='laporpublik_pool',
                pool_size=20,
                pool_reset_session=True,
                host=app.config['DB_HOST'],
                port=app.config['DB_PORT'],
                user=app.config['DB_USER'],
                password=app.config['DB_PASS'],
                database=app.config['DB_NAME'],
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci',
                autocommit=False
            )
            logger.info('✅ Database connection pool initialized')
        except MySQLError as e:
            logger.error(f'❌ Failed to initialize DB pool: {e}')
            raise

    def get_connection(self):
        """Get connection from pool."""
        if not self.pool:
            self._init_pool()
        return self.pool.get_connection()

    def execute(self, sql: str, params: tuple = None, fetch: str = 'all', commit: bool = False) -> Any:
        """Execute SQL query with error handling."""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, params or ())

            if commit:
                conn.commit()
                return cursor.lastrowid

            if fetch == 'one':
                return cursor.fetchone()
            elif fetch == 'all':
                return cursor.fetchall()
            elif fetch == 'count':
                return cursor.rowcount

            return None

        except MySQLError as e:
            if conn:
                conn.rollback()
            logger.error(f'DB Error: {e} | SQL: {sql[:200]}')
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


# Initialize database pool

# ─────────────────────────────────────────────
# REDIS CACHE (Optional)
# ─────────────────────────────────────────────
class CacheManager:
    """Redis cache manager with fallback to in-memory."""

    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}

        if REDIS_AVAILABLE and app.config.get('REDIS_URL'):
            try:
                self.redis_client = redis.from_url(
                    app.config['REDIS_URL'],
                    decode_responses=True,
                    socket_timeout=5
                )
                self.redis_client.ping()
                logger.info('✅ Redis cache connected')
            except Exception as e:
                logger.warning(f'⚠️ Redis not available, using memory cache: {e}')
                self.redis_client = None

    def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        if self.redis_client:
            return self.redis_client.get(key)
        return self.memory_cache.get(key)

    def set(self, key: str, value: str, expire: int = 300):
        """Set value in cache."""
        if self.redis_client:
            self.redis_client.setex(key, expire, value)
        else:
            self.memory_cache[key] = value
            # Simple cleanup for memory cache
            if len(self.memory_cache) > 1000:
                self.memory_cache.clear()

    def delete(self, key: str):
        """Delete key from cache."""
        if self.redis_client:
            self.redis_client.delete(key)
        elif key in self.memory_cache:
            del self.memory_cache[key]

    def increment(self, key: str, expire: int = 60) -> int:
        """Increment counter with expiry."""
        if self.redis_client:
            pipe = self.redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, expire)
            results = pipe.execute()
            return results[0]
        else:
            current = self.memory_cache.get(key, 0)
            self.memory_cache[key] = current + 1
            return current + 1


cache = CacheManager()


# ─────────────────────────────────────────────
# RATE LIMITING
# ─────────────────────────────────────────────
class RateLimiter:
    """Rate limiter with Redis or in-memory fallback."""

    def __init__(self):
        self.limits = defaultdict(list)

    def is_limited(self, key: str, max_requests: int, window_seconds: int) -> Tuple[bool, int]:
        """
        Check if request is rate limited.
        Returns: (is_limited, retry_after_seconds)
        """
        now = time.time()

        if cache.redis_client:
            # Use Redis for distributed rate limiting
            redis_key = f'rate_limit:{key}'
            count = cache.increment(redis_key, window_seconds)

            if count > max_requests:
                ttl = cache.redis_client.ttl(redis_key)
                return True, max(ttl, 1)
            return False, 0
        else:
            # In-memory fallback
            self.limits[key] = [t for t in self.limits[key] if now - t < window_seconds]

            if len(self.limits[key]) >= max_requests:
                oldest = min(self.limits[key])
                retry_after = int(window_seconds - (now - oldest)) + 1
                return True, retry_after

            self.limits[key].append(now)
            return False, 0


rate_limiter = RateLimiter()


def rate_limit(key_func, max_requests: int = 10, window_seconds: int = 60):
    """Rate limiting decorator."""

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            try:
                key = key_func()
                is_limited, retry_after = rate_limiter.is_limited(key, max_requests, window_seconds)

                if is_limited:
                    response = jsonify({
                        'ok': False,
                        'msg': f'Terlalu banyak percobaan. Coba lagi dalam {retry_after} detik.',
                        'retry_after': retry_after
                    })
                    response.headers['Retry-After'] = str(retry_after)
                    return response, 429

                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f'Rate limit error: {e}')
                return f(*args, **kwargs)

        return decorated

    return decorator


def get_client_ip() -> str:
    """Get real client IP from headers."""
    if request.headers.get('X-Forwarded-For'):
        return request.headers['X-Forwarded-For'].split(',')[0].strip()
    if request.headers.get('X-Real-IP'):
        return request.headers['X-Real-IP']
    return request.remote_addr or 'unknown'


# ─────────────────────────────────────────────
# SECURITY UTILITIES
# ─────────────────────────────────────────────
class SecurityUtils:
    """Security helper functions."""

    @staticmethod
    def sanitize(text: str) -> str:
        """Sanitize input to prevent XSS."""
        if not text:
            return text
        # Remove HTML tags and special characters
        text = re.sub(r'<[^>]+>', '', str(text))
        text = re.sub(r'[<>"\';()]', '', text)
        return text.strip()

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def generate_ticket() -> str:
        """Generate unique ticket ID."""
        ts = datetime.datetime.now().strftime('%Y%m%d')
        uid = secrets.token_hex(3).upper()
        return f'LP-{ts}-{uid}'

    @staticmethod
    def check_password_strength(password: str) -> Dict[str, Any]:
        """Check password strength and return score."""
        checks = {
            'length': len(password) >= 8,
            'uppercase': bool(re.search(r'[A-Z]', password)),
            'lowercase': bool(re.search(r'[a-z]', password)),
            'number': bool(re.search(r'\d', password)),
            'special': bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        }

        score = sum(checks.values())

        strength = 'weak'
        if score >= 5:
            strength = 'very_strong'
        elif score >= 4:
            strength = 'strong'
        elif score >= 3:
            strength = 'medium'

        return {
            'score': score,
            'strength': strength,
            'checks': checks
        }

    @staticmethod
    def allowed_file(filename: str) -> bool:
        """Check if file extension is allowed."""
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


security = SecurityUtils()

# ─────────────────────────────────────────────
# DATABASE SCHEMA
# ─────────────────────────────────────────────
SCHEMA = """
-- Users table with multi-provider auth support
CREATE TABLE IF NOT EXISTS users (
    id                      INT AUTO_INCREMENT PRIMARY KEY,
    uid                     VARCHAR(36) NOT NULL UNIQUE DEFAULT (UUID()),
    full_name               VARCHAR(120) NOT NULL,
    email                   VARCHAR(160) NOT NULL UNIQUE,
    phone                   VARCHAR(20),
    nik                     VARCHAR(20),
    address                 TEXT,
    avatar_url              VARCHAR(300),
    password                VARCHAR(256),
    google_id               VARCHAR(100) UNIQUE,
    auth_provider           ENUM('local','google') DEFAULT 'local',
    role                    ENUM('user','admin','superadmin') NOT NULL DEFAULT 'user',
    is_active               TINYINT(1) DEFAULT 1,
    is_verified             TINYINT(1) DEFAULT 0,
    verify_token            VARCHAR(64),
    reset_token             VARCHAR(64),
    reset_expiry            DATETIME,
    last_login              DATETIME,
    login_count             INT DEFAULT 0,
    failed_login_attempts   INT DEFAULT 0,
    locked_until            DATETIME,
    password_changed_at     DATETIME,
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_google_id (google_id),
    INDEX idx_role (role),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Reports table
CREATE TABLE IF NOT EXISTS reports (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id       VARCHAR(20) NOT NULL UNIQUE,
    user_id         INT NOT NULL,
    title           VARCHAR(300) NOT NULL,
    category        VARCHAR(80) NOT NULL,
    subcategory     VARCHAR(80),
    description     TEXT NOT NULL,
    location_name   VARCHAR(300),
    latitude        DECIMAL(10,7),
    longitude       DECIMAL(10,7),
    address_detail  TEXT,
    district        VARCHAR(120),
    city            VARCHAR(120),
    province        VARCHAR(120),
    priority        ENUM('low','medium','high','critical') DEFAULT 'medium',
    status          ENUM('pending','in_review','in_progress','resolved','rejected','closed') DEFAULT 'pending',
    is_anonymous    TINYINT(1) DEFAULT 0,
    is_sos          TINYINT(1) DEFAULT 0,
    admin_notes     TEXT,
    resolved_at     DATETIME,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_status (status),
    INDEX idx_category (category),
    INDEX idx_priority (priority),
    INDEX idx_created (created_at),
    INDEX idx_user (user_id),
    INDEX idx_location (latitude, longitude)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Report attachments
CREATE TABLE IF NOT EXISTS report_attachments (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    report_id   INT NOT NULL,
    file_url    VARCHAR(300) NOT NULL,
    file_type   VARCHAR(30),
    file_size   BIGINT,
    file_name   VARCHAR(255),
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE,
    INDEX idx_report (report_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Report timeline
CREATE TABLE IF NOT EXISTS report_timeline (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    report_id   INT NOT NULL,
    actor_id    INT,
    actor_name  VARCHAR(120),
    action      VARCHAR(80) NOT NULL,
    old_status  VARCHAR(40),
    new_status  VARCHAR(40),
    notes       TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE,
    INDEX idx_report (report_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- User notifications
CREATE TABLE IF NOT EXISTS notifications (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    report_id   INT,
    title       VARCHAR(200) NOT NULL,
    message     TEXT NOT NULL,
    type        ENUM('info','success','warning','error','sos') DEFAULT 'info',
    is_read     TINYINT(1) DEFAULT 0,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE SET NULL,
    INDEX idx_user_read (user_id, is_read),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- SOS events
CREATE TABLE IF NOT EXISTS sos_events (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    latitude    DECIMAL(10,7) NOT NULL,
    longitude   DECIMAL(10,7) NOT NULL,
    address     VARCHAR(300),
    message     TEXT,
    status      ENUM('active','resolved','false_alarm') DEFAULT 'active',
    resolved_by INT,
    resolved_at DATETIME,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_status (status),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Admin notifications
CREATE TABLE IF NOT EXISTS admin_notifications (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    type        ENUM('new_report','sos','user_register','report_update','system') DEFAULT 'new_report',
    title       VARCHAR(200) NOT NULL,
    message     TEXT NOT NULL,
    ref_id      INT,
    is_read     TINYINT(1) DEFAULT 0,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_read (is_read),
    INDEX idx_type (type),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- OAuth accounts
CREATE TABLE IF NOT EXISTS oauth_accounts (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT NOT NULL,
    provider        VARCHAR(30) NOT NULL,
    provider_id     VARCHAR(200) NOT NULL,
    provider_data   JSON,
    access_token    TEXT,
    refresh_token   TEXT,
    token_expiry    DATETIME,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_provider_user (provider, user_id),
    UNIQUE KEY uk_provider_id (provider, provider_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Password reset tokens
CREATE TABLE IF NOT EXISTS password_resets (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    token       VARCHAR(64) NOT NULL UNIQUE,
    expires_at  DATETIME NOT NULL,
    is_used     TINYINT(1) DEFAULT 0,
    ip_address  VARCHAR(45),
    user_agent  VARCHAR(300),
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_token (token),
    INDEX idx_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- System settings
CREATE TABLE IF NOT EXISTS system_settings (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    `key`       VARCHAR(80) NOT NULL UNIQUE,
    value       TEXT,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Audit logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT,
    action      VARCHAR(80) NOT NULL,
    details     TEXT,
    ip_address  VARCHAR(45),
    user_agent  VARCHAR(300),
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_action (action),
    INDEX idx_created (created_at),
    INDEX idx_ip (ip_address)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- User sessions (for session management)
CREATE TABLE IF NOT EXISTS user_sessions (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    session_id  VARCHAR(100) NOT NULL UNIQUE,
    ip_address  VARCHAR(45),
    user_agent  VARCHAR(300),
    last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_session (session_id),
    INDEX idx_last_active (last_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""


def init_db():
    """Initialize database with schema and defaults."""
    try:
        # Connect without database to create it
        conn = mysql.connector.connect(
            host=app.config['DB_HOST'],
            port=app.config['DB_PORT'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASS'],
            charset='utf8mb4'
        )
        cursor = conn.cursor()

        # Create database
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{app.config['DB_NAME']}` "
            f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        cursor.execute(f"USE `{app.config['DB_NAME']}`")

        # Execute schema
        for stmt in SCHEMA.strip().split(';'):
            stmt = stmt.strip()
            if stmt:
                try:
                    cursor.execute(stmt)
                except MySQLError as e:
                    logger.warning(f'Schema warning: {e}')

        conn.commit()

        # Create default superadmin
        cursor.execute("SELECT id FROM users WHERE role='superadmin' LIMIT 1")
        if not cursor.fetchone():
            pw_hash = generate_password_hash('Admin@2026!')
            cursor.execute("""
                INSERT INTO users 
                (uid, full_name, email, phone, password, role, is_active, is_verified, auth_provider)
                VALUES (%s, 'Super Administrator', 'admin@lapor.id', '081234567890', %s, 'superadmin', 1, 1, 'local')
            """, (str(uuid.uuid4()), pw_hash))
            conn.commit()
            logger.info('✅ Default superadmin created: admin@lapor.id / Admin@2026!')

        # Insert default settings
        # UPGRADE: these now seed from .env on first run (via app.config,
        # which itself reads os.environ) instead of always inserting blank
        # strings / hardcoded numbers regardless of what was configured.
        # INSERT IGNORE means this only affects fresh installs — existing
        # rows edited later via the admin settings UI are left untouched.
        defaults = [
            ('app_name', 'LaporPublik'),
            ('google_client_id', app.config['GOOGLE_CLIENT_ID']),
            ('google_maps_key', app.config['GOOGLE_MAPS_API_KEY']),
            ('max_upload_mb', str(app.config['MAX_UPLOAD_MB'])),
            ('sos_email', 'sos@lapor.id'),
            ('max_login_attempts', str(app.config['MAX_LOGIN_ATTEMPTS'])),
            ('lockout_duration_minutes', str(app.config['LOCKOUT_DURATION_MINUTES'])),
            ('password_min_length', '8'),
            ('require_strong_password', '1'),
        ]

        for key, value in defaults:
            cursor.execute(
                "INSERT IGNORE INTO system_settings (`key`, value) VALUES (%s, %s)",
                (key, value)
            )

        conn.commit()

        # Make password nullable for OAuth users
        try:
            cursor.execute("ALTER TABLE users MODIFY password VARCHAR(256) NULL")
            conn.commit()
        except MySQLError:
            pass  # Column already nullable

        cursor.close()
        conn.close()

        logger.info('✅ Database initialized successfully')

    except MySQLError as e:
        logger.error(f'❌ Database initialization failed: {e}')
        raise


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
def get_setting(key: str, default: str = None) -> Optional[str]:
    """Get system setting value."""
    try:
        result = db.execute(
            "SELECT value FROM system_settings WHERE `key`=%s",
            (key,),
            fetch='one'
        )
        return result['value'] if result else default
    except Exception as e:
        logger.error(f'Error getting setting {key}: {e}')
        return default


def log_audit(user_id: int, action: str, details: str = None):
    """Log security-relevant actions."""
    try:
        db.execute("""
            INSERT INTO audit_logs (user_id, action, details, ip_address, user_agent)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            user_id,
            action,
            details,
            get_client_ip(),
            request.headers.get('User-Agent', '')[:300]
        ), commit=True)
    except Exception as e:
        logger.warning(f'Audit log failed: {e}')


def push_notification(user_id: int, title: str, message: str, ntype: str = 'info', report_id: int = None):
    """Push notification to user."""
    try:
        db.execute("""
            INSERT INTO notifications (user_id, report_id, title, message, type)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, report_id, title, message, ntype), commit=True)
    except Exception as e:
        logger.error(f'Failed to push notification: {e}')


def push_admin_notification(title: str, message: str, ntype: str = 'new_report', ref_id: int = None):
    """Push notification to admin."""
    try:
        db.execute("""
            INSERT INTO admin_notifications (type, title, message, ref_id)
            VALUES (%s, %s, %s, %s)
        """, (ntype, title, message, ref_id), commit=True)
    except Exception as e:
        logger.error(f'Failed to push admin notification: {e}')


def log_timeline(report_id: int, actor_id: int, actor_name: str, action: str,
                 old_st: str = None, new_st: str = None, notes: str = None):
    """Log report timeline event."""
    try:
        db.execute("""
            INSERT INTO report_timeline 
            (report_id, actor_id, actor_name, action, old_status, new_status, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (report_id, actor_id, actor_name, action, old_st, new_st, notes), commit=True)
    except Exception as e:
        logger.error(f'Failed to log timeline: {e}')


# ─────────────────────────────────────────────
# AUTH DECORATORS
# ─────────────────────────────────────────────
def login_required(f):
    """Require authentication."""

    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({
                'ok': False,
                'msg': 'Sesi tidak valid. Silakan login kembali.'
            }), 401
        return f(*args, **kwargs)

    return decorated


def admin_required(f):
    """Require admin role."""

    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'ok': False, 'msg': 'Unauthorized'}), 401
        if session.get('role') not in ('admin', 'superadmin'):
            return jsonify({
                'ok': False,
                'msg': 'Akses ditolak. Hanya admin yang diizinkan.'
            }), 403
        return f(*args, **kwargs)

    return decorated


def superadmin_required(f):
    """Require superadmin role."""

    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'ok': False, 'msg': 'Unauthorized'}), 401
        if session.get('role') != 'superadmin':
            return jsonify({
                'ok': False,
                'msg': 'Akses ditolak. Hanya superadmin yang diizinkan.'
            }), 403
        return f(*args, **kwargs)

    return decorated


# ─────────────────────────────────────────────
# REQUEST HOOKS
# ─────────────────────────────────────────────
@app.before_request
def before_request():
    """Before request hook."""
    g.start_time = time.time()

    # Log request (excluding static files)
    if not request.path.startswith('/static'):
        logger.debug(f'{request.method} {request.path} from {get_client_ip()}')


@app.after_request
def after_request(response):
    """After request hook."""
    # Add security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

    # Calculate request time
    if hasattr(g, 'start_time'):
        request_time = time.time() - g.start_time
        response.headers['X-Request-Time'] = f'{request_time:.3f}s'

    return response


# ─────────────────────────────────────────────
# STATIC PAGES
# ─────────────────────────────────────────────
@app.route('/')
def index():
    """Landing page."""
    return send_from_directory('templates', 'index.html')


@app.route('/login')
def login_page():
    """Login/Register page."""
    if 'user_id' in session:
        role = session.get('role', 'user')
        return redirect('/dashboard/admin' if role in ('admin', 'superadmin') else '/dashboard/user')
    return send_from_directory('templates', 'login.html')


@app.route('/dashboard/user')
@login_required
def dashboard_user():
    """User dashboard."""
    if session.get('role') in ('admin', 'superadmin'):
        return redirect('/dashboard/admin')
    return send_from_directory('templates', 'dashboard-user.html')


@app.route('/dashboard/admin')
@admin_required
def dashboard_admin():
    """Admin dashboard."""
    return send_from_directory('templates', 'dashboard-admin.html')


@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files."""
    return send_from_directory('static', filename)


# ─────────────────────────────────────────────
# AUTH — CONFIG ENDPOINT
# ─────────────────────────────────────────────
@app.route('/api/auth/config', methods=['GET'])
def auth_config():
    """Get public auth configuration for frontend."""
    return jsonify({
        'ok': True,
        'config': {
            'google_client_id': get_setting('google_client_id') or app.config['GOOGLE_CLIENT_ID'],
            'google_oauth_available': GOOGLE_AUTH_AVAILABLE,
            'app_name': get_setting('app_name') or 'LaporPublik',
        }
    })


# ─────────────────────────────────────────────
# AUTH — REGISTER
# ─────────────────────────────────────────────
@app.route('/api/auth/register', methods=['POST'])
@rate_limit(lambda: f'register:{get_client_ip()}', max_requests=3, window_seconds=300)
def register():
    """Register new user with email/password."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'ok': False, 'msg': 'Data tidak valid.'}), 400

        name = security.sanitize(data.get('full_name', '')).strip()
        email = security.sanitize(data.get('email', '')).lower().strip()
        phone = security.sanitize(data.get('phone', '')).strip()
        nik = security.sanitize(data.get('nik', '')).strip()
        password = data.get('password', '')

        # Validation
        if not all([name, email, password]):
            return jsonify({'ok': False, 'msg': 'Nama, email, dan password wajib diisi.'}), 400

        if len(name) < 3:
            return jsonify({'ok': False, 'msg': 'Nama terlalu pendek (min 3 karakter).'}), 400

        if not security.validate_email(email):
            return jsonify({'ok': False, 'msg': 'Format email tidak valid.'}), 400

        # Password strength check
        pw_strength = security.check_password_strength(password)
        require_strong = get_setting('require_strong_password') == '1'
        min_length = int(get_setting('password_min_length') or 8)

        if len(password) < min_length:
            return jsonify({'ok': False, 'msg': f'Password minimal {min_length} karakter.'}), 400

        if require_strong and pw_strength['score'] < 3:
            return jsonify({
                'ok': False,
                'msg': 'Password terlalu lemah. Gunakan kombinasi huruf besar, kecil, angka, dan simbol.',
                'password_strength': pw_strength
            }), 400

        # Check existing user
        existing = db.execute("SELECT id FROM users WHERE email=%s", (email,), fetch='one')
        if existing:
            return jsonify({'ok': False, 'msg': 'Email sudah terdaftar. Silakan login.'}), 409

        # Create user
        uid = str(uuid.uuid4())
        token = secrets.token_hex(32)
        pw_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

        user_id = db.execute("""
            INSERT INTO users 
            (uid, full_name, email, phone, nik, password, verify_token, auth_provider)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'local')
        """, (uid, name, email, phone, nik, pw_hash, token), commit=True)

        log_audit(user_id, 'register', f'Email: {email}')

        push_admin_notification(
            f'Pengguna Baru: {name}',
            f'Pengguna baru mendaftar dengan email {email}.',
            ntype='user_register',
            ref_id=user_id
        )

        return jsonify({
            'ok': True,
            'msg': 'Registrasi berhasil! Silakan login.',
            'user_id': user_id
        }), 201

    except Exception as e:
        logger.error(f'Register error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


# ─────────────────────────────────────────────
# AUTH — LOGIN
# ─────────────────────────────────────────────
@app.route('/api/auth/login', methods=['POST'])
@rate_limit(lambda: f'login:{get_client_ip()}', max_requests=10, window_seconds=60)
def login():
    """Login with email/password."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'ok': False, 'msg': 'Data tidak valid.'}), 400

        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        remember = data.get('remember', False)

        if not email or not password:
            return jsonify({'ok': False, 'msg': 'Email dan password wajib diisi.'}), 400

        # Get user
        user = db.execute(
            "SELECT * FROM users WHERE email=%s",
            (email,),
            fetch='one'
        )

        if not user:
            return jsonify({'ok': False, 'msg': 'Email atau password salah.'}), 401

        # Check if account locked
        if user.get('locked_until'):
            locked_until = user['locked_until']
            if isinstance(locked_until, str):
                locked_until = datetime.datetime.fromisoformat(str(locked_until))

            if locked_until > datetime.datetime.now():
                remaining = int((locked_until - datetime.datetime.now()).total_seconds() / 60)
                return jsonify({
                    'ok': False,
                    'msg': f'Akun dikunci sementara. Coba lagi dalam {remaining} menit.',
                    'locked_until': locked_until.isoformat()
                }), 423

        # Check if active
        if not user.get('is_active'):
            return jsonify({'ok': False, 'msg': 'Akun Anda telah dinonaktifkan. Hubungi admin.'}), 403

        # Check password
        if not user.get('password') or not check_password_hash(user['password'], password):
            # Increment failed attempts
            new_attempts = (user.get('failed_login_attempts') or 0) + 1
            max_attempts = int(get_setting('max_login_attempts') or 5)
            lockout_minutes = int(get_setting('lockout_duration_minutes') or 15)

            update_data = {'failed_login_attempts': new_attempts}

            if new_attempts >= max_attempts:
                lock_until = datetime.datetime.now() + datetime.timedelta(minutes=lockout_minutes)
                update_data['locked_until'] = lock_until
                log_audit(user['id'], 'account_locked', 'Too many failed attempts')

            set_clause = ', '.join(f'{k}=%s' for k in update_data)
            db.execute(
                f"UPDATE users SET {set_clause} WHERE id=%s",
                tuple(update_data.values()) + (user['id'],),
                commit=True
            )

            remaining = max_attempts - new_attempts
            return jsonify({
                'ok': False,
                'msg': f'Email atau password salah. Sisa percobaan: {remaining}'
            }), 401

        # Success - reset failed attempts
        db.execute("""
            UPDATE users 
            SET failed_login_attempts=0, locked_until=NULL,
                last_login=NOW(), login_count=login_count+1
            WHERE id=%s
        """, (user['id'],), commit=True)

        # Set session
        session.permanent = True
        app.config['PERMANENT_SESSION_LIFETIME'] = (
            datetime.timedelta(days=30) if remember else datetime.timedelta(hours=12)
        )

        session['user_id'] = user['id']
        session['uid'] = user['uid']
        session['role'] = user['role']
        session['full_name'] = user['full_name']
        session['email'] = user['email']
        session['auth_provider'] = user.get('auth_provider', 'local')

        log_audit(user['id'], 'login_success', f'Provider: {user.get("auth_provider", "local")}')

        redirect_url = '/dashboard/admin' if user['role'] in ('admin', 'superadmin') else '/dashboard/user'

        return jsonify({
            'ok': True,
            'msg': f'Selamat datang, {user["full_name"]}!',
            'role': user['role'],
            'redirect': redirect_url,
            'user': {
                'id': user['id'],
                'full_name': user['full_name'],
                'email': user['email'],
                'avatar_url': user['avatar_url'],
                'role': user['role'],
                'auth_provider': user.get('auth_provider', 'local'),
            }
        })

    except Exception as e:
        logger.error(f'Login error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


# ─────────────────────────────────────────────
# AUTH — GOOGLE OAUTH
# ─────────────────────────────────────────────
@app.route('/api/auth/google', methods=['POST'])
@rate_limit(lambda: f'google:{get_client_ip()}', max_requests=10, window_seconds=60)
def google_login():
    """Handle Google OAuth credential from frontend."""
    if not GOOGLE_AUTH_AVAILABLE:
        return jsonify({'ok': False, 'msg': 'Google OAuth tidak tersedia di server.'}), 500

    try:
        data = request.get_json()
        if not data:
            return jsonify({'ok': False, 'msg': 'Data tidak valid.'}), 400

        credential = data.get('credential')
        if not credential:
            return jsonify({'ok': False, 'msg': 'Credential tidak diterima.'}), 400

        # Get client ID
        client_id = get_setting('google_client_id') or app.config['GOOGLE_CLIENT_ID']
        if not client_id:
            return jsonify({'ok': False, 'msg': 'Google Client ID belum dikonfigurasi.'}), 500

        # Verify Google ID token
        idinfo = google_id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            client_id
        )

        # Validate audience
        if idinfo.get('aud') != client_id:
            raise ValueError('Invalid audience')

        google_id = idinfo['sub']
        email = idinfo.get('email', '').lower()
        name = idinfo.get('name', '')
        picture = idinfo.get('picture', '')

        if not email:
            return jsonify({'ok': False, 'msg': 'Email tidak tersedia dari akun Google.'}), 400

        # Check if user exists by Google ID
        user = db.execute("SELECT * FROM users WHERE google_id=%s", (google_id,), fetch='one')

        if not user:
            # Check if email exists (link accounts)
            user = db.execute("SELECT * FROM users WHERE email=%s", (email,), fetch='one')

            if user:
                # Link Google account to existing user
                db.execute("""
                    UPDATE users 
                    SET google_id=%s, auth_provider='google', 
                        avatar_url=COALESCE(avatar_url, %s)
                    WHERE id=%s
                """, (google_id, picture, user['id']), commit=True)

                user['google_id'] = google_id
                user['auth_provider'] = 'google'

                if picture and not user.get('avatar_url'):
                    user['avatar_url'] = picture

                # Save OAuth account
                db.execute("""
                    INSERT INTO oauth_accounts (user_id, provider, provider_id, provider_data)
                    VALUES (%s, 'google', %s, %s)
                    ON DUPLICATE KEY UPDATE provider_data=%s, updated_at=NOW()
                """, (user['id'], google_id, json.dumps(idinfo)[:1000], json.dumps(idinfo)[:1000]), commit=True)
            else:
                # Create new user
                uid = str(uuid.uuid4())
                user_id = db.execute("""
                    INSERT INTO users 
                    (uid, full_name, email, avatar_url, google_id, password, role, is_active, is_verified, auth_provider)
                    VALUES (%s, %s, %s, %s, %s, NULL, 'user', 1, 1, 'google')
                """, (uid, name, email, picture, google_id), commit=True)

                # Save OAuth account
                db.execute("""
                    INSERT INTO oauth_accounts (user_id, provider, provider_id, provider_data)
                    VALUES (%s, 'google', %s, %s)
                """, (user_id, google_id, json.dumps(idinfo)[:1000]), commit=True)

                user = db.execute("SELECT * FROM users WHERE id=%s", (user_id,), fetch='one')

                push_admin_notification(
                    f'Pengguna Baru (Google): {name}',
                    f'Pengguna baru mendaftar via Google dengan email {email}.',
                    ntype='user_register',
                    ref_id=user_id
                )

                log_audit(user_id, 'register_google', f'Email: {email}')

        # Check if active
        if not user.get('is_active'):
            return jsonify({'ok': False, 'msg': 'Akun Anda telah dinonaktifkan.'}), 403

        # Login
        db.execute("""
            UPDATE users 
            SET last_login=NOW(), login_count=login_count+1
            WHERE id=%s
        """, (user['id'],), commit=True)

        session.permanent = True
        session['user_id'] = user['id']
        session['uid'] = user['uid']
        session['role'] = user['role']
        session['full_name'] = user['full_name']
        session['email'] = user['email']
        session['auth_provider'] = 'google'

        log_audit(user['id'], 'login_google', f'Email: {email}')

        redirect_url = '/dashboard/admin' if user['role'] in ('admin', 'superadmin') else '/dashboard/user'

        return jsonify({
            'ok': True,
            'msg': f'Selamat datang, {user["full_name"]}!',
            'role': user['role'],
            'redirect': redirect_url,
            'user': {
                'id': user['id'],
                'full_name': user['full_name'],
                'email': user['email'],
                'avatar_url': user.get('avatar_url') or picture,
                'role': user['role'],
                'auth_provider': 'google',
            }
        })

    except ValueError as e:
        logger.warning(f'Google OAuth invalid token: {e}')
        return jsonify({'ok': False, 'msg': 'Token Google tidak valid.'}), 401
    except Exception as e:
        logger.error(f'Google OAuth error: {e}')
        return jsonify({'ok': False, 'msg': 'Gagal login dengan Google. Coba lagi.'}), 500


# ─────────────────────────────────────────────
# AUTH — LOGOUT & SESSION
# ─────────────────────────────────────────────
@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user."""
    uid = session.get('user_id')
    if uid:
        log_audit(uid, 'logout')
    session.clear()
    return jsonify({'ok': True, 'msg': 'Logout berhasil.', 'redirect': '/login'})


@app.route('/api/auth/me', methods=['GET'])
@login_required
def me():
    """Get current user info."""
    user = db.execute("""
        SELECT id, uid, full_name, email, phone, nik, address, avatar_url,
               role, is_verified, auth_provider, created_at, last_login, login_count 
        FROM users WHERE id=%s
    """, (session['user_id'],), fetch='one')

    if not user:
        session.clear()
        return jsonify({'ok': False, 'msg': 'User tidak ditemukan.'}), 404

    return jsonify({'ok': True, 'user': user})


@app.route('/api/auth/change-password', methods=['POST'])
@login_required
@rate_limit(lambda: f'chpw:{session.get("user_id")}', max_requests=5, window_seconds=300)
def change_password():
    """Change user password."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'ok': False, 'msg': 'Data tidak valid.'}), 400

        old_pw = data.get('old_password', '')
        new_pw = data.get('new_password', '')

        min_length = int(get_setting('password_min_length') or 8)
        if len(new_pw) < min_length:
            return jsonify({'ok': False, 'msg': f'Password baru minimal {min_length} karakter.'}), 400

        # Check password strength
        pw_strength = security.check_password_strength(new_pw)
        require_strong = get_setting('require_strong_password') == '1'

        if require_strong and pw_strength['score'] < 3:
            return jsonify({
                'ok': False,
                'msg': 'Password baru terlalu lemah.',
                'password_strength': pw_strength
            }), 400

        user = db.execute("SELECT password FROM users WHERE id=%s", (session['user_id'],), fetch='one')

        if not user.get('password') or not check_password_hash(user['password'], old_pw):
            return jsonify({'ok': False, 'msg': 'Password lama salah.'}), 401

        db.execute("""
            UPDATE users 
            SET password=%s, password_changed_at=NOW()
            WHERE id=%s
        """, (generate_password_hash(new_pw, method='pbkdf2:sha256', salt_length=16), session['user_id']), commit=True)

        log_audit(session['user_id'], 'password_change')

        return jsonify({'ok': True, 'msg': 'Password berhasil diubah.'})

    except Exception as e:
        logger.error(f'Change password error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


# ─────────────────────────────────────────────
# AUTH — PASSWORD RESET
# ─────────────────────────────────────────────
@app.route('/api/auth/forgot-password', methods=['POST'])
@rate_limit(lambda: f'forgot:{get_client_ip()}', max_requests=3, window_seconds=300)
def forgot_password():
    """Request password reset."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'ok': False, 'msg': 'Data tidak valid.'}), 400

        email = data.get('email', '').lower().strip()

        if not email:
            return jsonify({'ok': False, 'msg': 'Email wajib diisi.'}), 400

        user = db.execute("""
            SELECT * FROM users 
            WHERE email=%s AND auth_provider='local'
        """, (email,), fetch='one')

        if not user:
            # Don't reveal if email exists (security)
            return jsonify({'ok': True, 'msg': 'Jika email terdaftar, instruksi reset akan dikirim.'})

        token = secrets.token_urlsafe(32)
        expires_at = datetime.datetime.now() + datetime.timedelta(hours=1)

        db.execute("""
            INSERT INTO password_resets (user_id, token, expires_at, ip_address, user_agent)
            VALUES (%s, %s, %s, %s, %s)
        """, (user['id'], token, expires_at, get_client_ip(), request.headers.get('User-Agent', '')[:300]), commit=True)

        # TODO: Send email with reset link
        reset_link = f"{request.host_url}login?reset={token}"
        logger.info(f'Password reset link for {email}: {reset_link}')
        return jsonify({'ok': True, 'msg': 'Link reset password telah dikirim ke email Anda.', 'method': 'email'})

    except Exception as e:
        logger.error(f'Forgot password error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


@app.route('/api/auth/reset-password', methods=['POST'])
@rate_limit(lambda: f'reset:{get_client_ip()}', max_requests=5, window_seconds=300)
def reset_password():
    """Reset password with token."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'ok': False, 'msg': 'Data tidak valid.'}), 400

        email = data.get('email', '').lower().strip()
        new_password = data.get('new_password', '')
        token = data.get('token', '')

        if not email or not new_password:
            return jsonify({'ok': False, 'msg': 'Email dan password baru wajib diisi.'}), 400

        min_length = int(get_setting('password_min_length') or 8)
        if len(new_password) < min_length:
            return jsonify({'ok': False, 'msg': f'Password minimal {min_length} karakter.'}), 400

        user = db.execute("SELECT * FROM users WHERE email=%s", (email,), fetch='one')
        if not user:
            return jsonify({'ok': False, 'msg': 'Email tidak ditemukan.'}), 404

        verified = False

        # Verify via token
        if token:
            reset_record = db.execute("""
                SELECT * FROM password_resets 
                WHERE user_id=%s AND token=%s AND is_used=0 AND expires_at > NOW()
                ORDER BY created_at DESC LIMIT 1
            """, (user['id'], token), fetch='one')

            if reset_record:
                db.execute("UPDATE password_resets SET is_used=1 WHERE id=%s", (reset_record['id'],), commit=True)
                verified = True

        if not verified:
            return jsonify({'ok': False, 'msg': 'Token reset tidak valid atau sudah kadaluarsa.'}), 401

        # Update password
        db.execute("""
            UPDATE users 
            SET password=%s, failed_login_attempts=0, locked_until=NULL, password_changed_at=NOW()
            WHERE id=%s
        """, (generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=16), user['id']), commit=True)

        log_audit(user['id'], 'password_reset', 'Password changed via reset flow')

        push_notification(
            user['id'],
            'Password Diubah',
            'Password Anda berhasil diubah. Jika ini bukan Anda, segera hubungi admin.',
            'warning'
        )

        return jsonify({'ok': True, 'msg': 'Password berhasil diubah. Silakan login dengan password baru.'})

    except Exception as e:
        logger.error(f'Reset password error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


# ─────────────────────────────────────────────
# AUTH — PASSWORD STRENGTH CHECK
# ─────────────────────────────────────────────
@app.route('/api/auth/check-password-strength', methods=['POST'])
def check_password_strength():
    """Check password strength (public endpoint)."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'ok': False, 'msg': 'Data tidak valid.'}), 400

        password = data.get('password', '')
        result = security.check_password_strength(password)

        return jsonify({
            'ok': True,
            'strength': result
        })

    except Exception as e:
        logger.error(f'Password strength check error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


# ─────────────────────────────────────────────
# PROFILE
# ─────────────────────────────────────────────
@app.route('/api/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update user profile."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'ok': False, 'msg': 'Data tidak valid.'}), 400

        allowed = ['full_name', 'phone', 'nik', 'address']
        updates = {k: security.sanitize(data[k]) for k in allowed if k in data}

        if not updates:
            return jsonify({'ok': False, 'msg': 'Tidak ada data untuk diperbarui.'}), 400

        set_clause = ', '.join(f'{k}=%s' for k in updates)
        vals = list(updates.values()) + [session['user_id']]

        db.execute(f"UPDATE users SET {set_clause} WHERE id=%s", tuple(vals), commit=True)

        if 'full_name' in updates:
            session['full_name'] = updates['full_name']

        log_audit(session['user_id'], 'profile_update', f'Fields: {list(updates.keys())}')

        return jsonify({'ok': True, 'msg': 'Profil berhasil diperbarui.'})

    except Exception as e:
        logger.error(f'Update profile error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


@app.route('/api/profile/avatar', methods=['POST'])
@login_required
def upload_avatar():
    """Upload user avatar."""
    try:
        if 'avatar' not in request.files:
            return jsonify({'ok': False, 'msg': 'Tidak ada file yang dikirim.'}), 400

        f = request.files['avatar']
        if not f or not security.allowed_file(f.filename):
            return jsonify({'ok': False, 'msg': 'Format file tidak didukung.'}), 400

        # Check file size
        f.seek(0, os.SEEK_END)
        file_size = f.tell()
        f.seek(0)

        max_size = int(get_setting('max_upload_mb') or 16) * 1024 * 1024
        if file_size > max_size:
            return jsonify({'ok': False, 'msg': f'File terlalu besar. Maksimal {max_size // (1024 * 1024)}MB.'}), 400

        ext = f.filename.rsplit('.', 1)[1].lower()
        filename = f"avatar_{session['user_id']}_{secrets.token_hex(6)}.{ext}"

        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        url = f'/static/uploads/{filename}'

        db.execute("UPDATE users SET avatar_url=%s WHERE id=%s", (url, session['user_id']), commit=True)

        log_audit(session['user_id'], 'avatar_upload', f'File: {filename}')

        return jsonify({'ok': True, 'avatar_url': url})

    except Exception as e:
        logger.error(f'Upload avatar error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


# ─────────────────────────────────────────────
# REPORTS — USER
# ─────────────────────────────────────────────
@app.route('/api/reports', methods=['POST'])
@login_required
def create_report():
    """Create new report."""
    try:
        data = request.form if request.files else request.get_json()
        if not data:
            return jsonify({'ok': False, 'msg': 'Data tidak valid.'}), 400

        title = security.sanitize(data.get('title', '')).strip()
        category = security.sanitize(data.get('category', '')).strip()
        subcategory = security.sanitize(data.get('subcategory', '')).strip()
        description = security.sanitize(data.get('description', '')).strip()
        loc_name = security.sanitize(data.get('location_name', '')).strip()
        lat = data.get('latitude')
        lng = data.get('longitude')
        address = security.sanitize(data.get('address_detail', '')).strip()
        district = security.sanitize(data.get('district', '')).strip()
        city = security.sanitize(data.get('city', '')).strip()
        province = security.sanitize(data.get('province', '')).strip()
        priority = data.get('priority', 'medium')
        # BUGFIX: str(True) == 'True' (capital) never matched the lowercase
        # tuple, so JSON boolean `true` from the frontend was silently
        # treated as non-anonymous. Normalize to lowercase before comparing.
        is_anon = 1 if str(data.get('is_anonymous', '0')).strip().lower() in ('1', 'true', 'yes', 'on') else 0

        if not all([title, category, description]):
            return jsonify({'ok': False, 'msg': 'Judul, kategori, dan deskripsi wajib diisi.'}), 400

        if len(title) < 10:
            return jsonify({'ok': False, 'msg': 'Judul terlalu pendek (min 10 karakter).'}), 400

        if len(description) < 20:
            return jsonify({'ok': False, 'msg': 'Deskripsi terlalu pendek (min 20 karakter).'}), 400

        ticket = security.generate_ticket()

        report_id = db.execute("""
            INSERT INTO reports
            (ticket_id, user_id, title, category, subcategory, description,
             location_name, latitude, longitude, address_detail, district, city, province,
             priority, is_anonymous)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (ticket, session['user_id'], title, category, subcategory, description,
              loc_name, lat, lng, address, district, city, province, priority, is_anon), commit=True)

        # Handle file attachments
        files = request.files.getlist('attachments')
        for f in files:
            if f and security.allowed_file(f.filename):
                ext = f.filename.rsplit('.', 1)[1].lower()
                fname = f"attach_{report_id}_{secrets.token_hex(6)}.{ext}"
                fpath = os.path.join(app.config['UPLOAD_FOLDER'], fname)
                f.save(fpath)

                ftype = 'image' if ext in {'png', 'jpg', 'jpeg', 'gif', 'webp'} else 'video' if ext in {'mp4',
                                                                                                        'mov'} else 'doc'
                # BUGFIX: FileStorage.content_length reflects the
                # Content-Length header of the multipart part, which browsers
                # frequently omit — it was routinely 0/None. Get the real
                # size from disk after saving instead.
                try:
                    fsize = os.path.getsize(fpath)
                except OSError:
                    fsize = 0

                db.execute("""
                    INSERT INTO report_attachments (report_id, file_url, file_type, file_size, file_name)
                    VALUES (%s, %s, %s, %s, %s)
                """, (report_id, f'/static/uploads/{fname}', ftype, fsize, f.filename), commit=True)

        log_timeline(report_id, session['user_id'], session['full_name'], 'Laporan dibuat', new_st='pending')

        push_notification(
            session['user_id'],
            'Laporan Berhasil Dikirim',
            f'Laporan #{ticket} Anda telah diterima dan sedang menunggu review.',
            'success',
            report_id
        )

        push_admin_notification(
            f'Laporan Baru: {title}',
            f'Pelapor: {session["full_name"]} | Kategori: {category} | Prioritas: {priority}',
            ntype='new_report',
            ref_id=report_id
        )

        return jsonify({
            'ok': True,
            'msg': 'Laporan berhasil dikirim!',
            'ticket_id': ticket,
            'report_id': report_id
        }), 201

    except Exception as e:
        logger.error(f'Create report error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


@app.route('/api/reports/my', methods=['GET'])
@login_required
def my_reports():
    """Get user's reports."""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 10)), 100)
        status = request.args.get('status')
        offset = (page - 1) * per_page

        where = "WHERE r.user_id=%s"
        params = [session['user_id']]

        if status:
            where += " AND r.status=%s"
            params.append(status)

        total = db.execute(f"SELECT COUNT(*) as cnt FROM reports r {where}", tuple(params), fetch='one')['cnt']
        params += [per_page, offset]

        rows = db.execute(f"""
            SELECT r.*, COUNT(a.id) as attachment_count
            FROM reports r
            LEFT JOIN report_attachments a ON a.report_id=r.id
            {where}
            GROUP BY r.id
            ORDER BY r.created_at DESC
            LIMIT %s OFFSET %s
        """, tuple(params))

        return jsonify({
            'ok': True,
            'reports': rows,
            'pagination': {
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': math.ceil(total / per_page) if total else 0
            }
        })

    except Exception as e:
        logger.error(f'Get my reports error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


@app.route('/api/reports/<int:report_id>', methods=['GET'])
@login_required
def get_report(report_id):
    """Get report details."""
    try:
        user_id = session['user_id']
        role = session.get('role')

        if role in ('admin', 'superadmin'):
            report = db.execute("""
                SELECT r.*, u.full_name, u.email, u.phone, u.nik, u.avatar_url 
                FROM reports r JOIN users u ON u.id=r.user_id WHERE r.id=%s
            """, (report_id,), fetch='one')
        else:
            report = db.execute("""
                SELECT * FROM reports WHERE id=%s AND user_id=%s
            """, (report_id, user_id), fetch='one')

        if not report:
            return jsonify({'ok': False, 'msg': 'Laporan tidak ditemukan.'}), 404

        attachments = db.execute("SELECT * FROM report_attachments WHERE report_id=%s", (report_id,))
        timeline = db.execute("""
            SELECT * FROM report_timeline 
            WHERE report_id=%s 
            ORDER BY created_at ASC
        """, (report_id,))

        return jsonify({
            'ok': True,
            'report': report,
            'attachments': attachments,
            'timeline': timeline
        })

    except Exception as e:
        logger.error(f'Get report error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


@app.route('/api/reports/track/<ticket_id>', methods=['GET'])
def track_report(ticket_id):
    """Public endpoint - track report by ticket ID."""
    try:
        report = db.execute("""
            SELECT r.ticket_id, r.title, r.category, r.status, r.priority, r.created_at, r.updated_at,
                   r.admin_notes, r.is_anonymous, u.full_name
            FROM reports r JOIN users u ON u.id=r.user_id
            WHERE r.ticket_id=%s
        """, (ticket_id,), fetch='one')

        if not report:
            return jsonify({'ok': False, 'msg': 'Nomor tiket tidak ditemukan.'}), 404

        if report['is_anonymous']:
            report['full_name'] = 'Anonim'

        timeline = db.execute("""
            SELECT action, old_status, new_status, notes, created_at 
            FROM report_timeline 
            WHERE report_id=(SELECT id FROM reports WHERE ticket_id=%s) 
            ORDER BY created_at ASC
        """, (ticket_id,))

        return jsonify({'ok': True, 'report': report, 'timeline': timeline})

    except Exception as e:
        logger.error(f'Track report error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


# ─────────────────────────────────────────────
# REPORTS — ADMIN
# ─────────────────────────────────────────────
@app.route('/api/admin/reports', methods=['GET'])
@admin_required
def admin_reports():
    """Get all reports (admin)."""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        status = request.args.get('status')
        category = request.args.get('category')
        priority = request.args.get('priority')
        search = request.args.get('search', '')
        sort = request.args.get('sort', 'created_at')
        order = 'DESC' if request.args.get('order', 'desc').lower() == 'desc' else 'ASC'
        offset = (page - 1) * per_page

        where_parts = ['1=1']
        params = []

        if status:
            where_parts.append('r.status=%s')
            params.append(status)
        if category:
            where_parts.append('r.category=%s')
            params.append(category)
        if priority:
            where_parts.append('r.priority=%s')
            params.append(priority)
        if search:
            where_parts.append('(r.title LIKE %s OR r.ticket_id LIKE %s OR u.full_name LIKE %s)')
            s = f'%{search}%'
            params += [s, s, s]

        where = 'WHERE ' + ' AND '.join(where_parts)

        total = db.execute(
            f"SELECT COUNT(*) as cnt FROM reports r JOIN users u ON u.id=r.user_id {where}",
            tuple(params),
            fetch='one'
        )['cnt']

        params += [per_page, offset]

        SORTABLE = {'created_at', 'updated_at', 'priority', 'status', 'title'}
        sort = sort if sort in SORTABLE else 'created_at'

        rows = db.execute(f"""
            SELECT r.*, u.full_name, u.email, u.phone, u.avatar_url,
                   COUNT(a.id) as attachment_count
            FROM reports r
            JOIN users u ON u.id=r.user_id
            LEFT JOIN report_attachments a ON a.report_id=r.id
            {where}
            GROUP BY r.id
            ORDER BY r.{sort} {order}
            LIMIT %s OFFSET %s
        """, tuple(params))

        return jsonify({
            'ok': True,
            'reports': rows,
            'pagination': {
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': math.ceil(max(total, 1) / per_page)
            }
        })

    except Exception as e:
        logger.error(f'Admin reports error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


@app.route('/api/admin/reports/<int:report_id>/status', methods=['PUT'])
@admin_required
def update_report_status(report_id):
    """Update report status (admin)."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'ok': False, 'msg': 'Data tidak valid.'}), 400

        new_status = data.get('status')
        notes = security.sanitize(data.get('notes', ''))

        VALID = ('pending', 'in_review', 'in_progress', 'resolved', 'rejected', 'closed')
        if new_status not in VALID:
            return jsonify({'ok': False, 'msg': 'Status tidak valid.'}), 400

        report = db.execute("SELECT * FROM reports WHERE id=%s", (report_id,), fetch='one')
        if not report:
            return jsonify({'ok': False, 'msg': 'Laporan tidak ditemukan.'}), 404

        old_status = report['status']

        # BUGFIX: the previous version embedded
        #   resolved_at={'NOW()' if new_status == 'resolved' else 'NULL'}
        # inside a plain (non f-) string, so Python never evaluated the
        # conditional expression — the literal text
        # "{'NOW()' if new_status == 'resolved' else 'NULL'}" was sent to
        # MySQL as SQL, which is a guaranteed syntax error on every single
        # status update. Fixed by building the clause first and using an
        # f-string only for the safe, hardcoded SQL fragment (never for
        # user input — status/notes/report_id still go through %s params).
        resolved_clause = "resolved_at=NOW()" if new_status == 'resolved' else "resolved_at=NULL"
        db.execute(f"""
            UPDATE reports 
            SET status=%s, admin_notes=%s, {resolved_clause}
            WHERE id=%s
        """, (new_status, notes, report_id), commit=True)

        log_timeline(
            report_id,
            session['user_id'],
            session['full_name'],
            f'Status diperbarui ke {new_status}',
            old_status,
            new_status,
            notes
        )

        STATUS_MSG = {
            'in_review': 'Laporan Anda sedang direview oleh tim kami.',
            'in_progress': 'Laporan Anda sedang dalam penanganan.',
            'resolved': 'Laporan Anda telah diselesaikan. Terima kasih!',
            'rejected': 'Laporan Anda ditolak. Silakan hubungi admin.',
            'closed': 'Laporan Anda telah ditutup.',
        }

        msg = STATUS_MSG.get(new_status, f'Status laporan Anda diperbarui ke {new_status}.')

        push_notification(
            report['user_id'],
            f'Status Laporan #{report["ticket_id"]} Diperbarui',
            f'{msg}' + (f' Catatan admin: {notes}' if notes else ''),
            'info',
            report_id
        )

        return jsonify({'ok': True, 'msg': 'Status laporan berhasil diperbarui.'})

    except Exception as e:
        logger.error(f'Update report status error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


# ─────────────────────────────────────────────
# ADMIN — DASHBOARD STATS
# ─────────────────────────────────────────────
@app.route('/api/admin/stats', methods=['GET'])
@admin_required
def admin_stats():
    """Get admin dashboard statistics."""
    try:
        total = db.execute("SELECT COUNT(*) as c FROM reports", fetch='one')['c']
        pending = db.execute("SELECT COUNT(*) as c FROM reports WHERE status='pending'", fetch='one')['c']
        in_progress = \
        db.execute("SELECT COUNT(*) as c FROM reports WHERE status IN('in_review','in_progress')", fetch='one')['c']
        resolved = db.execute("SELECT COUNT(*) as c FROM reports WHERE status='resolved'", fetch='one')['c']
        total_users = db.execute("SELECT COUNT(*) as c FROM users WHERE role='user'", fetch='one')['c']
        sos_active = db.execute("SELECT COUNT(*) as c FROM sos_events WHERE status='active'", fetch='one')['c']

        daily = db.execute("""
            SELECT DATE(created_at) as day, COUNT(*) as count
            FROM reports
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY DATE(created_at)
            ORDER BY day ASC
        """)

        by_category = db.execute("""
            SELECT category, COUNT(*) as count
            FROM reports GROUP BY category ORDER BY count DESC LIMIT 10
        """)

        by_status = db.execute("""
            SELECT status, COUNT(*) as count FROM reports GROUP BY status
        """)

        by_priority = db.execute("""
            SELECT priority, COUNT(*) as count FROM reports GROUP BY priority
        """)

        sos = db.execute("""
            SELECT s.*, u.full_name, u.phone
            FROM sos_events s JOIN users u ON u.id=s.user_id
            WHERE s.status='active' ORDER BY s.created_at DESC LIMIT 5
        """)

        top_reporters = db.execute("""
            SELECT u.full_name, u.email, COUNT(r.id) as report_count
            FROM users u JOIN reports r ON r.user_id=u.id
            GROUP BY u.id ORDER BY report_count DESC LIMIT 5
        """)

        return jsonify({
            'ok': True,
            'stats': {
                'total': total,
                'pending': pending,
                'in_progress': in_progress,
                'resolved': resolved,
                'total_users': total_users,
                'sos_active': sos_active,
            },
            'daily': daily,
            'by_category': by_category,
            'by_status': by_status,
            'by_priority': by_priority,
            'sos': sos,
            'top_reporters': top_reporters,
        })

    except Exception as e:
        logger.error(f'Admin stats error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


# ─────────────────────────────────────────────
# ADMIN — USER MANAGEMENT
# ─────────────────────────────────────────────

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def admin_users():
    """Get all users (admin) with pagination and search."""
    try:
        page = int(request.args.get('page', 1))
        per_page = min(int(request.args.get('per_page', 20)), 100)
        search = request.args.get('search', '')
        offset = (page - 1) * per_page

        where = "WHERE role='user'"
        params = []

        if search:
            where += " AND (full_name LIKE %s OR email LIKE %s OR phone LIKE %s)"
            s = f'%{search}%'
            params += [s, s, s]

        total = db.execute(f"SELECT COUNT(*) as c FROM users {where}", tuple(params), fetch='one')['c']
        params += [per_page, offset]

        rows = db.execute(f"""
            SELECT u.id, u.uid, u.full_name, u.email, u.phone, u.nik, u.address,
                   u.avatar_url, u.is_active, u.is_verified, u.auth_provider, u.last_login, u.login_count, u.created_at,
                   COUNT(r.id) as report_count
            FROM users u LEFT JOIN reports r ON r.user_id=u.id
            {where}
            GROUP BY u.id ORDER BY u.created_at DESC
            LIMIT %s OFFSET %s
        """, tuple(params))

        return jsonify({
            'ok': True,
            'users': rows,
            'pagination': {
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': math.ceil(max(total, 1) / per_page)
            }
        }), 200

    except Exception as e:
        logger.error(f'Admin users error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


@app.route('/api/admin/users/<int:user_id>', methods=['GET'])
@admin_required
def get_admin_user_detail(user_id):
    """Get single user detail for admin dashboard (SOLUSI ERROR 404)."""
    try:
        # Mengambil data detail user dan menghitung total laporan yang pernah dibuat
        user = db.execute("""
            SELECT u.id, u.uid, u.full_name, u.email, u.phone, u.nik, u.address,
                   u.avatar_url, u.is_active, u.is_verified, u.auth_provider, u.last_login, u.login_count, u.created_at,
                   COUNT(r.id) as report_count
            FROM users u 
            LEFT JOIN reports r ON r.user_id = u.id
            WHERE u.id = %s AND u.role = 'user'
            GROUP BY u.id
        """, (user_id,), fetch='one')

        if not user:
            return jsonify({'ok': False, 'msg': 'User tidak ditemukan.'}), 404

        return jsonify({
            'ok': True,
            'user': user
        }), 200

    except Exception as e:
        logger.error(f'Get admin user detail error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


@app.route('/api/admin/users/<int:user_id>/toggle', methods=['PUT'])
@admin_required
def toggle_user(user_id):
    """Toggle user active status."""
    try:
        user = db.execute(
            "SELECT is_active, full_name FROM users WHERE id=%s AND role='user'",
            (user_id,),
            fetch='one'
        )

        if not user:
            return jsonify({'ok': False, 'msg': 'User tidak ditemukan.'}), 404

        new_state = 0 if user['is_active'] else 1
        db.execute("UPDATE users SET is_active=%s WHERE id=%s", (new_state, user_id), commit=True)

        action = 'diaktifkan' if new_state else 'dinonaktifkan'
        log_audit(user_id, f'account_{"activated" if new_state else "deactivated"}', f'By admin {session["user_id"]}')

        return jsonify({
            'ok': True,
            'msg': f'Akun {user["full_name"]} berhasil {action}.',
            'is_active': new_state
        }), 200

    except Exception as e:
        logger.error(f'Toggle user error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500

# ─────────────────────────────────────────────
# SOS
# ─────────────────────────────────────────────
@app.route('/api/sos', methods=['POST'])
@login_required
def trigger_sos():
    """Trigger SOS emergency."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'ok': False, 'msg': 'Data tidak valid.'}), 400

        lat = data.get('latitude')
        lng = data.get('longitude')
        msg = security.sanitize(data.get('message', 'Bantuan diperlukan!'))
        addr = security.sanitize(data.get('address', ''))

        if not lat or not lng:
            return jsonify({'ok': False, 'msg': 'Koordinat lokasi wajib disertakan.'}), 400

        sos_id = db.execute("""
            INSERT INTO sos_events (user_id, latitude, longitude, address, message)
            VALUES (%s, %s, %s, %s, %s)
        """, (session['user_id'], lat, lng, addr, msg), commit=True)

        user = db.execute(
            "SELECT full_name, phone FROM users WHERE id=%s",
            (session['user_id'],),
            fetch='one'
        )

        push_admin_notification(
            f'SOS DARURAT dari {user["full_name"]}',
            f'Lokasi: {addr or f"{lat},{lng}"} | Pesan: {msg} | Tel: {user["phone"]}',
            ntype='sos',
            ref_id=sos_id
        )

        push_notification(
            session['user_id'],
            'SOS Dikirim',
            'Tim darurat telah diberitahu lokasi Anda. Tetap tenang.',
            'warning'
        )

        logger.info(f'SOS triggered by user {session["user_id"]} at {lat},{lng}')

        return jsonify({
            'ok': True,
            'msg': 'SOS berhasil dikirim! Tim kami akan segera merespons.',
            'sos_id': sos_id
        })

    except Exception as e:
        logger.error(f'Trigger SOS error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


@app.route('/api/sos/active', methods=['GET'])
@admin_required
def active_sos():
    """Get active SOS events."""
    try:
        rows = db.execute("""
            SELECT s.*, u.full_name, u.phone, u.email
            FROM sos_events s JOIN users u ON u.id=s.user_id
            WHERE s.status='active' ORDER BY s.created_at DESC
        """)

        return jsonify({'ok': True, 'sos': rows})

    except Exception as e:
        logger.error(f'Get active SOS error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


# ─────────────────────────────────────────────
# NOTIFICATIONS (USER & ADMIN)
# ─────────────────────────────────────────────

@app.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    """Get user notifications."""
    try:
        # Optimasi: Sebutkan kolom secara spesifik dibanding menggunakan SELECT *
        rows = db.execute("""
            SELECT id, title, message, is_read, created_at 
            FROM notifications 
            WHERE user_id = %s
            ORDER BY created_at DESC LIMIT 50
        """, (session['user_id'],))

        unread = db.execute("""
            SELECT COUNT(*) as c FROM notifications 
            WHERE user_id = %s AND is_read = 0
        """, (session['user_id'],), fetch='one')['c']

        return jsonify({'ok': True, 'notifications': rows, 'unread': unread}), 200

    except Exception as e:
        logger.error(f'Get notifications error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


@app.route('/api/notifications/read-all', methods=['PUT'])
@login_required
def read_all_notifications():
    """Mark all user notifications as read."""
    try:
        db.execute(
            "UPDATE notifications SET is_read = 1 WHERE user_id = %s",
            (session['user_id'],),
            commit=True
        )
        return jsonify({'ok': True, 'msg': 'Semua notifikasi pengguna ditandai dibaca.'}), 200

    except Exception as e:
        logger.error(f'Read all notifications error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


@app.route('/api/admin/notifications', methods=['GET'])
@admin_required
def admin_notifications():
    """Get admin notifications."""
    try:
        # Optimasi: Menyebutkan kolom yang dibutuhkan saja
        rows = db.execute("""
            SELECT id, title, message, is_read, created_at 
            FROM admin_notifications 
            ORDER BY created_at DESC LIMIT 100
        """)

        unread = db.execute("""
            SELECT COUNT(*) as c 
            FROM admin_notifications 
            WHERE is_read = 0
        """, fetch='one')['c']

        return jsonify({'ok': True, 'notifications': rows, 'unread': unread}), 200

    except Exception as e:
        logger.error(f'Get admin notifications error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


@app.route('/api/admin/notifications/read-all', methods=['PUT'])
@admin_required
def read_all_admin_notifications():
    """Mark all admin notifications as read (SOLUSI ERROR 404)."""
    try:
        # Mengubah semua notifikasi admin menjadi sudah dibaca (is_read=1)
        db.execute(
            "UPDATE admin_notifications SET is_read = 1 WHERE is_read = 0",
            commit=True
        )
        return jsonify({'ok': True, 'msg': 'Semua notifikasi admin berhasil ditandai dibaca.'}), 200

    except Exception as e:
        logger.error(f'Read all admin notifications error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500

# ─────────────────────────────────────────────
# MAPS
# ─────────────────────────────────────────────
@app.route('/api/admin/maps/reports', methods=['GET'])
@admin_required
def map_reports():
    """Get reports with location for map."""
    try:
        rows = db.execute("""
            SELECT r.id, r.ticket_id, r.title, r.category, r.status, r.priority,
                   r.latitude, r.longitude, r.location_name, r.address_detail, r.created_at,
                   u.full_name, u.phone
            FROM reports r JOIN users u ON u.id=r.user_id
            WHERE r.latitude IS NOT NULL AND r.longitude IS NOT NULL
            ORDER BY r.created_at DESC LIMIT 1000
        """)

        return jsonify({'ok': True, 'markers': rows})

    except Exception as e:
        logger.error(f'Map reports error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


@app.route('/api/admin/maps/sos', methods=['GET'])
@admin_required
def map_sos():
    """Get SOS events for map."""
    try:
        rows = db.execute("""
            SELECT s.*, u.full_name, u.phone
            FROM sos_events s JOIN users u ON u.id=s.user_id
            WHERE s.latitude IS NOT NULL ORDER BY s.created_at DESC LIMIT 100
        """)

        return jsonify({'ok': True, 'markers': rows})

    except Exception as e:
        logger.error(f'Map SOS error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


# ─────────────────────────────────────────────
# SETTINGS
# ─────────────────────────────────────────────
@app.route('/api/admin/settings', methods=['GET'])
@admin_required
def get_settings():
    """Get system settings."""
    try:
        rows = db.execute("SELECT `key`, value FROM system_settings")
        return jsonify({'ok': True, 'settings': {r['key']: r['value'] for r in rows}})

    except Exception as e:
        logger.error(f'Get settings error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


@app.route('/api/admin/settings', methods=['PUT'])
@admin_required
def update_settings():
    """Update system settings."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'ok': False, 'msg': 'Data tidak valid.'}), 400

        for k, v in data.items():
            db.execute("UPDATE system_settings SET value=%s WHERE `key`=%s", (v, k), commit=True)

        log_audit(session['user_id'], 'settings_update', f'Keys: {list(data.keys())}')

        return jsonify({'ok': True, 'msg': 'Pengaturan berhasil disimpan.'})

    except Exception as e:
        logger.error(f'Update settings error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


# ─────────────────────────────────────────────
# PUBLIC STATS
# ─────────────────────────────────────────────
@app.route('/api/public/stats', methods=['GET'])
def public_stats():
    """Get public statistics for landing page."""
    try:
        total = db.execute("SELECT COUNT(*) as c FROM reports", fetch='one')['c']
        resolved = db.execute("SELECT COUNT(*) as c FROM reports WHERE status='resolved'", fetch='one')['c']
        users = db.execute("SELECT COUNT(*) as c FROM users WHERE role='user'", fetch='one')['c']

        return jsonify({'ok': True, 'total': total, 'resolved': resolved, 'users': users})

    except Exception as e:
        logger.error(f'Public stats error: {e}')
        return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


# ─────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────
@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    try:
        db.execute("SELECT 1 as ok", fetch='one')
        db_ok = True
    except:
        db_ok = False

    return jsonify({
        'ok': db_ok,
        'timestamp': datetime.datetime.now().isoformat(),
        'version': '3.0.1',
        'google_oauth': GOOGLE_AUTH_AVAILABLE,
        'http_client': HTTP_AVAILABLE,
        'redis_cache': cache.redis_client is not None
    })


# ─────────────────────────────────────────────
# ERROR HANDLERS
# ─────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({'ok': False, 'msg': 'Endpoint tidak ditemukan.'}), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    logger.error(f'Server error: {e}')
    return jsonify({'ok': False, 'msg': 'Terjadi kesalahan server.'}), 500


@app.errorhandler(413)
def too_large(e):
    """Handle 413 errors."""
    return jsonify({'ok': False, 'msg': 'File terlalu besar. Maksimal 16MB.'}), 413


@app.errorhandler(429)
def rate_limit_exceeded(e):
    """Handle 429 errors."""
    return jsonify({'ok': False, 'msg': 'Terlalu banyak permintaan. Coba lagi nanti.'}), 429

try:
    init_db()
except Exception as e:
    logger.error(f'❌ DB init failed: {e}')
    print(f'⚠️  DB init warning: {e}')

db = DatabasePool()


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == '__main__':
    print('=' * 70)
    print('🚀  LaporPublik Backend v3.0 Starting...')
    print('=' * 70)
    print(f'   Environment:    {app.config["ENV"]}')
    print(f'   Debug Mode:     {app.config["DEBUG"]}')
    _google_ready = GOOGLE_AUTH_AVAILABLE and bool(app.config.get('GOOGLE_CLIENT_ID'))
    print(f'   Google OAuth:   {"✅ Ready" if _google_ready else "❌ " + ("Library belum terinstall" if not GOOGLE_AUTH_AVAILABLE else "GOOGLE_CLIENT_ID kosong di .env")}')
    print(f'   HTTP Client:    {"✅ Available" if HTTP_AVAILABLE else "❌ Not installed"}')
    print(f'   Redis Cache:    {"✅ Available" if REDIS_AVAILABLE else "❌ Not installed"}')
    print(f'   Database:       {app.config["DB_HOST"]}:{app.config["DB_PORT"]}/{app.config["DB_NAME"]}')
    print('=' * 70)

    port = int(os.environ.get('PORT', 5001))
    debug = app.config['DEBUG']

    print(f'\n🌐  Server running at: http://0.0.0.0:{port}')
    print(f'📊  Health check: http://localhost:{port}/api/health')
    print(f'🔐  Login page: http://localhost:{port}/login')
    print('=' * 70)

    app.run(host='0.0.0.0', port=port, debug=debug)
