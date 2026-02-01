"""Main entry point for the Adversarial Knowledge Cartographer."""

import logging
from config import config
from utils.logging_config import setup_logging, get_logger

# Configure structured logging
setup_logging(
    log_level=config.log_level,
    log_file="logs/cartographer.log"
)

logger = get_logger(__name__)


def main():
    """Main entry point for the application."""
    logger.info("Starting Adversarial Knowledge Cartographer")
    
    # Validate API keys
    try:
        config.validate_api_keys()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your .env file and ensure all required API keys are set")
        return
    
    logger.info(f"Using LLM provider: {config.llm_provider}")
    logger.info(f"Using search provider: {config.search_provider}")
    logger.info(f"Max iterations: {config.max_iterations}")
    logger.info(f"Min sources: {config.min_sources}")
    
    # Initialize workflow orchestrator
    from agents import WorkflowOrchestrator
    orchestrator = WorkflowOrchestrator(max_iterations=config.max_iterations)
    logger.info("Workflow orchestrator initialized successfully")


if __name__ == "__main__":
    main()
