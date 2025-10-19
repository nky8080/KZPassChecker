"""
Advanced Rate Limiting for Kanazawa Cultural Facility Agent Demo
Implements multiple rate limiting strategies to prevent abuse
"""
import time
import hashlib
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class RateLimitType(Enum):
    """Rate limit types"""
    PER_IP = "per_ip"
    PER_USER = "per_user"
    GLOBAL = "global"

@dataclass
class RateLimitRule:
    """Rate limit rule configuration"""
    max_requests: int
    window_seconds: int
    limit_type: RateLimitType
    burst_allowance: int = 0  # Additional requests allowed in burst

class RateLimitResult:
    """Rate limit check result"""
    def __init__(self, allowed: bool, remaining: int = 0, reset_time: float = 0, 
                 retry_after: int = 0, message: str = ""):
        self.allowed = allowed
        self.remaining = remaining
        self.reset_time = reset_time
        self.retry_after = retry_after
        self.message = message

class AdvancedRateLimiter:
    """Advanced rate limiter with multiple strategies"""
    
    def __init__(self):
        # In-memory storage for demo (use Redis/DynamoDB in production)
        self.request_counts: Dict[str, Tuple[int, float, int]] = {}  # key: (count, window_start, burst_used)
        self.global_count = 0
        self.global_window_start = time.time()
        
        # Rate limit rules
        self.rules = {
            RateLimitType.PER_IP: RateLimitRule(
                max_requests=10,
                window_seconds=60,
                limit_type=RateLimitType.PER_IP,
                burst_allowance=3
            ),
            RateLimitType.GLOBAL: RateLimitRule(
                max_requests=100,
                window_seconds=60,
                limit_type=RateLimitType.GLOBAL,
                burst_allowance=20
            )
        }
    
    def check_rate_limit(self, identifier: str, limit_type: RateLimitType = RateLimitType.PER_IP) -> RateLimitResult:
        """
        Check if request is within rate limits
        
        Args:
            identifier: Client identifier (IP, user ID, etc.)
            limit_type: Type of rate limit to check
            
        Returns:
            RateLimitResult with decision and metadata
        """
        current_time = time.time()
        rule = self.rules.get(limit_type)
        
        if not rule:
            return RateLimitResult(allowed=True, message="No rate limit rule found")
        
        # Clean up old entries
        self._cleanup_old_entries(current_time)
        
        if limit_type == RateLimitType.GLOBAL:
            return self._check_global_limit(current_time, rule)
        else:
            return self._check_identifier_limit(identifier, current_time, rule)
    
    def record_request(self, identifier: str, limit_type: RateLimitType = RateLimitType.PER_IP) -> None:
        """
        Record a request for rate limiting
        
        Args:
            identifier: Client identifier
            limit_type: Type of rate limit
        """
        current_time = time.time()
        
        if limit_type == RateLimitType.GLOBAL:
            self._record_global_request(current_time)
        else:
            self._record_identifier_request(identifier, current_time)
    
    def _check_identifier_limit(self, identifier: str, current_time: float, rule: RateLimitRule) -> RateLimitResult:
        """Check rate limit for specific identifier"""
        key = self._get_cache_key(identifier, rule.limit_type)
        
        if key in self.request_counts:
            count, window_start, burst_used = self.request_counts[key]
            
            # Check if we're in the same window
            if current_time - window_start < rule.window_seconds:
                total_allowed = rule.max_requests + rule.burst_allowance
                
                if count >= total_allowed:
                    retry_after = int(rule.window_seconds - (current_time - window_start)) + 1
                    return RateLimitResult(
                        allowed=False,
                        remaining=0,
                        reset_time=window_start + rule.window_seconds,
                        retry_after=retry_after,
                        message=f"Rate limit exceeded. Try again in {retry_after} seconds."
                    )
                
                remaining = total_allowed - count
                return RateLimitResult(
                    allowed=True,
                    remaining=remaining,
                    reset_time=window_start + rule.window_seconds,
                    message="Request allowed"
                )
        
        # First request or new window
        return RateLimitResult(
            allowed=True,
            remaining=rule.max_requests + rule.burst_allowance - 1,
            reset_time=current_time + rule.window_seconds,
            message="Request allowed"
        )
    
    def _check_global_limit(self, current_time: float, rule: RateLimitRule) -> RateLimitResult:
        """Check global rate limit"""
        if current_time - self.global_window_start < rule.window_seconds:
            total_allowed = rule.max_requests + rule.burst_allowance
            
            if self.global_count >= total_allowed:
                retry_after = int(rule.window_seconds - (current_time - self.global_window_start)) + 1
                return RateLimitResult(
                    allowed=False,
                    remaining=0,
                    reset_time=self.global_window_start + rule.window_seconds,
                    retry_after=retry_after,
                    message=f"Global rate limit exceeded. Try again in {retry_after} seconds."
                )
            
            remaining = total_allowed - self.global_count
            return RateLimitResult(
                allowed=True,
                remaining=remaining,
                reset_time=self.global_window_start + rule.window_seconds,
                message="Request allowed"
            )
        
        # New window
        return RateLimitResult(
            allowed=True,
            remaining=rule.max_requests + rule.burst_allowance - 1,
            reset_time=current_time + rule.window_seconds,
            message="Request allowed"
        )
    
    def _record_identifier_request(self, identifier: str, current_time: float) -> None:
        """Record request for identifier"""
        rule = self.rules[RateLimitType.PER_IP]
        key = self._get_cache_key(identifier, rule.limit_type)
        
        if key in self.request_counts:
            count, window_start, burst_used = self.request_counts[key]
            
            if current_time - window_start < rule.window_seconds:
                # Same window - increment count
                new_burst_used = burst_used
                if count >= rule.max_requests:
                    new_burst_used += 1
                
                self.request_counts[key] = (count + 1, window_start, new_burst_used)
            else:
                # New window
                self.request_counts[key] = (1, current_time, 0)
        else:
            # First request
            self.request_counts[key] = (1, current_time, 0)
    
    def _record_global_request(self, current_time: float) -> None:
        """Record global request"""
        rule = self.rules[RateLimitType.GLOBAL]
        
        if current_time - self.global_window_start < rule.window_seconds:
            self.global_count += 1
        else:
            # New window
            self.global_count = 1
            self.global_window_start = current_time
    
    def _get_cache_key(self, identifier: str, limit_type: RateLimitType) -> str:
        """Generate cache key for identifier and limit type"""
        # Hash identifier for privacy and consistent key length
        hashed_id = hashlib.sha256(identifier.encode()).hexdigest()[:16]
        return f"{limit_type.value}:{hashed_id}"
    
    def _cleanup_old_entries(self, current_time: float) -> None:
        """Clean up expired entries to prevent memory leaks"""
        expired_keys = []
        
        for key, (count, window_start, burst_used) in self.request_counts.items():
            # Determine rule based on key prefix
            if key.startswith("per_ip:"):
                rule = self.rules[RateLimitType.PER_IP]
            else:
                continue  # Skip unknown types
            
            if current_time - window_start >= rule.window_seconds * 2:  # Keep for 2x window
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.request_counts[key]
    
    def get_rate_limit_headers(self, result: RateLimitResult, rule: RateLimitRule) -> Dict[str, str]:
        """
        Get rate limit headers for HTTP response
        
        Args:
            result: Rate limit check result
            rule: Applied rate limit rule
            
        Returns:
            Dictionary of rate limit headers
        """
        headers = {
            'X-RateLimit-Limit': str(rule.max_requests + rule.burst_allowance),
            'X-RateLimit-Remaining': str(result.remaining),
            'X-RateLimit-Reset': str(int(result.reset_time))
        }
        
        if not result.allowed:
            headers['Retry-After'] = str(result.retry_after)
        
        return headers

