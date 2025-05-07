import argparse
import os
from colorama import Fore, Back, Style, init
init(autoreset=True)
from .utils import ConfigValidator, ALLOWED_SCAN_TYPES, upload_results, handle_failure
from .scan import IaCScanner
from .utils.spinner import Spinner

from .utils.logger import Logger


def clean_env_vars():
    """Removes surrounding single or double quotes from all environment variables."""
    for key, value in os.environ.items():
        if value and ((value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"'))):
            os.environ[key] = value[1:-1]

def print_banner():
    banner = r"""
    ╔═╗┌─┐┌─┐┬ ┬╦╔═┌┐┌┌─┐─┐ ┬  ╔═╗╔═╗╔═╗╔╦╗  ╔═╗┌─┐┌─┐┌┐┌┌┐┌┌─┐┬─┐
    ╠═╣│  │  │ │╠╩╗││││ │┌┴┬┘  ╠═╣╚═╗╠═╝║║║  ╚═╗│  ├─┤││││││├┤ ├┬┘
    ╩ ╩└─┘└─┘└─┘╩ ╩┘└┘└─┘┴ └─  ╩ ╩╚═╝╩  ╩ ╩  ╚═╝└─┘┴ ┴┘└┘┘└┘└─┘┴└─
    """
    print(Fore.BLUE + banner)

def main():
    clean_env_vars()
    print_banner()
    parser = argparse.ArgumentParser(prog="aspm-cli", description="ASPM CLI Tool")
    subparsers = parser.add_subparsers(dest="command")

    parser.add_argument('--softfail', action='store_true', help='Enable soft fail mode for scanning')

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

def print_env(args):
    try:
        Logger.get_logger().info(f"ACCUKNOX_ENDPOINT={os.getenv('ACCUKNOX_ENDPOINT')}")
        Logger.get_logger().info(f"ACCUKNOX_TENANT={os.getenv('ACCUKNOX_TENANT')}")
        Logger.get_logger().info(f"ACCUKNOX_LABEL={os.getenv('ACCUKNOX_LABEL')}")
    except Exception as e:
        Logger.get_logger().error(e)

def run_scan(args):
    try:
        # Determine the scan type from subcommand
        if args.scantype:
            softfail = args.softfail
            accuknox_endpoint = os.getenv("ACCUKNOX_ENDPOINT")
            accuknox_tenant = os.getenv("ACCUKNOX_TENANT")
            accuknox_label = os.getenv("ACCUKNOX_LABEL")
            accuknox_token = os.getenv("ACCUKNOX_TOKEN")
            ConfigValidatorObj = ConfigValidator(args.scantype.lower(), accuknox_endpoint, accuknox_tenant, accuknox_label, accuknox_token, softfail)


            if args.scantype.lower() == "iac":
                spinner = Spinner(message=f"Running {args.scantype.lower()} scan...",  color=Fore.GREEN)
                spinner.start()
                ConfigValidatorObj.validate_iac_scan(args.repo_url, args.repo_branch, args.file, args.directory, args.compact, args.quiet, args.framework)
                IaCScannerObj = IaCScanner(args.repo_url, args.repo_branch, args.file, args.directory, args.compact, args.quiet, args.framework)
                exit_code, result_file = IaCScannerObj.run()
                spinner.stop()
    
                if(result_file):
                    upload_results(result_file, accuknox_endpoint, accuknox_tenant, accuknox_label, accuknox_token, "IAC")
                handle_failure(exit_code, softfail)
                pass
        else:
            Logger.get_logger().error("Invalid scan type.")
    except Exception as e:
        Logger.get_logger().error("Scan failed.")
        Logger.get_logger().error(e)
