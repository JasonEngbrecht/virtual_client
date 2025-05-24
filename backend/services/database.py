"""
Base database service
Provides database session management and base CRUD operations
"""

from typing import Type, TypeVar, Generic, List, Optional, Dict, Any
from sqlalchemy import create_engine, select, update, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, DeclarativeMeta
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from pathlib import Path
import logging

from ..config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Create base class for SQLAlchemy models
Base = declarative_base()

# Type variables for generic CRUD operations
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class DatabaseService:
    """
    Base database service providing session management
    """
    
    def __init__(self, database_url: str = None):
        """
        Initialize database service
        
        Args:
            database_url: Database connection URL (uses settings default if not provided)
        """
        self.database_url = database_url or settings.database_url
        
        # Handle SQLite relative paths
        if self.database_url.startswith("sqlite:///./"):
            # Convert relative path to absolute
            db_path = self.database_url.replace("sqlite:///./", "")
            project_root = Path(__file__).parent.parent.parent
            absolute_path = project_root / db_path
            self.database_url = f"sqlite:///{absolute_path}"
        
        # Create engine
        # Only echo SQL in debug mode and not during tests
        echo_sql = settings.debug and not self._is_test_mode()
        self.engine = create_engine(
            self.database_url,
            connect_args={"check_same_thread": False} if "sqlite" in self.database_url else {},
            echo=echo_sql
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        logger.info(f"Database service initialized with URL: {self.database_url}")
    
    def _is_test_mode(self) -> bool:
        """Check if we're running in test mode"""
        import sys
        import os
        # Check if pytest is running or if we're in a test environment
        return (
            "pytest" in sys.modules or
            "test" in sys.argv[0] or
            os.environ.get("PYTEST_CURRENT_TEST") is not None
        )
    
    @contextmanager
    def get_db(self) -> Session:
        """
        Context manager for database sessions
        
        Yields:
            Session: SQLAlchemy database session
        """
        db = self.SessionLocal()
        try:
            yield db
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            db.rollback()
            raise
        finally:
            db.close()
    
    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created")


class BaseCRUD(Generic[ModelType], DatabaseService):
    """
    Generic CRUD operations for SQLAlchemy models
    Inherit from this class to create model-specific CRUD services
    """
    
    def __init__(self, model: Type[ModelType], database_url: str = None):
        """
        Initialize CRUD service for a specific model
        
        Args:
            model: SQLAlchemy model class
            database_url: Database connection URL (optional)
        """
        super().__init__(database_url)
        self.model = model
    
    def create(self, db: Session, **kwargs) -> ModelType:
        """
        Create a new record
        
        Args:
            db: Database session
            **kwargs: Model field values
            
        Returns:
            Created model instance
        """
        try:
            db_obj = self.model(**kwargs)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Created {self.model.__name__} with id: {getattr(db_obj, 'id', 'unknown')}")
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"Error creating {self.model.__name__}: {e}")
            db.rollback()
            raise
    
    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        Get a single record by ID
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            Model instance or None if not found
        """
        try:
            result = db.query(self.model).filter(self.model.id == id).first()
            if result:
                logger.debug(f"Retrieved {self.model.__name__} with id: {id}")
            else:
                logger.debug(f"{self.model.__name__} not found with id: {id}")
            return result
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving {self.model.__name__}: {e}")
            raise
    
    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        **filters
    ) -> List[ModelType]:
        """
        Get multiple records with optional filtering
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            **filters: Field filters (field_name=value)
            
        Returns:
            List of model instances
        """
        try:
            query = db.query(self.model)
            
            # Apply filters
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)
            
            results = query.offset(skip).limit(limit).all()
            logger.debug(f"Retrieved {len(results)} {self.model.__name__} records")
            return results
        except SQLAlchemyError as e:
            logger.error(f"Error retrieving {self.model.__name__} records: {e}")
            raise
    
    def update(
        self,
        db: Session,
        id: Any,
        **kwargs
    ) -> Optional[ModelType]:
        """
        Update a record
        
        Args:
            db: Database session
            id: Record ID
            **kwargs: Fields to update
            
        Returns:
            Updated model instance or None if not found
        """
        try:
            db_obj = self.get(db, id)
            if not db_obj:
                return None
            
            # Update fields
            for field, value in kwargs.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Updated {self.model.__name__} with id: {id}")
            return db_obj
        except SQLAlchemyError as e:
            logger.error(f"Error updating {self.model.__name__}: {e}")
            db.rollback()
            raise
    
    def delete(self, db: Session, id: Any) -> bool:
        """
        Delete a record
        
        Args:
            db: Database session
            id: Record ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            db_obj = self.get(db, id)
            if not db_obj:
                return False
            
            db.delete(db_obj)
            db.commit()
            logger.info(f"Deleted {self.model.__name__} with id: {id}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error deleting {self.model.__name__}: {e}")
            db.rollback()
            raise
    
    def count(self, db: Session, **filters) -> int:
        """
        Count records with optional filtering
        
        Args:
            db: Database session
            **filters: Field filters
            
        Returns:
            Number of records
        """
        try:
            query = db.query(self.model)
            
            # Apply filters
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)
            
            count = query.count()
            logger.debug(f"Counted {count} {self.model.__name__} records")
            return count
        except SQLAlchemyError as e:
            logger.error(f"Error counting {self.model.__name__} records: {e}")
            raise
    
    def exists(self, db: Session, **filters) -> bool:
        """
        Check if a record exists with given filters
        
        Args:
            db: Database session
            **filters: Field filters
            
        Returns:
            True if exists, False otherwise
        """
        return self.count(db, **filters) > 0


# Global database service instance
db_service = DatabaseService()

# Dependency function for FastAPI
def get_db():
    """
    Dependency function for FastAPI to get database sessions
    
    Yields:
        Session: SQLAlchemy database session
    """
    with db_service.get_db() as db:
        yield db
