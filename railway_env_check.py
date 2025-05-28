"""
Railway Environment Validation
Ensures all required environment variables are set correctly
"""
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_railway_environment():
    """Check and validate Railway environment variables"""
    logger.info("🔍 Checking Railway environment...")
    
    # Required environment variables
    required_vars = {
        'DATABASE_URL': 'PostgreSQL database connection string',
        'ANTHROPIC_API_KEY': 'Anthropic Claude API key for conversations'
    }
    
    # Optional environment variables with defaults
    optional_vars = {
        'RAILWAY_SERVICE': 'teacher',
        'APP_ENV': 'production',
        'DEBUG': 'false',
        'PORT': '8000',
        'HOST': '0.0.0.0'
    }
    
    all_good = True
    
    # Check required variables
    logger.info("📋 Required environment variables:")
    for var, description in required_vars.items():
        value = os.environ.get(var)
        if value:
            # Hide sensitive values in logs
            if 'KEY' in var or 'PASSWORD' in var or 'SECRET' in var:
                display_value = f"{value[:8]}..." if len(value) > 8 else "***"
                logger.info(f"  ✅ {var}: {display_value}")
            elif 'DATABASE_URL' in var:
                # Show database type without credentials
                if value.startswith('postgresql://'):
                    logger.info(f"  ✅ {var}: postgresql://***@{value.split('@')[1] if '@' in value else '***'}")
                else:
                    logger.info(f"  ✅ {var}: {value}")
            else:
                logger.info(f"  ✅ {var}: {value}")
        else:
            logger.error(f"  ❌ {var}: MISSING - {description}")
            all_good = False
    
    # Check optional variables
    logger.info("🔧 Optional environment variables:")
    for var, default in optional_vars.items():
        value = os.environ.get(var, default)
        logger.info(f"  📝 {var}: {value}")
    
    # Railway-specific checks
    logger.info("🚂 Railway-specific environment:")
    railway_vars = [
        'RAILWAY_DEPLOYMENT_ID', 'RAILWAY_ENVIRONMENT_NAME', 
        'RAILWAY_PROJECT_NAME', 'RAILWAY_SERVICE_NAME'
    ]
    
    for var in railway_vars:
        value = os.environ.get(var)
        if value:
            logger.info(f"  🚂 {var}: {value}")
    
    # Check Python path
    python_path = os.environ.get('PYTHONPATH', '')
    logger.info(f"🐍 PYTHONPATH: {python_path or 'Not set'}")
    
    if all_good:
        logger.info("✅ All required environment variables are set!")
    else:
        logger.error("❌ Missing required environment variables!")
    
    return all_good


def setup_railway_environment():
    """Set default environment variables for Railway if not already set"""
    logger.info("🔧 Setting up Railway environment defaults...")
    
    defaults = {
        'APP_ENV': 'production',
        'DEBUG': 'false',
        'RAILWAY_SERVICE': 'teacher',
        'PYTHONPATH': '/app'
    }
    
    for var, default_value in defaults.items():
        current_value = os.environ.get(var)
        if not current_value:
            os.environ[var] = default_value
            logger.info(f"  📝 Set {var} = {default_value}")
        else:
            logger.info(f"  ✅ {var} already set to: {current_value}")


if __name__ == "__main__":
    setup_railway_environment()
    success = check_railway_environment()
    
    if success:
        logger.info("🎉 Railway environment is ready!")
        sys.exit(0)
    else:
        logger.error("💥 Railway environment setup failed!")
        sys.exit(1)
