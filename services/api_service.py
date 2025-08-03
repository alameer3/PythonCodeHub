"""
API service for handling HTTP requests and external API integrations.
Provides a consistent interface for API communications.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from urllib.request import urlopen, Request
from urllib.parse import urlencode, urljoin
from urllib.error import HTTPError, URLError
import json

from config.settings import Settings
from data.models import APIResponse
from core.exceptions import APIError


class APIService:
    """Service for handling API requests and responses."""
    
    def __init__(self, settings: Settings):
        """
        Initialize API service with configuration.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.logger = logging.getLogger(self.__class__.__name__)
        self.base_url = settings.api_base_url
        self.api_key = settings.api_key
        self.default_headers = {
            'Content-Type': 'application/json',
            'User-Agent': f'{settings.app_name}/{settings.app_version}'
        }
        
        if self.api_key:
            self.default_headers['Authorization'] = f'Bearer {self.api_key}'
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, 
            headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """
        Make GET request to API endpoint.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            headers: Additional headers
            
        Returns:
            APIResponse object with response data
        """
        url = urljoin(self.base_url, endpoint)
        
        if params:
            query_string = urlencode(params)
            url = f"{url}?{query_string}"
        
        return self._make_request('GET', url, headers=headers)
    
    def post(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
             headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """
        Make POST request to API endpoint.
        
        Args:
            endpoint: API endpoint path
            data: Request payload
            headers: Additional headers
            
        Returns:
            APIResponse object with response data
        """
        url = urljoin(self.base_url, endpoint)
        return self._make_request('POST', url, data=data, headers=headers)
    
    def put(self, endpoint: str, data: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """
        Make PUT request to API endpoint.
        
        Args:
            endpoint: API endpoint path
            data: Request payload
            headers: Additional headers
            
        Returns:
            APIResponse object with response data
        """
        url = urljoin(self.base_url, endpoint)
        return self._make_request('PUT', url, data=data, headers=headers)
    
    def delete(self, endpoint: str, headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """
        Make DELETE request to API endpoint.
        
        Args:
            endpoint: API endpoint path
            headers: Additional headers
            
        Returns:
            APIResponse object with response data
        """
        url = urljoin(self.base_url, endpoint)
        return self._make_request('DELETE', url, headers=headers)
    
    def _make_request(self, method: str, url: str, data: Optional[Dict[str, Any]] = None,
                     headers: Optional[Dict[str, str]] = None) -> APIResponse:
        """
        Make HTTP request with error handling and response parsing.
        
        Args:
            method: HTTP method
            url: Full URL
            data: Request payload
            headers: Request headers
            
        Returns:
            APIResponse object
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Making {method} request to: {url}")
            
            # Prepare headers
            request_headers = self.default_headers.copy()
            if headers:
                request_headers.update(headers)
            
            # Prepare request
            request_data = None
            if data and method in ['POST', 'PUT']:
                request_data = json.dumps(data).encode('utf-8')
            
            request = Request(url, data=request_data, headers=request_headers)
            request.get_method = lambda: method
            
            # Make request
            with urlopen(request, timeout=30) as response:
                response_data = response.read().decode('utf-8')
                
                # Try to parse as JSON
                try:
                    parsed_data = json.loads(response_data)
                except json.JSONDecodeError:
                    parsed_data = response_data
                
                response_headers = dict(response.headers)
                response_time = time.time() - start_time
                
                api_response = APIResponse(
                    status_code=response.status,
                    data=parsed_data,
                    headers=response_headers,
                    response_time=response_time
                )
                
                self.logger.info(f"Request completed: {method} {url} - {response.status} - {response_time:.2f}s")
                return api_response
                
        except HTTPError as e:
            response_time = time.time() - start_time
            error_data = None
            
            try:
                error_data = e.read().decode('utf-8')
                try:
                    error_data = json.loads(error_data)
                except json.JSONDecodeError:
                    pass
            except Exception:
                pass
            
            api_response = APIResponse(
                status_code=e.code,
                data=error_data,
                response_time=response_time
            )
            
            self.logger.error(f"HTTP error: {method} {url} - {e.code} - {response_time:.2f}s")
            return api_response
            
        except URLError as e:
            response_time = time.time() - start_time
            self.logger.error(f"URL error: {method} {url} - {e.reason}")
            raise APIError(f"Network error: {e.reason}")
            
        except Exception as e:
            response_time = time.time() - start_time
            self.logger.error(f"Unexpected error: {method} {url} - {e}")
            raise APIError(f"Request failed: {e}")
    
    def health_check(self) -> bool:
        """
        Perform health check on the API.
        
        Returns:
            True if API is healthy, False otherwise
        """
        try:
            response = self.get('/health')
            return response.is_success
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False
    
    def get_api_info(self) -> Optional[Dict[str, Any]]:
        """
        Get API information and metadata.
        
        Returns:
            API information dictionary or None if not available
        """
        try:
            response = self.get('/info')
            if response.is_success:
                return response.data
            return None
        except Exception as e:
            self.logger.error(f"Failed to get API info: {e}")
            return None
    
    def upload_data(self, endpoint: str, data: List[Dict[str, Any]]) -> APIResponse:
        """
        Upload data to API endpoint.
        
        Args:
            endpoint: Upload endpoint
            data: Data to upload
            
        Returns:
            APIResponse object
        """
        payload = {
            'data': data,
            'timestamp': time.time(),
            'count': len(data)
        }
        
        return self.post(endpoint, payload)
    
    def batch_request(self, requests: List[Dict[str, Any]]) -> List[APIResponse]:
        """
        Make multiple API requests in batch.
        
        Args:
            requests: List of request specifications
            
        Returns:
            List of APIResponse objects
        """
        responses = []
        
        for request_spec in requests:
            method = request_spec.get('method', 'GET')
            endpoint = request_spec.get('endpoint', '')
            data = request_spec.get('data')
            headers = request_spec.get('headers')
            
            try:
                if method.upper() == 'GET':
                    response = self.get(endpoint, data, headers)
                elif method.upper() == 'POST':
                    response = self.post(endpoint, data, headers)
                elif method.upper() == 'PUT':
                    response = self.put(endpoint, data, headers)
                elif method.upper() == 'DELETE':
                    response = self.delete(endpoint, headers)
                else:
                    raise APIError(f"Unsupported method: {method}")
                
                responses.append(response)
                
            except Exception as e:
                # Create error response
                error_response = APIResponse(
                    status_code=500,
                    data={'error': str(e)},
                    response_time=0.0
                )
                responses.append(error_response)
        
        return responses
