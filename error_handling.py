#!/usr/bin/env python3
"""
Comprehensive Error Handling System for AI Swarm Platform
Provides robust error handling, recovery, and monitoring capabilities
"""

import asyncio
import logging
import logging.handlers
import time
import traceback
import json
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, Union
from enum import Enum
from dataclasses import dataclass, field
from collections import deque
from pathlib import Path
import hashlib

# Configuration
MAX_RETRIES = 3
RETRY_DELAYS = [1, 5, 15]  # seconds
CIRCUIT_BREAKER_THRESHOLD = 5
CIRCUIT_BREAKER_TIMEOUT = 60  # seconds
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX_REQUESTS = 100


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class ServiceLevel(Enum):
    """Service degradation levels"""
    FULL = "full"
    REDUCED = "reduced"
    MINIMAL = "minimal"
    EMERGENCY = "emergency"


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class ErrorContext:
    """Context information for errors"""
    component: str
    operation: str
    timestamp: datetime = field(default_factory=datetime.now)
    user_id: Optional[str] = None
    task_id: Optional[str] = None
    agent_id: Optional[str] = None
    additional_info: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None


@dataclass
class ErrorResponse:
    """Standardized error response"""
    code: int
    message: str
    action: str
    severity: ErrorSeverity
    context: Optional[ErrorContext] = None
    retry_after: Optional[int] = None


class SwarmException(Exception):
    """Base exception for swarm system"""
    def __init__(self, message: str, error_code: int = 500, severity: ErrorSeverity = ErrorSeverity.MEDIUM):
        self.message = message
        self.error_code = error_code
        self.severity = severity
        super().__init__(message)


class ValidationError(SwarmException):
    """Input validation error"""
    def __init__(self, errors: List[str]):
        message = f"Validation failed: {', '.join(errors)}"
        super().__init__(message, 400, ErrorSeverity.LOW)
        self.errors = errors


class AgentError(SwarmException):
    """Agent execution error"""
    def __init__(self, agent_id: str, message: str):
        super().__init__(f"Agent {agent_id}: {message}", 500, ErrorSeverity.HIGH)
        self.agent_id = agent_id


class CircuitOpenError(SwarmException):
    """Circuit breaker is open"""
    def __init__(self, service: str):
        super().__init__(f"Circuit breaker for {service} is open", 503, ErrorSeverity.HIGH)
        self.service = service


class RateLimitError(SwarmException):
    """Rate limit exceeded"""
    def __init__(self, user_id: str, retry_after: int):
        super().__init__(f"Rate limit exceeded for user {user_id}", 429, ErrorSeverity.LOW)
        self.user_id = user_id
        self.retry_after = retry_after


class CircuitBreaker:
    """Circuit breaker pattern implementation"""
    
    def __init__(self, name: str, failure_threshold: int = CIRCUIT_BREAKER_THRESHOLD, 
                 timeout: int = CIRCUIT_BREAKER_TIMEOUT):
        self.name = name
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self.success_count = 0
        self.half_open_successes_required = 3
        
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self.should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logging.info(f"Circuit breaker {self.name} entering HALF_OPEN state")
            else:
                raise CircuitOpenError(self.name)
        
        try:
            result = await func(*args, **kwargs)
            self.on_success()
            return result
        except Exception as e:
            self.on_failure()
            raise
    
    def should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return False
        return time.time() - self.last_failure_time >= self.timeout
    
    def on_success(self):
        """Handle successful execution"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.half_open_successes_required:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                logging.info(f"Circuit breaker {self.name} closed after successful recovery")
        elif self.state == CircuitState.CLOSED:
            self.failure_count = max(0, self.failure_count - 1)
    
    def on_failure(self):
        """Handle failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.success_count = 0
            logging.error(f"Circuit breaker {self.name} reopened after failure in HALF_OPEN state")
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logging.error(f"Circuit breaker {self.name} opened after {self.failure_count} failures")


