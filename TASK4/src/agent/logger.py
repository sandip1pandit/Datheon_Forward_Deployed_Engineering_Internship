from datetime import datetime


execution_logs = []


def log_event(event_type: str, message: str):

    log_entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "event": event_type,
        "message": message
    }

    execution_logs.append(log_entry)

    print(
        f"[{log_entry['timestamp']}] "
        f"[{event_type.upper()}] {message}"
    )

    return log_entry


def get_execution_logs():
    return execution_logs


def clear_execution_logs():
    execution_logs.clear()