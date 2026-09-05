import sys
import argparse
import logging
from sponsor_engine.utils.logging import setup_logger
from sponsor_engine.scheduler.daily_job import DailySponsorshipJob

logger = setup_logger("main")

def run_daily_cmd():
    """Runs daily lead discovery job automatically."""
    print("\n🚀 Launching News NIT IIT 100% Automated Lead & DM Engine...\n")
    job = DailySponsorshipJob()
    result = job.run_daily_pipeline()

    print(result["report_text"])
    print("\n✅ Daily job and automated DM dispatch completed successfully!")

def run_web_cmd():
    """Launches local Flask web CRM server."""
    from api.index import app
    print("\n🌐 Starting News NIT IIT Sponsorship Flask CRM Web Server...\n")
    app.run(host="0.0.0.0", port=5000, debug=True)

def main():
    parser = argparse.ArgumentParser(
        description="News NIT IIT - 100% Automated Lead Discovery & DM Engine"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    subparsers.add_parser("run-daily", help="Run daily automated lead discovery & DM dispatch")
    subparsers.add_parser("web", help="Launch local Flask web CRM server")

    args = parser.parse_args()

    if args.command == "run-daily" or args.command is None:
        run_daily_cmd()
    elif args.command == "web":
        run_web_cmd()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
