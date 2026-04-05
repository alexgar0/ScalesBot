import logging
from typing import Optional

import logfire
from rich.console import Console
from rich.logging import RichHandler

def setup_logging(console: Optional[Console] = None) -> None:
    log_console = console or Console()
    rich_handler = RichHandler(
        console=log_console,
        show_time=True,
        show_path=False,
        markup=True,
        rich_tracebacks=True
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s", 
        handlers=[rich_handler],
        force=True
    )
    
    logfire.configure(send_to_logfire="if-token-present")
    logfire.instrument_pydantic_ai()