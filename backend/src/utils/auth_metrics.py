from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
import time
import threading


class AuthMetricType(Enum):
    """
    Types of authentication metrics
    """
    LOGIN_ATTEMPTS = "login_attempts"
    LOGIN_SUCCESS_RATE = "login_success_rate"
    TOKEN_VALIDATIONS = "token_validations"
    FAILED_AUTH_ATTEMPTS = "failed_auth_attempts"
    ACTIVE_SESSIONS = "active_sessions"
    PERMISSION_DENIED = "permission_denied"


class AuthMetricsCollector:
    """
    Utility class for collecting and monitoring authentication metrics
    """

    def __init__(self):
        self.metrics = {}
        self.lock = threading.Lock()
        self.init_default_metrics()

    def init_default_metrics(self):
        """
        Initialize default authentication metrics
        """
        with self.lock:
            self.metrics = {
                AuthMetricType.LOGIN_ATTEMPTS.value: {
                    "count": 0,
                    "timestamp": datetime.utcnow().isoformat()
                },
                AuthMetricType.LOGIN_SUCCESS_RATE.value: {
                    "success_count": 0,
                    "failure_count": 0,
                    "rate": 0.0,
                    "timestamp": datetime.utcnow().isoformat()
                },
                AuthMetricType.TOKEN_VALIDATIONS.value: {
                    "count": 0,
                    "timestamp": datetime.utcnow().isoformat()
                },
                AuthMetricType.FAILED_AUTH_ATTEMPTS.value: {
                    "count": 0,
                    "timestamp": datetime.utcnow().isoformat()
                },
                AuthMetricType.ACTIVE_SESSIONS.value: {
                    "count": 0,
                    "timestamp": datetime.utcnow().isoformat()
                },
                AuthMetricType.PERMISSION_DENIED.value: {
                    "count": 0,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }

    def increment_metric(self, metric_type: AuthMetricType, increment_by: int = 1):
        """
        Increment a specific authentication metric

        Args:
            metric_type: Type of metric to increment
            increment_by: Amount to increment by (default: 1)
        """
        with self.lock:
            if metric_type.value in self.metrics:
                if metric_type == AuthMetricType.LOGIN_SUCCESS_RATE:
                    # For success rate, we track both success and failure separately
                    pass  # This would be handled by update_login_success_rate
                else:
                    self.metrics[metric_type.value]["count"] += increment_by
                    self.metrics[metric_type.value]["timestamp"] = datetime.utcnow().isoformat()

    def update_login_success_rate(self, success: bool):
        """
        Update login success/failure counts for calculating success rate

        Args:
            success: Whether the login attempt was successful
        """
        with self.lock:
            if success:
                self.metrics[AuthMetricType.LOGIN_SUCCESS_RATE.value]["success_count"] += 1
            else:
                self.metrics[AuthMetricType.LOGIN_SUCCESS_RATE.value]["failure_count"] += 1

            # Recalculate success rate
            total = (self.metrics[AuthMetricType.LOGIN_SUCCESS_RATE.value]["success_count"] +
                     self.metrics[AuthMetricType.LOGIN_SUCCESS_RATE.value]["failure_count"])
            if total > 0:
                rate = (self.metrics[AuthMetricType.LOGIN_SUCCESS_RATE.value]["success_count"] / total) * 100
                self.metrics[AuthMetricType.LOGIN_SUCCESS_RATE.value]["rate"] = rate
            else:
                self.metrics[AuthMetricType.LOGIN_SUCCESS_RATE.value]["rate"] = 0.0

            self.metrics[AuthMetricType.LOGIN_SUCCESS_RATE.value]["timestamp"] = datetime.utcnow().isoformat()

    def get_metric(self, metric_type: AuthMetricType) -> Dict[str, Any]:
        """
        Get the current value of a specific metric

        Args:
            metric_type: Type of metric to retrieve

        Returns:
            Dictionary containing metric data
        """
        with self.lock:
            return self.metrics.get(metric_type.value, {})

    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all authentication metrics

        Returns:
            Dictionary containing all metrics
        """
        with self.lock:
            return self.metrics.copy()

    def reset_metric(self, metric_type: AuthMetricType):
        """
        Reset a specific metric to zero

        Args:
            metric_type: Type of metric to reset
        """
        with self.lock:
            if metric_type.value in self.metrics:
                if metric_type == AuthMetricType.LOGIN_SUCCESS_RATE:
                    self.metrics[metric_type.value] = {
                        "success_count": 0,
                        "failure_count": 0,
                        "rate": 0.0,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    self.metrics[metric_type.value]["count"] = 0
                    self.metrics[metric_type.value]["timestamp"] = datetime.utcnow().isoformat()

    def calculate_average_response_time(self, start_time: float) -> float:
        """
        Calculate the average response time for authentication operations

        Args:
            start_time: Start time of the operation (using time.time())

        Returns:
            Average response time in seconds
        """
        return time.time() - start_time


class AuthMetricsMiddleware:
    """
    Middleware class for tracking authentication metrics
    """

    def __init__(self, metrics_collector: AuthMetricsCollector):
        self.metrics = metrics_collector

    async def track_login_attempt(self, success: bool):
        """
        Track a login attempt in metrics

        Args:
            success: Whether the login attempt was successful
        """
        self.metrics.increment_metric(AuthMetricType.LOGIN_ATTEMPTS)
        if not success:
            self.metrics.increment_metric(AuthMetricType.FAILED_AUTH_ATTEMPTS)
        self.metrics.update_login_success_rate(success)

    async def track_token_validation(self, success: bool):
        """
        Track a token validation in metrics

        Args:
            success: Whether the token validation was successful
        """
        self.metrics.increment_metric(AuthMetricType.TOKEN_VALIDATIONS)
        if not success:
            self.metrics.increment_metric(AuthMetricType.FAILED_AUTH_ATTEMPTS)

    async def track_permission_denied(self):
        """
        Track a permission denied event in metrics
        """
        self.metrics.increment_metric(AuthMetricType.PERMISSION_DENIED)


# Global instances
auth_metrics = AuthMetricsCollector()
auth_metrics_middleware = AuthMetricsMiddleware(auth_metrics)