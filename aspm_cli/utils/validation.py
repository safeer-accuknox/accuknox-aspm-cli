from pydantic import BaseModel, ValidationError, Field, field_validator, root_validator
import os
from typing import Optional
from aspm_cli.utils.logger import Logger


ALLOWED_SCAN_TYPES = {"iac", "sast", "sq-sast"}

class Config(BaseModel):
    SCAN_TYPE: str
    ACCUKNOX_ENDPOINT: str
    ACCUKNOX_TENANT: int
    ACCUKNOX_LABEL: str
    ACCUKNOX_TOKEN: str
    SOFT_FAIL: bool

    @field_validator("SCAN_TYPE")
    @classmethod
    def validate_scan_type(cls, v):
        if v not in ALLOWED_SCAN_TYPES:
            raise ValueError(f"Invalid SCAN_TYPE. Allowed values: {', '.join(ALLOWED_SCAN_TYPES)}.")
        return v

class IaCScannerConfig(BaseModel):
    REPOSITORY_URL: str
    REPOSITORY_BRANCH: str
    FILE: str
    DIRECTORY: str 
    COMPACT: bool
    QUIET: bool
    FRAMEWORK: Optional[str]

    @field_validator("REPOSITORY_URL", mode="before")
    @classmethod
    def validate_repository_url(cls, v):
        if not v:
            raise ValueError("Unable to retrieve REPOSITORY_URL from Git metadata. Please pass the --repo-url variable.")
        if not isinstance(v, str) or not v.startswith("http"):
            raise ValueError("Invalid REPOSITORY_URL. It must be a valid URL starting with 'http'.")
        return v

    @field_validator("REPOSITORY_BRANCH", mode="before")
    @classmethod
    def validate_repository_branch(cls, v):
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Unable to retrieve REPOSITORY_BRANCH from Git metadata. Please pass the --repo-branch variable")
        return v

class SASTScannerConfig(BaseModel):
    REPOSITORY_URL: str
    COMMIT_REF: str
    COMMIT_SHA: str
    PIPELINE_ID: Optional[str] 
    JOB_URL: Optional[str]

    @field_validator("REPOSITORY_URL", mode="before")
    @classmethod
    def validate_repository_url(cls, v):
        if not v:
            raise ValueError("Unable to retrieve REPOSITORY_URL from Git metadata. Please pass the --repo-url variable.")
        if not isinstance(v, str) or not v.startswith("http"):
            raise ValueError("Invalid REPOSITORY_URL. It must be a valid URL starting with 'http'.")
        return v

    @field_validator("COMMIT_REF", mode="before")
    @classmethod
    def validate_commit_ref(cls, v):
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Unable to retrieve COMMIT_REF from Git metadata. Please pass the --commit-ref variable")
        return v
    
    @field_validator("COMMIT_SHA", mode="before")
    @classmethod
    def validate_commit_sha(cls, v):
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Unable to retrieve COMMIT_SHA from Git metadata. Please pass the --commit-sha variable")
        return v
    
class SQSASTScannerConfig(BaseModel):
    SONAR_PROJECT_KEY: str
    SONAR_TOKEN: str
    SONAR_HOST_URL: str
    SONAR_ORG_ID: Optional[str] 
    REPOSITORY_URL: str
    BRANCH: str
    COMMIT_SHA: str
    PIPELINE_URL: Optional[str] 

    @field_validator("REPOSITORY_URL", mode="before")
    @classmethod
    def validate_repository_url(cls, v):
        if not v:
            raise ValueError("Unable to retrieve REPOSITORY_URL from Git metadata. Please pass the --repo-url variable.")
        if not isinstance(v, str) or not v.startswith("http"):
            raise ValueError("Invalid REPOSITORY_URL. It must be a valid URL starting with 'http'.")
        return v

    @field_validator("BRANCH", mode="before")
    @classmethod
    def validate_commit_ref(cls, v):
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Unable to retrieve BRANCH from Git metadata. Please pass the --branch variable")
        return v
    
    @field_validator("COMMIT_SHA", mode="before")
    @classmethod
    def validate_commit_sha(cls, v):
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Unable to retrieve COMMIT_SHA from Git metadata. Please pass the --commit-sha variable")
        return v

class ConfigValidator:
    def __init__(self, scan_type, accuknox_endpoint, accuknox_tenant, accuknox_label, accuknox_token, softfail):
        try:
            self.config = Config(
                SCAN_TYPE=scan_type,
                ACCUKNOX_ENDPOINT=accuknox_endpoint,
                ACCUKNOX_TENANT=accuknox_tenant,
                ACCUKNOX_LABEL=accuknox_label,
                ACCUKNOX_TOKEN=accuknox_token,
                SOFT_FAIL=softfail
            )
        except ValidationError as e:
            for error in e.errors():
                Logger.get_logger().error(f"{error['loc'][0]}: {error['msg']}")
            exit(1)

    def validate_sast_scan(self, repo_url, commit_ref, commit_sha, pipeline_id, job_url):
        try:
            self.config = SASTScannerConfig(
                REPOSITORY_URL=repo_url,
                COMMIT_REF=commit_ref,
                COMMIT_SHA=commit_sha,
                PIPELINE_ID=pipeline_id,
                JOB_URL=job_url
            )
        except ValidationError as e:
            for error in e.errors():
                Logger.get_logger().error(f"{error['loc'][0]}: {error['msg']}")
            exit(1)


    def validate_sq_sast_scan(self, sonar_project_key,  sonar_token, sonar_host_url, sonar_org_id, repo_url, branch, commit_sha, pipeline_url):
        try:
            self.config = SQSASTScannerConfig(
                SONAR_PROJECT_KEY=sonar_project_key,
                SONAR_TOKEN=sonar_token,
                SONAR_HOST_URL=sonar_host_url,
                SONAR_ORG_ID = sonar_org_id, 
                REPOSITORY_URL=repo_url,
                BRANCH=branch,
                COMMIT_SHA=commit_sha,
                PIPELINE_URL=pipeline_url,
            )
        except ValidationError as e:
            for error in e.errors():
                Logger.get_logger().error(f"{error['loc'][0]}: {error['msg']}")
            exit(1)