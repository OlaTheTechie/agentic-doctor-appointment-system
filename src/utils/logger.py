"""
centralized logging configuration for the appointment system
provides structured logging with different levels and formats
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..config.settings import settings


class ColoredFormatter(logging.Formatter):
    """colored formatter for console output"""
    
    # color codes
    COLORS = {
        'DEBUG': '\033[36m',    # cyan
        'INFO': '\033[32m',     # green
        'WARNING': '\033[33m',  # yellow
        'ERROR': '\033[31m',    # red
        'CRITICAL': '\033[35m', # magenta
        'RESET': '\033[0m'      # reset
    }
    
    def format(self, record):
        # add color to level name
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


class AppLogger:
    """centralized logger for the appointment system"""
    
    def __init__(self):
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        self._setup_loggers()
    
    def _setup_loggers(self):
        """setup different loggers for different components"""
        
        # main application logger
        self.app_logger = self._create_logger(
            "app",
            "logs/app.log",
            level=settings.logging.level
        )
        
        # api request logger
        self.api_logger = self._create_logger(
            "api",
            "logs/api.log",
            level="INFO"
        )
        
        # memory chat logger
        self.memory_logger = self._create_logger(
            "memory",
            "logs/memory.log",
            level="INFO"
        )
        
        # agent system logger
        self.agent_logger = self._create_logger(
            "agents",
            "logs/agents.log",
            level="INFO"
        )
        
        # error logger (all errors)
        self.error_logger = self._create_logger(
            "errors",
            "logs/errors.log",
            level="ERROR"
        )
    
    def _create_logger(self, name: str, log_file: str, level: str = "INFO") -> logging.Logger:
        """create a logger with file and console handlers"""
        
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))
        
        # clear existing handlers
        logger.handlers.clear()
        
        # file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        
        # console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        
        # formatters
        file_format = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s'
        )
        
        console_format = ColoredFormatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
        )
        
        file_handler.setFormatter(file_format)
        console_handler.setFormatter(console_format)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def get_logger(self, component: str) -> logging.Logger:
        """get logger for specific component"""
        loggers = {
            "app": self.app_logger,
            "api": self.api_logger,
            "memory": self.memory_logger,
            "agents": self.agent_logger,
            "errors": self.error_logger
        }
        
        return loggers.get(component, self.app_logger)


# global logger instance
app_logger = AppLogger()


def get_logger(component: str = "app") -> logging.Logger:
    """get logger for component"""
    return app_logger.get_logger(component)


# convenience functions
def log_api_request(method: str, endpoint: str, patient_id: Optional[int] = None, 
                   status_code: Optional[int] = None, duration: Optional[float] = None):
    """log api request with structured data"""
    logger = get_logger("api")
    
    log_data = {
        "method": method,
        "endpoint": endpoint,
        "patient_id": patient_id,
        "status_code": status_code,
        "duration_ms": round(duration * 1000, 2) if duration else None
    }
    
    # filter out None values
    log_data = {k: v for k, v in log_data.items() if v is not None}
    
    if status_code and status_code >= 400:
        logger.error(f"API Request Failed: {log_data}")
    else:
        logger.info(f"API Request: {log_data}")


def log_memory_action(action: str, session_id: str, patient_id: int, 
                     message_count: Optional[int] = None, context_used: bool = False):
    """log memory chat actions"""
    logger = get_logger("memory")
    
    log_data = {
        "action": action,
        "session_id": session_id[:12] + "...",  # truncate for privacy
        "patient_id": patient_id,
        "message_count": message_count,
        "context_used": context_used
    }
    
    logger.info(f"Memory Action: {log_data}")


def log_agent_activity(agent_name: str, intent: str, patient_id: int, 
                      success: bool = True, error: Optional[str] = None):
    """log agent system activity"""
    logger = get_logger("agents")
    
    log_data = {
        "agent": agent_name,
        "intent": intent,
        "patient_id": patient_id,
        "success": success
    }
    
    if success:
        logger.info(f"Agent Success: {log_data}")
    else:
        log_data["error"] = error
        logger.error(f"Agent Error: {log_data}")


def log_error(component: str, error: Exception, context: Optional[dict] = None):
    """log errors with context"""
    logger = get_logger("errors")
    
    log_data = {
        "component": component,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {}
    }
    
    logger.error(f"System Error: {log_data}", exc_info=True)