class RetryStrategy:
    """Retry logic with exponential backoff"""
    
    def __init__(self, max_retries: int = MAX_RETRIES, delays: List[int] = None):
        self.max_retries = max_retries
        self.delays = delays or RETRY_DELAYS
        
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                result = await func(*args, **kwargs)
                if attempt > 0:
                    logging.info(f"Retry successful after {attempt + 1} attempts")
                return result
            except Exception as e:
                last_exception = e
                logging.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    delay = self.delays[min(attempt, len(self.delays) - 1)]
                    logging.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
        
        logging.error(f"All {self.max_retries} attempts failed")
        raise last_exception


class RequestValidator:
    """Input validation and sanitization"""
    
    # Regex patterns for common injections - more specific to avoid false positives
    SQL_INJECTION_PATTERN = re.compile(r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)\b.*\b(FROM|INTO|TABLE|WHERE)\b)", re.IGNORECASE)
    COMMAND_INJECTION_PATTERN = re.compile(r"[;&|`$()].*\b(rm|del|format|shutdown)\b", re.IGNORECASE)
    PATH_TRAVERSAL_PATTERN = re.compile(r"\.\.[/\\]")
    
    @staticmethod
    def validate_swarm_request(request: Dict[str, Any]) -> bool:
        """Validate swarm execution request"""
        errors = []
        
        # Check required fields
        if not request.get('task_description'):
            errors.append("task_description is required")
        
        # Validate task description
        task_desc = request.get('task_description', '')
        if len(task_desc) > 10000:
            errors.append("task_description exceeds maximum length")
        
        if RequestValidator.contains_injection(task_desc):
            errors.append("Potential injection detected in task_description")
        
        # Validate priority
        valid_priorities = ['low', 'medium', 'high', 'critical', None]
        if request.get('priority') not in valid_priorities:
            errors.append(f"Invalid priority. Must be one of: {valid_priorities}")
        
        # Validate context if provided
        if 'context' in request and not isinstance(request['context'], dict):
            errors.append("context must be a dictionary")
        
        if errors:
            raise ValidationError(errors)
        
        return True
    
    @staticmethod
    def contains_injection(text: str) -> bool:
        """Check for potential injection attacks"""
        if RequestValidator.SQL_INJECTION_PATTERN.search(text):
            return True
        if RequestValidator.COMMAND_INJECTION_PATTERN.search(text):
            return True
        if RequestValidator.PATH_TRAVERSAL_PATTERN.search(text):
            return True
        return False
    
    @staticmethod
    def sanitize_path(path: str) -> str:
        """Sanitize file paths"""
        # Remove path traversal attempts
        path = path.replace('..', '')
        # Convert to Path object and resolve
        try:
            safe_path = Path(path).resolve()
            return str(safe_path)
        except Exception:
            raise ValidationError([f"Invalid path: {path}"])
    
    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """Validate API key format"""
        if not api_key:
            raise ValidationError(["API key is required"])
        
        # Basic format validation (adjust based on actual API key format)
        if len(api_key) < 20:
            raise ValidationError(["Invalid API key format"])
        
        return True


class RateLimiter:
    """Rate limiting implementation"""
    
    def __init__(self, max_requests: int = RATE_LIMIT_MAX_REQUESTS, 
                 window_seconds: int = RATE_LIMIT_WINDOW):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # user_id -> deque of timestamps
        
    def check_limit(self, user_id: str) -> bool:
        """Check if user is within rate limit"""
        now = time.time()
        
        if user_id not in self.requests:
            self.requests[user_id] = deque()
        
        # Remove old requests outside the window
        while self.requests[user_id] and self.requests[user_id][0] < now - self.window_seconds:
            self.requests[user_id].popleft()
        
        # Check if limit exceeded
        if len(self.requests[user_id]) >= self.max_requests:
            retry_after = int(self.window_seconds - (now - self.requests[user_id][0]))
            raise RateLimitError(user_id, retry_after)
        
        # Add current request
        self.requests[user_id].append(now)
        return True
    
    def get_remaining_requests(self, user_id: str) -> int:
        """Get remaining requests for user"""
        if user_id not in self.requests:
            return self.max_requests
        return max(0, self.max_requests - len(self.requests[user_id]))


