"""
HTTP client management module for Claude Code hooks.
Provides multiple HTTP client backends with retries and caching.
"""

import asyncio
import logging
import time
from typing import Any

# HTTP client libraries (optional dependencies)
try:
    import httpx
except ImportError:
    httpx = None  # type: ignore

try:
    import requests
    import requests_cache
except ImportError:
    requests = None  # type: ignore
    requests_cache = None  # type: ignore

try:
    import urllib3
    from urllib3.poolmanager import PoolManager
    from urllib3.util.retry import Retry
except ImportError:
    urllib3 = None  # type: ignore
    Retry = None  # type: ignore
    PoolManager = None  # type: ignore

try:
    import websockets
except ImportError:
    websockets = None  # type: ignore

logger = logging.getLogger(__name__)


class HTTPClientManager:
    """Comprehensive HTTP client manager with multiple backends"""

    def __init__(self, cache_manager: Any | None = None):
        self.cache_manager = cache_manager

        # Initialize HTTP clients
        self.httpx_client = None
        self.requests_session = None
        self.urllib3_pool = None
        self.websocket_connections = {}

        # Initialize based on available libraries
        self._init_httpx()
        self._init_requests()
        self._init_urllib3()

    def _init_httpx(self):
        """Initialize HTTPX async client"""
        if httpx is not None:
            try:
                timeout = httpx.Timeout(10.0, connect=5.0)
                limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
                self.httpx_client = httpx.AsyncClient(
                    timeout=timeout,
                    limits=limits,
                    follow_redirects=True
                )
            except Exception:
                self.httpx_client = None

    def _init_requests(self):
        """Initialize requests session with caching"""
        if requests is not None:
            try:
                self.requests_session = requests.Session()

                # Configure caching if available
                if requests_cache is not None and self.cache_manager:
                    try:
                        cache_file = self.cache_manager.cache_dir / "http_cache.sqlite"
                        requests_cache.install_cache(
                            str(cache_file),
                            backend='sqlite',
                            expire_after=300  # 5 minutes
                        )
                    except Exception:
                        pass  # Continue without caching if it fails

                # Configure retries
                if urllib3 is not None:
                    try:
                        from requests.adapters import HTTPAdapter
                        retry_strategy = urllib3.Retry(
                            total=3,
                            status_forcelist=[429, 500, 502, 503, 504],
                            allowed_methods=["HEAD", "GET", "OPTIONS"]
                        )
                        adapter = HTTPAdapter(max_retries=retry_strategy)
                        self.requests_session.mount("http://", adapter)
                        self.requests_session.mount("https://", adapter)
                    except Exception:
                        pass  # Continue without retries if it fails
            except Exception:
                self.requests_session = None

    def _init_urllib3(self):
        """Initialize urllib3 pool manager"""
        if urllib3 is not None and Retry is not None and PoolManager is not None:
            try:
                retry = Retry(
                    total=3,
                    status_forcelist=[429, 500, 502, 503, 504]
                )
                self.urllib3_pool = PoolManager(
                    num_pools=10,
                    maxsize=10,
                    retries=retry,
                    timeout=urllib3.Timeout(connect=5.0, read=10.0)
                )
            except Exception:
                self.urllib3_pool = None

    async def httpx_request(self, method: str, url: str, **kwargs) -> dict[str, Any] | None:
        """Make async HTTP request using HTTPX"""
        if self.httpx_client is None:
            return None

        try:
            response = await self.httpx_client.request(method, url, **kwargs)
            return {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'content': response.text,
                'json': response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            }
        except Exception as e:
            return {'error': str(e)}

    def requests_request(self, method: str, url: str, **kwargs) -> dict[str, Any] | None:
        """Make HTTP request using requests"""
        if self.requests_session is None:
            return None

        try:
            response = self.requests_session.request(method, url, **kwargs)
            return {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'content': response.text,
                'json': response.json() if response.headers.get('content-type', '').startswith('application/json') else None,
                'from_cache': getattr(response, 'from_cache', False)
            }
        except Exception as e:
            return {'error': str(e)}

    def urllib3_request(self, method: str, url: str, **kwargs) -> dict[str, Any] | None:
        """Make HTTP request using urllib3"""
        if self.urllib3_pool is None:
            return None

        try:
            response = self.urllib3_pool.request(method, url, **kwargs)
            return {
                'status_code': response.status,
                'headers': dict(response.headers),
                'content': response.data.decode('utf-8') if response.data else None
            }
        except Exception as e:
            return {'error': str(e)}

    async def websocket_connect(self, uri: str, connection_id: str | None = None) -> str | None:
        """Connect to WebSocket using websockets library"""
        if websockets is None:
            return None

        connection_id = connection_id or f"ws_{hash(uri)}_{int(time.time())}"

        try:
            websocket = await websockets.connect(uri)
            self.websocket_connections[connection_id] = websocket
            return connection_id
        except Exception as e:
            return f"error: {str(e)}"

    async def websocket_send(self, connection_id: str, message: str) -> bool:
        """Send message via WebSocket connection"""
        if connection_id not in self.websocket_connections:
            return False

        try:
            websocket = self.websocket_connections[connection_id]
            await websocket.send(message)
            return True
        except Exception:
            # Remove broken connection
            if connection_id in self.websocket_connections:
                del self.websocket_connections[connection_id]
            return False

    async def websocket_receive(self, connection_id: str) -> str | None:
        """Receive message from WebSocket connection"""
        if connection_id not in self.websocket_connections:
            return None

        try:
            websocket = self.websocket_connections[connection_id]
            message = await websocket.recv()
            return message
        except Exception:
            # Remove broken connection
            if connection_id in self.websocket_connections:
                del self.websocket_connections[connection_id]
            return None

    async def websocket_close(self, connection_id: str) -> bool:
        """Close WebSocket connection"""
        if connection_id not in self.websocket_connections:
            return False

        try:
            websocket = self.websocket_connections[connection_id]
            await websocket.close()
            del self.websocket_connections[connection_id]
            return True
        except Exception:
            # Force remove from connections
            if connection_id in self.websocket_connections:
                del self.websocket_connections[connection_id]
            return False

    def close(self):
        """Close all HTTP clients and connections"""
        if self.httpx_client:
            asyncio.create_task(self.httpx_client.aclose())

        if self.requests_session:
            self.requests_session.close()

        # Close all websocket connections
        for conn_id in list(self.websocket_connections.keys()):
            asyncio.create_task(self.websocket_close(conn_id))

    def __del__(self):
        """Cleanup on deletion"""
        self.close()


# Export main components
__all__ = ['HTTPClientManager']
