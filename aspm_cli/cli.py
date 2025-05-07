import argparse
import os
from .utils import ConfigValidator, ALLOWED_SCAN_TYPES
from .scan import IaCScanner

def clean_env_vars():
    """Removes surrounding single or double quotes from all environment variables."""
    for key, value in os.environ.items():
        if value and ((value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"'))):
            os.environ[key] = value[1:-1]

def main():
    clean_env_vars()
    parser = argparse.ArgumentParser(prog="aspm-cli", description="ASPM CLI Tool")
    subparsers = parser.add_subparsers(dest="command")

    env_parser = subparsers.add_parser("env", help="Validate and print config from environment")
    env_parser.set_defaults(func=print_env)

    scan_parser = subparsers.add_parser("scan", help=f"Run a scan (e.g. {', '.join(ALLOWED_SCAN_TYPES)})")
    scan_subparsers = scan_parser.add_subparsers(dest="scantype")

    # IAC Scan Subcommand
    iac_parser = scan_subparsers.add_parser("iac", help="Run IAC scan")
    iac_parser.add_argument("--file", default="", help="Specify a file for scanning; cannot be used with directory input")
    iac_parser.add_argument("--directory", default="./", help="Directory with infrastructure code and/or package manager files to scan")
    iac_parser.add_argument("--compact", action="store_true", help="Do not display code blocks in output")
    iac_parser.add_argument("--quiet", action="store_true", help="Display only failed checks")
    iac_parser.add_argument("--framework", default="all", help="Filter scans by specific frameworks, e.g., --framework terraform,sca_package. For all frameworks, use --framework all")
    iac_parser.add_argument("--repo-url", help="GitHub repository URL")
    iac_parser.add_argument("--repo-branch", help="GitHub repository branch")
    iac_parser.set_defaults(func=run_scan)

    # Parse arguments and execute respective function
    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

def print_env():
    try:
        print(f"ACCUKNOX_ENDPOINT={os.getenv('ACCUKNOX_ENDPOINT')}")
        print(f"ACCUKNOX_TENANT={os.getenv('ACCUKNOX_TENANT')}")
        print(f"ACCUKNOX_LABEL={os.getenv('ACCUKNOX_LABEL')}")
    except Exception as e:
        print(e)

def run_scan(args):
    try:
        # Determine the scan type from subcommand
        if args.scantype:
            input_soft_fail = True
            ConfigValidatorObj = ConfigValidator(args.scantype.lower(), os.getenv("ACCUKNOX_ENDPOINT"), os.getenv("ACCUKNOX_TENANT"), os.getenv("ACCUKNOX_LABEL"), os.getenv("ACCUKNOX_TOKEN"), input_soft_fail)
            print(f"✅ Running {args.scantype.lower()} scan...")

            if args.scantype.lower() == "iac":
                ConfigValidatorObj.validate_iac_scan(args.repo_url, args.repo_branch, args.file, args.directory, args.compact, args.quiet, args.framework)
                IaCScannerObj = IaCScanner(args.repo_url, args.repo_branch, args.file, args.directory, args.compact, args.quiet, args.framework)
                exit_code, result_file = IaCScannerObj.run()
                pass 
        else:
            print("❌ Invalid scan type.")
    except Exception as e:
        print("❌ Scan failed:")
        print(e)
