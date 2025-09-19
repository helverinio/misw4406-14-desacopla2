from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class SagaEventType(Enum):
    """Types of saga events"""
    PARTNER_CREATION_STARTED = "partner_creation_started"
    PARTNER_CREATED = "partner_created"
    ALLIANCE_CREATION_STARTED = "alliance_creation_started"
    ALLIANCE_CREATED = "alliance_created"
    PARTNER_CREATION_FAILED = "partner_creation_failed"
    ALLIANCE_CREATION_FAILED = "alliance_creation_failed"
    SAGA_COMPLETED = "saga_completed"
    SAGA_FAILED = "saga_failed"
    COMPENSATION_STARTED = "compensation_started"
    COMPENSATION_COMPLETED = "compensation_completed"


@dataclass
class SagaEvent:
    """Base class for saga events"""
    event_id: str
    saga_id: str
    event_type: SagaEventType
    timestamp: datetime
    payload: Dict[str, Any]
    correlation_id: Optional[str] = None


@dataclass
class PartnerCreationStarted(SagaEvent):
    """Event when partner creation saga starts"""
    def __init__(self, saga_id: str, event_id: str, partner_data: Dict[str, Any], correlation_id: Optional[str] = None):
        super().__init__(
            event_id=event_id,
            saga_id=saga_id,
            event_type=SagaEventType.PARTNER_CREATION_STARTED,
            timestamp=datetime.utcnow(),
            payload={"partner_data": partner_data},
            correlation_id=correlation_id
        )


@dataclass
class PartnerCreated(SagaEvent):
    """Event when partner is successfully created"""
    def __init__(self, saga_id: str, event_id: str, partner_id: str, partner_data: Dict[str, Any], correlation_id: Optional[str] = None):
        super().__init__(
            event_id=event_id,
            saga_id=saga_id,
            event_type=SagaEventType.PARTNER_CREATED,
            timestamp=datetime.utcnow(),
            payload={"partner_id": partner_id, "partner_data": partner_data},
            correlation_id=correlation_id
        )


@dataclass
class AllianceCreationStarted(SagaEvent):
    """Event when alliance creation starts"""
    def __init__(self, saga_id: str, event_id: str, partner_id: str, correlation_id: Optional[str] = None):
        super().__init__(
            event_id=event_id,
            saga_id=saga_id,
            event_type=SagaEventType.ALLIANCE_CREATION_STARTED,
            timestamp=datetime.utcnow(),
            payload={"partner_id": partner_id},
            correlation_id=correlation_id
        )


@dataclass
class AllianceCreated(SagaEvent):
    """Event when alliance is successfully created"""
    def __init__(self, saga_id: str, event_id: str, partner_id: str, alliance_id: str, correlation_id: Optional[str] = None):
        super().__init__(
            event_id=event_id,
            saga_id=saga_id,
            event_type=SagaEventType.ALLIANCE_CREATED,
            timestamp=datetime.utcnow(),
            payload={"partner_id": partner_id, "alliance_id": alliance_id},
            correlation_id=correlation_id
        )


@dataclass
class PartnerCreationFailed(SagaEvent):
    """Event when partner creation fails"""
    def __init__(self, saga_id: str, event_id: str, error: str, partner_data: Dict[str, Any], correlation_id: Optional[str] = None):
        super().__init__(
            event_id=event_id,
            saga_id=saga_id,
            event_type=SagaEventType.PARTNER_CREATION_FAILED,
            timestamp=datetime.utcnow(),
            payload={"error": error, "partner_data": partner_data},
            correlation_id=correlation_id
        )


@dataclass
class AllianceCreationFailed(SagaEvent):
    """Event when alliance creation fails"""
    def __init__(self, saga_id: str, event_id: str, partner_id: str, error: str, correlation_id: Optional[str] = None):
        super().__init__(
            event_id=event_id,
            saga_id=saga_id,
            event_type=SagaEventType.ALLIANCE_CREATION_FAILED,
            timestamp=datetime.utcnow(),
            payload={"partner_id": partner_id, "error": error},
            correlation_id=correlation_id
        )


@dataclass
class SagaCompleted(SagaEvent):
    """Event when saga completes successfully"""
    def __init__(self, saga_id: str, event_id: str, partner_id: str, alliance_id: str, correlation_id: Optional[str] = None):
        super().__init__(
            event_id=event_id,
            saga_id=saga_id,
            event_type=SagaEventType.SAGA_COMPLETED,
            timestamp=datetime.utcnow(),
            payload={"partner_id": partner_id, "alliance_id": alliance_id},
            correlation_id=correlation_id
        )


@dataclass
class SagaFailed(SagaEvent):
    """Event when saga fails"""
    def __init__(self, saga_id: str, event_id: str, error: str, step_failed: str, correlation_id: Optional[str] = None):
        super().__init__(
            event_id=event_id,
            saga_id=saga_id,
            event_type=SagaEventType.SAGA_FAILED,
            timestamp=datetime.utcnow(),
            payload={"error": error, "step_failed": step_failed},
            correlation_id=correlation_id
        )


@dataclass
class CompensationStarted(SagaEvent):
    """Event when compensation starts"""
    def __init__(self, saga_id: str, event_id: str, compensation_actions: list, correlation_id: Optional[str] = None):
        super().__init__(
            event_id=event_id,
            saga_id=saga_id,
            event_type=SagaEventType.COMPENSATION_STARTED,
            timestamp=datetime.utcnow(),
            payload={"compensation_actions": compensation_actions},
            correlation_id=correlation_id
        )


@dataclass
class CompensationCompleted(SagaEvent):
    """Event when compensation completes"""
    def __init__(self, saga_id: str, event_id: str, compensation_results: Dict[str, Any], correlation_id: Optional[str] = None):
        super().__init__(
            event_id=event_id,
            saga_id=saga_id,
            event_type=SagaEventType.COMPENSATION_COMPLETED,
            timestamp=datetime.utcnow(),
            payload={"compensation_results": compensation_results},
            correlation_id=correlation_id
        )
