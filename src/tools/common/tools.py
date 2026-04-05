from datetime import datetime


from tools._internal.registry import tool


@tool(plain=True)
def get_local_time() -> str:
    """
    Gets the local time.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
