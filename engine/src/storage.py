from abc import ABC, abstractmethod
from typing import Optional

from .models import ClassifiedAgent, Violation


class StorageBackend(ABC):
    @abstractmethod
    def initialize(self) -> None:
        ...

    @abstractmethod
    def upsert_agent(self, agent: ClassifiedAgent) -> None:
        ...

    @abstractmethod
    def remove_agent(self, container_id: str) -> None:
        ...

    @abstractmethod
    def get_agent(self, container_id: str) -> Optional[dict]:
        ...

    @abstractmethod
    def list_agents(self, status: Optional[str] = None) -> list[dict]:
        ...

    @abstractmethod
    def log_violation(self, violation: Violation) -> None:
        ...

    @abstractmethod
    def get_violations(
        self,
        violation_type: Optional[str] = None,
        severity: Optional[str] = None,
        container_id: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict]:
        ...

    @abstractmethod
    def log_alert(self, alert: dict) -> None:
        ...

    @abstractmethod
    def get_alert_history(
        self,
        level: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict]:
        ...
