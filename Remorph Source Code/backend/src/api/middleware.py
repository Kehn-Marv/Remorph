import time
from fastapi import Request, Response
try:
    from fastapi.middleware.base import BaseHTTPMiddleware
except Exception:
    # Older/newer FastAPI may expose middleware via Starlette
    from starlette.middleware.base import BaseHTTPMiddleware
from src.utils.logging import setup_logger

logger = setup_logger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging and timing"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {response.status_code} "
                f"({process_time:.3f}s)"
            )
            
            # Add timing header
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Request failed after {process_time:.3f}s: {e}")
            raise

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        return response