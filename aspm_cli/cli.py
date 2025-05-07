import argparse
import os
from pydantic import BaseModel, ValidationError, field_validator
from typing import Literal

class Config(BaseModel):
    ACCUKNOX_ENDPOINT: str
    ACCUKNOX_TENANT: int
    ACCUKNOX_LABEL: str
    ACCUKNOX_TOKEN: str
    SCAN_TYPE: Literal["iac", "sast", "dast"]

def main():
    parser = argparse.ArgumentParser(prog="aspm-cli", description="ASPM CLI Tool")
    subparsers = parser.add_subparsers(dest="command")

    env_parser = subparsers.add_parser("env", help="Validate and print config from environment")
    env_parser.set_defaults(func=print_env)

    scan_parser = subparsers.add_parser("scan", help="Run a scan (e.g., IAC, SAST, DAST)")
    scan_parser.add_argument("--scantype", required=True, help="Type of scan (iac, sast, dast)")
    scan_parser.set_defaults(func=run_scan)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

def print_env(args):
    try:
        cfg = Config(
            SCAN_TYPE="iac",  # dummy default
            ACCUKNOX_ENDPOINT=os.getenv("ACCUKNOX_ENDPOINT"),
            ACCUKNOX_TENANT=os.getenv("ACCUKNOX_TENANT"),
            ACCUKNOX_LABEL=os.getenv("ACCUKNOX_LABEL"),
            ACCUKNOX_TOKEN=os.getenv("ACCUKNOX_TOKEN"),
        )
        for field, value in cfg.model_dump().items():
            print(f"{field}={value}")
    except ValidationError as e:
        print(e)

def run_scan(args):
    try:
        cfg = Config(
            SCAN_TYPE=args.scantype.lower(),
            ACCUKNOX_ENDPOINT=os.getenv("ACCUKNOX_ENDPOINT"),
            ACCUKNOX_TENANT=os.getenv("ACCUKNOX_TENANT"),
            ACCUKNOX_LABEL=os.getenv("ACCUKNOX_LABEL"),
            ACCUKNOX_TOKEN=os.getenv("ACCUKNOX_TOKEN"),
        )
        print(f"✅ Running {cfg.SCAN_TYPE.upper()} scan...")
        # here you can integrate scan logic
    except ValidationError as e:
        print("❌ Config validation failed:")
        print(e)
