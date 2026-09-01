import sys
import argparse
import logging
from sponsor_engine.utils.logging import setup_logger
from sponsor_engine.scheduler.daily_job import DailySponsorshipJob
from config.settings import get_settings

logger = setup_logger("main")

def run_daily_cmd():
    """Runs daily lead discovery job."""
    print("\n🚀 Launching News NIT IIT Daily Lead Discovery Engine...\n")
    job = DailySponsorshipJob()
    result = job.run_daily_pipeline()

    print(result["report_text"])
    print("\n✅ Daily job completed successfully!")

def run_dashboard_cmd():
    """Launches Streamlit dashboard UI."""
    import subprocess
    print("\n🌐 Starting News NIT IIT Sponsorship Streamlit Dashboard...\n")
    dashboard_path = get_settings().BASE_DIR / "dashboard" / "app.py"
    subprocess.run(["streamlit", "run", str(dashboard_path)])

def main():
    parser = argparse.ArgumentParser(
        description="News NIT IIT - AI Sponsorship Lead Generation & Outreach Automation CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # run-daily subcommand
    subparsers.add_parser("run-daily", help="Run 12-step daily lead discovery pipeline")

    # dashboard subcommand
    subparsers.add_parser("dashboard", help="Launch interactive Streamlit dashboard")

    # export-report subcommand
    subparsers.add_parser("export-report", help="Export latest top sponsor leads report")

    args = parser.parse_args()

    if args.command == "run-daily" or args.command is None:
        run_daily_cmd()
    elif args.command == "dashboard":
        run_dashboard_cmd()
    elif args.command == "export-report":
        run_daily_cmd()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