# Global rate limiter instance
rate_limiter = AdvancedRateLimiter()

def check_request_rate_limit(client_ip: str) -> Tuple[bool, Dict[str, str], str]:
    """
    Check rate limits for a request
    
    Args:
        client_ip: Client IP address
        
    Returns:
        Tuple of (allowed, headers, error_message)
    """
    # Check per-IP limit
    ip_result = rate_limiter.check_rate_limit(client_ip, RateLimitType.PER_IP)
    if not ip_result.allowed:
        headers = rate_limiter.get_rate_limit_headers(ip_result, rate_limiter.rules[RateLimitType.PER_IP])
        return False, headers, ip_result.message
    
    # Check global limit
    global_result = rate_limiter.check_rate_limit("global", RateLimitType.GLOBAL)
    if not global_result.allowed:
        headers = rate_limiter.get_rate_limit_headers(global_result, rate_limiter.rules[RateLimitType.GLOBAL])
        return False, headers, global_result.message
    
    # Both limits passed - record the request
    rate_limiter.record_request(client_ip, RateLimitType.PER_IP)
    rate_limiter.record_request("global", RateLimitType.GLOBAL)
    
    # Return success with remaining limits
    headers = rate_limiter.get_rate_limit_headers(ip_result, rate_limiter.rules[RateLimitType.PER_IP])
    return True, headers, "Request allowed"