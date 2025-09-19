from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
import uuid


class SagaStatus(Enum):
    """Saga execution status"""
    STARTED = "started"
    PARTNER_CREATION_IN_PROGRESS = "partner_creation_in_progress"
    PARTNER_CREATED = "partner_created"
    ALLIANCE_CREATION_IN_PROGRESS = "alliance_creation_in_progress"
    ALLIANCE_CREATED = "alliance_created"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


class SagaStep(Enum):
    """Individual steps in the saga"""
    CREATE_PARTNER = "create_partner"
    CREATE_ALLIANCE = "create_alliance"
    COMPLETE_SAGA = "complete_saga"


@dataclass
class SagaStepExecution:
    """Represents the execution of a single saga step"""
    step: SagaStep
    status: str  # "pending", "in_progress", "completed", "failed", "compensated"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    compensation_data: Optional[Dict[str, Any]] = None


@dataclass
class SagaState:
    """Represents the current state of a saga execution"""
    saga_id: str
    correlation_id: Optional[str]
    status: SagaStatus
    current_step: Optional[SagaStep]
    steps: Dict[SagaStep, SagaStepExecution] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    partner_data: Optional[Dict[str, Any]] = None
    partner_id: Optional[str] = None
    alliance_id: Optional[str] = None
    error: Optional[str] = None
    compensation_actions: List[str] = field(default_factory=list)

    @classmethod
    def create_new(cls, partner_data: Dict[str, Any], correlation_id: Optional[str] = None) -> 'SagaState':
        """Create a new saga state"""
        saga_id = str(uuid.uuid4())
        
        # Initialize all steps as pending
        steps = {
            SagaStep.CREATE_PARTNER: SagaStepExecution(
                step=SagaStep.CREATE_PARTNER,
                status="pending"
            ),
            SagaStep.CREATE_ALLIANCE: SagaStepExecution(
                step=SagaStep.CREATE_ALLIANCE,
                status="pending"
            ),
            SagaStep.COMPLETE_SAGA: SagaStepExecution(
                step=SagaStep.COMPLETE_SAGA,
                status="pending"
            )
        }
        
        return cls(
            saga_id=saga_id,
            correlation_id=correlation_id,
            status=SagaStatus.STARTED,
            current_step=SagaStep.CREATE_PARTNER,
            steps=steps,
            partner_data=partner_data
        )

    def start_step(self, step: SagaStep) -> None:
        """Mark a step as started"""
        if step in self.steps:
            self.steps[step].status = "in_progress"
            self.steps[step].started_at = datetime.utcnow()
            self.current_step = step
            self.updated_at = datetime.utcnow()

    def complete_step(self, step: SagaStep, result: Optional[Dict[str, Any]] = None) -> None:
        """Mark a step as completed"""
        if step in self.steps:
            self.steps[step].status = "completed"
            self.steps[step].completed_at = datetime.utcnow()
            self.steps[step].result = result
            self.updated_at = datetime.utcnow()

    def fail_step(self, step: SagaStep, error: str) -> None:
        """Mark a step as failed"""
        if step in self.steps:
            self.steps[step].status = "failed"
            self.steps[step].completed_at = datetime.utcnow()
            self.steps[step].error = error
            self.updated_at = datetime.utcnow()
            self.error = error

    def set_partner_created(self, partner_id: str) -> None:
        """Set partner as created"""
        self.partner_id = partner_id
        self.status = SagaStatus.PARTNER_CREATED
        self.complete_step(SagaStep.CREATE_PARTNER, {"partner_id": partner_id})

    def set_alliance_created(self, alliance_id: str) -> None:
        """Set alliance as created"""
        self.alliance_id = alliance_id
        self.status = SagaStatus.ALLIANCE_CREATED
        self.complete_step(SagaStep.CREATE_ALLIANCE, {"alliance_id": alliance_id})

    def complete_saga(self) -> None:
        """Mark saga as completed"""
        self.status = SagaStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.complete_step(SagaStep.COMPLETE_SAGA)
        self.current_step = None

    def fail_saga(self, error: str, failed_step: SagaStep) -> None:
        """Mark saga as failed"""
        self.status = SagaStatus.FAILED
        self.error = error
        self.completed_at = datetime.utcnow()
        self.fail_step(failed_step, error)
        self.current_step = None

    def start_compensation(self, actions: List[str]) -> None:
        """Start compensation process"""
        self.status = SagaStatus.COMPENSATING
        self.compensation_actions = actions
        self.updated_at = datetime.utcnow()

    def complete_compensation(self) -> None:
        """Complete compensation process"""
        self.status = SagaStatus.COMPENSATED
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def get_next_step(self) -> Optional[SagaStep]:
        """Get the next step to execute"""
        if self.status == SagaStatus.FAILED or self.status == SagaStatus.COMPLETED:
            return None
            
        if self.current_step == SagaStep.CREATE_PARTNER and self.steps[SagaStep.CREATE_PARTNER].status == "completed":
            return SagaStep.CREATE_ALLIANCE
        elif self.current_step == SagaStep.CREATE_ALLIANCE and self.steps[SagaStep.CREATE_ALLIANCE].status == "completed":
            return SagaStep.COMPLETE_SAGA
        
        return self.current_step

    def is_completed(self) -> bool:
        """Check if saga is completed"""
        return self.status == SagaStatus.COMPLETED

    def is_failed(self) -> bool:
        """Check if saga has failed"""
        return self.status == SagaStatus.FAILED

    def needs_compensation(self) -> bool:
        """Check if saga needs compensation"""
        return self.status == SagaStatus.FAILED and any(
            step.status == "completed" for step in self.steps.values()
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert saga state to dictionary"""
        return {
            "saga_id": self.saga_id,
            "correlation_id": self.correlation_id,
            "status": self.status.value,
            "current_step": self.current_step.value if self.current_step else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "partner_data": self.partner_data,
            "partner_id": self.partner_id,
            "alliance_id": self.alliance_id,
            "error": self.error,
            "compensation_actions": self.compensation_actions,
            "steps": {
                step.value: {
                    "status": execution.status,
                    "started_at": execution.started_at.isoformat() if execution.started_at else None,
                    "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                    "error": execution.error,
                    "result": execution.result
                }
                for step, execution in self.steps.items()
            }
        }
