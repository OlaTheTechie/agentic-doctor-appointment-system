#!/usr/bin/env python3
"""
test script for logging system
verifies that all logging components work correctly
"""

import time
from src.utils.logger import (
    get_logger, 
    log_api_request, 
    log_memory_action, 
    log_agent_activity, 
    log_error
)

def test_logging_system():
    """test all logging components"""
    print("testing logging system...")
    print("=" * 50)
    
    # test basic loggers
    print("\n1. testing basic loggers...")
    
    app_logger = get_logger("app")
    api_logger = get_logger("api")
    memory_logger = get_logger("memory")
    agent_logger = get_logger("agents")
    error_logger = get_logger("errors")
    
    app_logger.info("application logger test")
    api_logger.info("api logger test")
    memory_logger.info("memory logger test")
    agent_logger.info("agent logger test")
    error_logger.error("error logger test")
    
    # test structured logging functions
    print("\n2. testing structured logging...")
    
    # test api request logging
    log_api_request(
        method="POST",
        endpoint="/api/v1/chat/sessions",
        patient_id=12345678,
        status_code=200,
        duration=0.123
    )
    
    # test memory action logging
    log_memory_action(
        action="session_created",
        session_id="chat_12345678_1234567890_abcd1234",
        patient_id=12345678,
        message_count=0,
        context_used=False
    )
    
    # test agent activity logging
    log_agent_activity(
        agent_name="AvailabilityAgent",
        intent="check_availability",
        patient_id=12345678,
        success=True
    )
    
    # test error logging
    try:
        raise ValueError("test error for logging")
    except Exception as e:
        log_error(
            component="test_logging",
            error=e,
            context={"test_data": "example"}
        )
    
    print("\n3. testing log levels...")
    
    logger = get_logger("app")
    logger.debug("debug message - should appear if debug enabled")
    logger.info("info message - should always appear")
    logger.warning("warning message - should appear in yellow")
    logger.error("error message - should appear in red")
    
    print("\n" + "=" * 50)
    print("logging test completed!")
    print("\ncheck the following log files:")
    print("- logs/app.log")
    print("- logs/api.log") 
    print("- logs/memory.log")
    print("- logs/agents.log")
    print("- logs/errors.log")
    
    # verify log files exist
    import os
    log_files = [
        "logs/app.log",
        "logs/api.log",
        "logs/memory.log", 
        "logs/agents.log",
        "logs/errors.log"
    ]
    
    print("\nlog file status:")
    for log_file in log_files:
        if os.path.exists(log_file):
            size = os.path.getsize(log_file)
            print(f"✓ {log_file} ({size} bytes)")
        else:
            print(f"✗ {log_file} (missing)")

if __name__ == "__main__":
    test_logging_system()