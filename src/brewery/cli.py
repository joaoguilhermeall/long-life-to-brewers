import argparse
import asyncio
import logging
from typing import Literal, get_args

from brewery.common import BreweryConfig
from brewery.pipeline import BreweryPipeline

BreweryCliActionType = Literal["bronze", "silver", "gold", "pipeline"]

parser = argparse.ArgumentParser(description="Brewery CLI")


parser.add_argument(choices=get_args(BreweryCliActionType), dest="action", type=str, help="Action to perform")


def _configure_logging(confg: BreweryConfig) -> None:
    """Configure logging for the application."""

    logging.basicConfig(
        level=confg.log_level,
        format=confg.log_format,
        handlers=[
            logging.FileHandler(confg.log_file),
            logging.StreamHandler(),
        ],
    )


def main():
    """Main entry point for the application."""
    config = BreweryConfig()
    pipeline = BreweryPipeline()

    _configure_logging(config)

    args = parser.parse_args()

    logging.info(f"Starting Brewery CLI with action: {args.action}")

    if args.action == "bronze":
        asyncio.run(pipeline.bronze())
    elif args.action == "silver":
        pipeline.silver()
    elif args.action == "gold":
        pipeline.gold()
    elif args.action == "pipeline":
        asyncio.run(pipeline.run())
