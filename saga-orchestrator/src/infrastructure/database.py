import os
import logging
from sqlalchemy import create_engine, Column, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional, List
from ..domain.saga_state import SagaState, SagaStatus, SagaStep


Base = declarative_base()


class SagaStateModel(Base):
    """SQLAlchemy model for saga state persistence"""
    __tablename__ = 'saga_states'
    
    saga_id = Column(String, primary_key=True)
    correlation_id = Column(String, nullable=True)
    status = Column(String, nullable=False)
    current_step = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    partner_data = Column(JSON, nullable=True)
    partner_id = Column(String, nullable=True)
    alliance_id = Column(String, nullable=True)
    error = Column(Text, nullable=True)
    compensation_actions = Column(JSON, nullable=True)
    steps = Column(JSON, nullable=True)


class SagaRepository:
    """Repository for saga state persistence"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/saga_db')
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.logger = logging.getLogger(__name__)
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def save_saga_state(self, saga_state: SagaState) -> bool:
        """Save saga state to database"""
        try:
            with self.get_session() as session:
                # Convert saga state to model
                saga_model = SagaStateModel(
                    saga_id=saga_state.saga_id,
                    correlation_id=saga_state.correlation_id,
                    status=saga_state.status.value,
                    current_step=saga_state.current_step.value if saga_state.current_step else None,
                    created_at=saga_state.created_at,
                    updated_at=saga_state.updated_at,
                    completed_at=saga_state.completed_at,
                    partner_data=saga_state.partner_data,
                    partner_id=saga_state.partner_id,
                    alliance_id=saga_state.alliance_id,
                    error=saga_state.error,
                    compensation_actions=saga_state.compensation_actions,
                    steps={
                        step.value: {
                            "status": execution.status,
                            "started_at": execution.started_at.isoformat() if execution.started_at else None,
                            "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                            "error": execution.error,
                            "result": execution.result
                        }
                        for step, execution in saga_state.steps.items()
                    }
                )
                
                # Merge (insert or update)
                session.merge(saga_model)
                session.commit()
                
                self.logger.info(f"Saved saga state for saga_id: {saga_state.saga_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to save saga state {saga_state.saga_id}: {e}")
            return False
    
    def get_saga_state(self, saga_id: str) -> Optional[SagaState]:
        """Get saga state by ID"""
        try:
            with self.get_session() as session:
                saga_model = session.query(SagaStateModel).filter(
                    SagaStateModel.saga_id == saga_id
                ).first()
                
                if not saga_model:
                    return None
                
                # Convert model to domain object
                saga_state = SagaState(
                    saga_id=saga_model.saga_id,
                    correlation_id=saga_model.correlation_id,
                    status=SagaStatus(saga_model.status),
                    current_step=SagaStep(saga_model.current_step) if saga_model.current_step else None,
                    created_at=saga_model.created_at,
                    updated_at=saga_model.updated_at,
                    completed_at=saga_model.completed_at,
                    partner_data=saga_model.partner_data,
                    partner_id=saga_model.partner_id,
                    alliance_id=saga_model.alliance_id,
                    error=saga_model.error,
                    compensation_actions=saga_model.compensation_actions or []
                )
                
                # Reconstruct steps
                if saga_model.steps:
                    from ..domain.saga_state import SagaStepExecution
                    for step_name, step_data in saga_model.steps.items():
                        step = SagaStep(step_name)
                        execution = SagaStepExecution(
                            step=step,
                            status=step_data["status"],
                            started_at=datetime.fromisoformat(step_data["started_at"]) if step_data["started_at"] else None,
                            completed_at=datetime.fromisoformat(step_data["completed_at"]) if step_data["completed_at"] else None,
                            error=step_data["error"],
                            result=step_data["result"]
                        )
                        saga_state.steps[step] = execution
                
                return saga_state
                
        except Exception as e:
            self.logger.error(f"Failed to get saga state {saga_id}: {e}")
            return None
    
    def get_active_sagas(self) -> List[SagaState]:
        """Get all active (non-completed, non-failed) sagas"""
        try:
            with self.get_session() as session:
                saga_models = session.query(SagaStateModel).filter(
                    SagaStateModel.status.in_([
                        SagaStatus.STARTED.value,
                        SagaStatus.PARTNER_CREATION_IN_PROGRESS.value,
                        SagaStatus.PARTNER_CREATED.value,
                        SagaStatus.ALLIANCE_CREATION_IN_PROGRESS.value,
                        SagaStatus.ALLIANCE_CREATED.value,
                        SagaStatus.COMPENSATING.value
                    ])
                ).all()
                
                sagas = []
                for saga_model in saga_models:
                    saga_state = self.get_saga_state(saga_model.saga_id)
                    if saga_state:
                        sagas.append(saga_state)
                
                return sagas
                
        except Exception as e:
            self.logger.error(f"Failed to get active sagas: {e}")
            return []
    
    def get_sagas_by_correlation_id(self, correlation_id: str) -> List[SagaState]:
        """Get sagas by correlation ID"""
        try:
            with self.get_session() as session:
                saga_models = session.query(SagaStateModel).filter(
                    SagaStateModel.correlation_id == correlation_id
                ).all()
                
                sagas = []
                for saga_model in saga_models:
                    saga_state = self.get_saga_state(saga_model.saga_id)
                    if saga_state:
                        sagas.append(saga_state)
                
                return sagas
                
        except Exception as e:
            self.logger.error(f"Failed to get sagas by correlation_id {correlation_id}: {e}")
            return []
    
    def delete_saga_state(self, saga_id: str) -> bool:
        """Delete saga state (for cleanup)"""
        try:
            with self.get_session() as session:
                saga_model = session.query(SagaStateModel).filter(
                    SagaStateModel.saga_id == saga_id
                ).first()
                
                if saga_model:
                    session.delete(saga_model)
                    session.commit()
                    self.logger.info(f"Deleted saga state for saga_id: {saga_id}")
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to delete saga state {saga_id}: {e}")
            return False
