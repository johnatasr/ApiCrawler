import re
from typing import Union, Dict, Optional
from datetime import datetime
import uuid
from enum import Enum
from app import redis_client
import json


class ScraperStatus(Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Job:
    def __init__(self, client_cpf: Union[str, None] = None):
        """
        Post-initialization method that gets executed after the dataclass is initialized.
        This method sanitizes the phone numbers and retrieves the URL for the website's logo.
        """
        if client_cpf:
            self.job_id = str(uuid.uuid4())
            self.state: str = ScraperStatus.RUNNING.value
            self.created_at: str = str(datetime.now())
            self.client_benefit_number = None
            self.updated_at = None

        self.client_cpf = re.sub(r'[-.\s]', '', client_cpf)

    def as_a_dict(self) -> Dict:
        """
        Returns the dataclass as a dictionary.
        Returns:
            Dict: The dataclass as a dictionary.
        """
        return self.__dict__

    def create(self) -> bool:
        return self if redis_client.set(self.job_id, json.dumps(self.as_a_dict())) else False

    @classmethod
    def get_by_id(cls, job_id: str):
        return redis_client.get(job_id)

    @classmethod
    def delete_by_id(cls, job_id: str):
        redis_client.delete([job_id])

    @classmethod
    def exists(cls, job_id: str):
        return redis_client.exists(job_id)

    @classmethod
    def update_by_id(cls, job_id: str, state: str, client_benefit_number: Optional[str] = None):
        job = redis_client.get(job_id)
        job = json.loads(job)
        job.state = state
        if client_benefit_number:
            job.client_benefit_number = client_benefit_number
        job.date_end = datetime.now()
        redis_client.set(job_id, job)
