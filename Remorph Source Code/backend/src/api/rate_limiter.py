import time
from collections import defaultdict, deque
from typing import Dict
from fastapi import HTTPException, Request
from src.utils.logging import setup_logger

logger = setup_logger(__name__)

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, deque] = defaultdict(deque)
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request"""
        # Use X-Forwarded-For if behind proxy, otherwise remote address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _cleanup_old_requests(self, client_id: str, current_time: float):
        """Remove requests outside the time window"""
        cutoff = current_time - self.window_seconds
        while self.requests[client_id] and self.requests[client_id][0] < cutoff:
            self.requests[client_id].popleft()
    
    def check_rate_limit(self, request: Request) -> bool:
        """Check if request is within rate limits"""
        client_id = self._get_client_id(request)
        current_time = time.time()
        
        # Clean up old requests
        self._cleanup_old_requests(client_id, current_time)
        
        # Check current request count
        request_count = len(self.requests[client_id])
        
        if request_count >= self.max_requests:
            logger.warning(f"Rate limit exceeded for client {client_id}")
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Max {self.max_requests} requests per {self.window_seconds} seconds."
            )
        
        # Add current request
        self.requests[client_id].append(current_time)
        
        logger.debug(f"Rate limit check passed for {client_id}: {request_count + 1}/{self.max_requests}")
        return True

# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=10, window_seconds=60)