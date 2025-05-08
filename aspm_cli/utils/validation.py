from pydantic import BaseModel, ValidationError, Field, field_validator, root_validator
import os
from typing import Optional
from aspm_cli.utils.logger import Logger


ALLOWED_SCAN_TYPES = {"iac", "sast"}

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
    COMMIT_SHA: Optional[str]
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

class SecretScannerConfig(BaseModel):
    RESULTS: Optional[str]
    BRANCH: Optional[str]
    EXCLUDE_PATHS: Optional[str]
    ADDITIONAL_ARGUMENTS: Optional[str]

class CxcannerConfig(BaseModel):
    CX_PROJECT_NAME: Optional[str] = None  
    CX_BRANCH: Optional[str] = None  
    CX_SCAN_ID: Optional[str] = None  
    CX_CLIENT_ID: str
    CX_CLIENT_SECRET: str
    CX_BASE_URI: str
    CX_TENANT: str
    INPUT_DIRECTORY: str
    REPOSITORY_URL: str
    REPOSITORY_BRANCH: str
    REPOSITORY_COMMIT_SHA: str
    REPOSITORY_COMMIT_REF: str
        
    @field_validator("REPOSITORY_URL", "REPOSITORY_BRANCH", "REPOSITORY_COMMIT_SHA", "REPOSITORY_COMMIT_REF", mode="before")
    @classmethod
    def validate_required_fields(cls, v, field):
        if not isinstance(v, str) or not v.strip():
            raise ValueError(f"Unable to retrieve {field.field_name} from Git metadata, Please set the {field.field_name} environment variable")
        return v

    @field_validator("CX_BASE_URI")
    @classmethod
    def validate_base_uri(cls, v):
        if not v.startswith("http"):
            raise ValueError("CX_BASE_URI must be a valid URL starting with 'http'.")
        return v
    
    @root_validator(pre=True)
    def validate_exclusive_fields(cls, values):
        if values.get("CX_SCAN_ID") and (values.get("CX_PROJECT_NAME") or values.get("CX_BRANCH")):
            raise ValueError("CX_SCAN_ID cannot be used with CX_PROJECT_NAME or CX_BRANCH.")
        if not values.get("CX_SCAN_ID") and (not values.get("CX_PROJECT_NAME") or not values.get("CX_BRANCH")):
            raise ValueError("Either CX_SCAN_ID or both CX_PROJECT_NAME and CX_BRANCH must be provided.")
        return values


class ConfigValidator:
    def __init__(self, scan_type, accuknox_endpoint, accuknox_tenant, accuknox_label, accuknox_token, input_soft_fail):
        try:
            self.config = Config(
                SCAN_TYPE=scan_type,
                ACCUKNOX_ENDPOINT=accuknox_endpoint,
                ACCUKNOX_TENANT=accuknox_tenant,
                ACCUKNOX_LABEL=accuknox_label,
                ACCUKNOX_TOKEN=accuknox_token,
                SOFT_FAIL=input_soft_fail
            )
        except ValidationError as e:
            for error in e.errors():
                Logger.get_logger().error(f"{error['loc'][0]}: {error['msg']}")
            exit(1)

    def validate_iac_scan(self, repo_url, repo_branch, input_file, input_directory, input_compact, input_quiet, input_framework):
        try:
            self.config = IaCScannerConfig(
                REPOSITORY_URL=repo_url,
                REPOSITORY_BRANCH=repo_branch,
                FILE=input_file,
                DIRECTORY=input_directory,
                COMPACT=input_compact,
                QUIET=input_quiet,
                FRAMEWORK=input_framework
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


    def validate_secret_scan(self, results, branch, exclude_paths, additional_arguments):
        try:
            self.config = SecretScannerConfig(
                RESULTS=results,
                BRANCH=branch,
                EXCLUDE_PATHS=exclude_paths,
                ADDITIONAL_ARGUMENTS=additional_arguments,
            )
        except ValidationError as e:
            for error in e.errors():
                Logger.get_logger().error(f"{error['loc'][0]}: {error['msg']}")
            exit(1)

    def validate_cx_scan(self, scan_id, project_name, branch, client_id, client_secret, base_uri, tenant, source_dir, repo_url, repo_branch, repo_commit_sha, repo_commit_ref):
        try:
            self.config = CxcannerConfig(
                CX_SCAN_ID=scan_id,
                CX_PROJECT_NAME=project_name,
                CX_BRANCH=branch,
                CX_CLIENT_ID=client_id,
                CX_CLIENT_SECRET=client_secret,
                CX_BASE_URI=base_uri,
                CX_TENANT=tenant,
                INPUT_DIRECTORY=source_dir,
                REPOSITORY_URL=repo_url,
                REPOSITORY_BRANCH=repo_branch,
                REPOSITORY_COMMIT_SHA=repo_commit_sha,
                REPOSITORY_COMMIT_REF=repo_commit_ref,
            )
        except ValidationError as e:
            errors = e.errors()
            for error in errors:
                location = " -> ".join(str(loc) for loc in error.get("loc", []))
                Logger.get_logger().error(f"{location if location else 'Validation Error'}: {error['msg']}")
            exit(1)