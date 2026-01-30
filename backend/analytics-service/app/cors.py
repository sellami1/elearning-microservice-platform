from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class GranularCORSMiddleware(BaseHTTPMiddleware):
    """
    Middleware to apply different CORS policies based on the request path.
    - /metrics/*: Publicly accessible (Access-Control-Allow-Origin: *)
    - /events/*: Restricted to specific origins (e.g., course-service)
    """
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # 1. Handle Preflight (OPTIONS) requests
        if request.method == "OPTIONS":
            from fastapi.responses import Response
            response = Response()
            if path.startswith("/metrics"):
                response.headers["Access-Control-Allow-Origin"] = "*"
                response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            elif path.startswith("/events"):
                response.headers["Access-Control-Allow-Origin"] = "http://course-service:8000"
                response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
            
            response.headers["Access-Control-Allow-Headers"] = "*"
            return response
            
        # 2. Handle actual requests
        response = await call_next(request)
        
        if path.startswith("/metrics"):
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
        elif path.startswith("/events"):
            response.headers["Access-Control-Allow-Origin"] = "http://course-service:8000"
            response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
            
        return response