class SwarmLogger:
    """Comprehensive logging system"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.setup_loggers()
        
    def setup_loggers(self):
        """Setup different loggers for different components"""
        self.loggers = {
            'agent': self.create_logger('agent', logging.DEBUG),
            'mcp': self.create_logger('mcp', logging.INFO),
            'error': self.create_logger('error', logging.ERROR),
            'audit': self.create_logger('audit', logging.INFO),
            'performance': self.create_logger('performance', logging.INFO),
        }
    
    def create_logger(self, name: str, level: int) -> logging.Logger:
        """Create a logger with file and console handlers"""
        logger = logging.getLogger(f"swarm.{name}")
        logger.setLevel(level)
        
        # File handler
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / f"{name}.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)
        
        # Console handler for errors
        if level >= logging.ERROR:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter(
                '%(levelname)s: %(message)s'
            ))
            logger.addHandler(console_handler)
        
        return logger
    
    def log_error(self, context: ErrorContext, error: Exception):
        """Log error with context"""
        self.loggers['error'].error(
            f"[{context.component}] {context.operation} failed: {str(error)}",
            extra={
                'timestamp': context.timestamp.isoformat(),
                'user_id': context.user_id,
                'task_id': context.task_id,
                'agent_id': context.agent_id,
                'additional_info': json.dumps(context.additional_info),
                'stack_trace': context.stack_trace or traceback.format_exc()
            }
        )
    
    def log_audit(self, action: str, user_id: str, details: Dict[str, Any]):
        """Log audit trail"""
        self.loggers['audit'].info(
            f"AUDIT: {action}",
            extra={
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id,
                'details': json.dumps(details)
            }
        )
    
    def log_performance(self, operation: str, duration: float, success: bool):
        """Log performance metrics"""
        self.loggers['performance'].info(
            f"PERF: {operation}",
            extra={
                'timestamp': datetime.now().isoformat(),
                'operation': operation,
                'duration_ms': duration * 1000,
                'success': success
            }
        )


class GracefulDegradation:
    """Service degradation strategy"""
    
    def __init__(self):
        self.current_level = ServiceLevel.FULL
        self.error_threshold = {
            ServiceLevel.FULL: 10,
            ServiceLevel.REDUCED: 20,
            ServiceLevel.MINIMAL: 30,
        }
        self.error_count = 0
        self.last_reset = time.time()
        self.reset_interval = 300  # 5 minutes
        
    def check_degradation(self):
        """Check if service should be degraded"""
        # Reset counter if interval passed
        if time.time() - self.last_reset > self.reset_interval:
            self.error_count = max(0, self.error_count - 10)
            self.last_reset = time.time()
        
        # Check for degradation
        if self.current_level == ServiceLevel.FULL and self.error_count > self.error_threshold[ServiceLevel.FULL]:
            self.current_level = ServiceLevel.REDUCED
            logging.warning("Service degraded to REDUCED level")
        elif self.current_level == ServiceLevel.REDUCED and self.error_count > self.error_threshold[ServiceLevel.REDUCED]:
            self.current_level = ServiceLevel.MINIMAL
            logging.warning("Service degraded to MINIMAL level")
        elif self.current_level == ServiceLevel.MINIMAL and self.error_count > self.error_threshold[ServiceLevel.MINIMAL]:
            self.current_level = ServiceLevel.EMERGENCY
            logging.critical("Service degraded to EMERGENCY level")
    
    def record_error(self):
        """Record an error and check degradation"""
        self.error_count += 1
        self.check_degradation()
    
    def record_success(self):
        """Record success and potentially improve service level"""
        self.error_count = max(0, self.error_count - 1)
        
        # Check for service level improvement
        if self.current_level == ServiceLevel.EMERGENCY and self.error_count < self.error_threshold[ServiceLevel.MINIMAL]:
            self.current_level = ServiceLevel.MINIMAL
            logging.info("Service improved to MINIMAL level")
        elif self.current_level == ServiceLevel.MINIMAL and self.error_count < self.error_threshold[ServiceLevel.REDUCED]:
            self.current_level = ServiceLevel.REDUCED
            logging.info("Service improved to REDUCED level")
        elif self.current_level == ServiceLevel.REDUCED and self.error_count < self.error_threshold[ServiceLevel.FULL]:
            self.current_level = ServiceLevel.FULL
            logging.info("Service restored to FULL level")
    
    def get_available_features(self) -> Dict[str, bool]:
        """Get available features based on current service level"""
        features = {
            ServiceLevel.FULL: {
                'all_agents': True,
                'web_research': True,
                'parallel_execution': True,
                'advanced_analysis': True,
                'caching': True,
            },
            ServiceLevel.REDUCED: {
                'all_agents': False,  # Limited agents
                'web_research': True,
                'parallel_execution': False,  # Sequential only
                'advanced_analysis': False,
                'caching': True,
            },
            ServiceLevel.MINIMAL: {
                'all_agents': False,
                'web_research': False,
                'parallel_execution': False,
                'advanced_analysis': False,
                'caching': True,
            },
            ServiceLevel.EMERGENCY: {
                'all_agents': False,
                'web_research': False,
                'parallel_execution': False,
                'advanced_analysis': False,
                'caching': False,  # Direct execution only
            }
        }
        return features.get(self.current_level, features[ServiceLevel.EMERGENCY])


class ErrorHandler:
    """Central error handling coordinator"""
    
    def __init__(self):
        self.logger = SwarmLogger()
        self.rate_limiter = RateLimiter()
        self.degradation = GracefulDegradation()
        self.circuit_breakers = {}
        
    def get_circuit_breaker(self, name: str) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(name)
        return self.circuit_breakers[name]
    
    async def handle_with_recovery(self, func: Callable, context: ErrorContext, 
                                  fallback: Optional[Callable] = None) -> Any:
        """Execute function with full error handling and recovery"""
        retry_strategy = RetryStrategy()
        
        try:
            # Check rate limit
            if context.user_id:
                self.rate_limiter.check_limit(context.user_id)
            
            # Execute with retry
            result = await retry_strategy.execute(func)
            self.degradation.record_success()
            return result
            
        except Exception as e:
            self.degradation.record_error()
            context.stack_trace = traceback.format_exc()
            self.logger.log_error(context, e)
            
            # Try fallback if provided
            if fallback:
                try:
                    logging.info(f"Attempting fallback for {context.operation}")
                    return await fallback()
                except Exception as fallback_error:
                    logging.error(f"Fallback also failed: {str(fallback_error)}")
            
            # Return error response
            return self.create_error_response(e, context)
    
    def create_error_response(self, error: Exception, context: ErrorContext) -> ErrorResponse:
        """Create standardized error response"""
        if isinstance(error, SwarmException):
            return ErrorResponse(
                code=error.error_code,
                message=error.message,
                action=self.get_recovery_action(error),
                severity=error.severity,
                context=context,
                retry_after=getattr(error, 'retry_after', None)
            )
        else:
            return ErrorResponse(
                code=500,
                message="An unexpected error occurred",
                action="Please try again later or contact support",
                severity=ErrorSeverity.HIGH,
                context=context
            )
    
    def get_recovery_action(self, error: SwarmException) -> str:
        """Get recommended recovery action for error"""
        recovery_actions = {
            ValidationError: "Please check your input and try again",
            AgentError: "Task will be retried with a different agent",
            CircuitOpenError: "Service temporarily unavailable, please wait",
            RateLimitError: "Please wait before making more requests",
        }
        
        for error_type, action in recovery_actions.items():
            if isinstance(error, error_type):
                return action
        
        return "An error occurred, please try again"


# Singleton instance
error_handler = ErrorHandler()