#!/usr/bin/env python3
"""
HTTP client management module for user prompt processing
"""

import asyncio
import time
from typing import Any

# HTTP client libraries
try:
    import httpx
except ImportError:
    httpx = None

try:
    import requests
    import requests_cache
except ImportError:
    requests = None
    requests_cache = None

try:
    import urllib3
    from urllib3.poolmanager import PoolManager
    from urllib3.util.retry import Retry
except ImportError:
    urllib3 = None
    Retry = None
    PoolManager = None

try:
    import websockets
except ImportError:
    websockets = None


class UserPromptHTTPClientManager:
    """HTTP client manager specifically for user prompt processing"""

    def __init__(self, cache_manager=None):
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
        """Initialize HTTPX async client for user prompt processing"""
        if httpx is not None:
            try:
                timeout = httpx.Timeout(30.0, connect=10.0)  # Longer timeouts for user requests
                limits = httpx.Limits(max_keepalive_connections=10, max_connections=20)
                self.httpx_client = httpx.AsyncClient(
                    timeout=timeout,
                    limits=limits,
                    follow_redirects=True,
                    headers={'User-Agent': 'Claude-Code-Hook/1.0'}
                )
            except Exception:
                self.httpx_client = None

    def _init_requests(self):
        """Initialize requests session with caching for user prompts"""
        if requests is not None:
            try:
                self.requests_session = requests.Session()
                self.requests_session.headers.update({'User-Agent': 'Claude-Code-Hook/1.0'})

                # Configure caching with longer TTL for user requests
                if requests_cache is not None and self.cache_manager:
                    try:
                        cache_file = self.cache_manager.cache_dir / "user_prompt_http_cache.sqlite"
                        requests_cache.install_cache(
                            str(cache_file),
                            backend='sqlite',
                            expire_after=600  # 10 minutes for user requests
                        )
                    except Exception:
                        pass  # Continue without caching if it fails

                # Configure retries for robustness
                if urllib3 is not None:
                    try:
                        from requests.adapters import HTTPAdapter
                        retry_strategy = urllib3.Retry(
                            total=5,  # More retries for user requests
                            backoff_factor=1,
                            status_forcelist=[429, 500, 502, 503, 504],
                            allowed_methods=["HEAD", "GET", "POST", "OPTIONS"]
                        )
                        adapter = HTTPAdapter(max_retries=retry_strategy)
                        self.requests_session.mount("http://", adapter)
                        self.requests_session.mount("https://", adapter)
                    except Exception:
                        pass  # Continue without retries if it fails
            except Exception:
                self.requests_session = None

    def _init_urllib3(self):
        """Initialize urllib3 pool manager for user prompts"""
        if urllib3 is not None and Retry is not None and PoolManager is not None:
            try:
                retry = Retry(
                    total=5,
                    backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504]
                )
                self.urllib3_pool = PoolManager(
                    num_pools=20,
                    maxsize=20,
                    retries=retry,
                    timeout=urllib3.Timeout(connect=10.0, read=30.0)
                )
            except Exception:
                self.urllib3_pool = None
        else:
            self.urllib3_pool = None

    async def fetch_url_content(self, url: str, method: str = 'GET', **kwargs) -> dict[str, Any]:
        """Fetch URL content using the best available HTTP client"""
        cache_key = f"http_{method}_{hash(url + str(kwargs))}"

        # Check cache first
        if self.cache_manager:
            cached_result = self.cache_manager.get_command_result(cache_key)
            if cached_result is not None:
                return cached_result

        result = None

        # Try HTTPX first (async, most modern)
        if self.httpx_client is not None:
            try:
                result = await self.httpx_request(method, url, **kwargs)
            except Exception as e:
                result = {'error': f'HTTPX failed: {str(e)}'}

        # Fallback to requests
        if (result is None or 'error' in result) and self.requests_session is not None:
            try:
                result = self.requests_request(method, url, **kwargs)
            except Exception as e:
                result = {'error': f'Requests failed: {str(e)}'}

        # Fallback to urllib3
        if (result is None or 'error' in result) and self.urllib3_pool is not None:
            try:
                result = self.urllib3_request(method, url, **kwargs)
            except Exception as e:
                result = {'error': f'urllib3 failed: {str(e)}'}

        # Cache successful results
        if result and 'error' not in result and self.cache_manager:
            self.cache_manager.set_command_result(cache_key, result)

        return result or {'error': 'No HTTP client available'}

    async def httpx_request(self, method: str, url: str, **kwargs) -> dict[str, Any]:
        """Make async HTTP request using HTTPX"""
        if self.httpx_client is None:
            return {'error': 'HTTPX not available'}

        response = await self.httpx_client.request(method, url, **kwargs)
        return {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'content': response.text,
            'json': response.json() if self._is_json_content(response.headers) else None,
            'client': 'httpx'
        }

    def requests_request(self, method: str, url: str, **kwargs) -> dict[str, Any]:
        """Make HTTP request using requests"""
        if self.requests_session is None:
            return {'error': 'Requests not available'}

        response = self.requests_session.request(method, url, **kwargs)
        return {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'content': response.text,
            'json': response.json() if self._is_json_content(response.headers) else None,
            'from_cache': getattr(response, 'from_cache', False),
            'client': 'requests'
        }

    def urllib3_request(self, method: str, url: str, **kwargs) -> dict[str, Any]:
        """Make HTTP request using urllib3"""
        if self.urllib3_pool is None:
            return {'error': 'urllib3 not available'}

        response = self.urllib3_pool.request(method, url, **kwargs)
        return {
            'status_code': response.status,
            'headers': dict(response.headers),
            'content': response.data.decode('utf-8') if response.data else None,
            'client': 'urllib3'
        }

    def _is_json_content(self, headers) -> bool:
        """Check if response content is JSON"""
        # Handle different header types (Dict, Headers, CaseInsensitiveDict)
        if hasattr(headers, 'get'):
            content_type = headers.get('content-type', '').lower()
        else:
            content_type = str(headers.get('content-type', '')).lower()
        return 'application/json' in content_type

    async def websocket_connect_for_prompt(self, uri: str, prompt_context: str | None = None) -> str | None:
        """Connect to WebSocket for prompt-related communication"""
        if websockets is None:
            return None

        connection_id = f"prompt_ws_{hash(uri + (prompt_context or ''))}_{int(time.time())}"

        try:
            websocket = await websockets.connect(uri)
            self.websocket_connections[connection_id] = {
                'websocket': websocket,
                'context': prompt_context,
                'created': time.time()
            }
            return connection_id
        except Exception as e:
            return f"error: {str(e)}"

    def get_client_status(self) -> dict[str, Any]:
        """Get status of all HTTP clients"""
        return {
            'httpx': self.httpx_client is not None,
            'requests': self.requests_session is not None,
            'urllib3': self.urllib3_pool is not None,
            'websockets': websockets is not None,
            'active_websockets': len(self.websocket_connections)
        }

    def close(self):
        """Close all HTTP clients and connections"""
        # Close httpx client
        if self.httpx_client:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.httpx_client.aclose())
                else:
                    # If no event loop is running, create one temporarily
                    asyncio.run(self.httpx_client.aclose())
            except RuntimeError:
                # If we can't get an event loop, just skip async cleanup
                pass

        if self.requests_session:
            self.requests_session.close()

        # Close all websocket connections
        for connection_id in list(self.websocket_connections.keys()):
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self._close_websocket(connection_id))
                else:
                    asyncio.run(self._close_websocket(connection_id))
            except RuntimeError:
                # Skip if no event loop
                pass

    async def _close_websocket(self, connection_id: str):
        """Close a specific websocket connection"""
        if connection_id in self.websocket_connections:
            try:
                websocket_info = self.websocket_connections[connection_id]
                await websocket_info['websocket'].close()
            except Exception:
                pass
            finally:
                del self.websocket_connections[connection_id]
