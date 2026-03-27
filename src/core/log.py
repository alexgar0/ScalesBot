import logfire

def setup_logging():
    logfire.configure(send_to_logfire='if-token-present')
    logfire.instrument_pydantic_ai()
