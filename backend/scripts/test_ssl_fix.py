#!/usr/bin/env python3
"""
Test script to verify SSL fixes for agricultural data fetcher
"""

import asyncio
import logging
import socket
import ssl
from urllib.parse import urlparse

import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_ssl_connection():
    """Test SSL connection to problematic sites"""
    
    # Test URLs
    test_urls = [
        "https://kvk.icar.gov.in",
        "https://www.icar.org.in",
        "https://data.gov.in"
    ]
    
    for url in test_urls:
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing: {url}")
        logger.info(f"{'='*60}")
        
        try:
            # Parse URL
            parsed = urlparse(url)
            host = parsed.hostname
            port = parsed.port or 443
            
            # Test 1: DNS Resolution
            logger.info("1. Testing DNS resolution...")
            try:
                ip = socket.gethostbyname(host)
                logger.info(f"   ✓ DNS successful: {host} -> {ip}")
            except socket.gaierror as e:
                logger.error(f"   ✗ DNS failed: {e}")
                continue
            
            # Test 2: Basic Socket Connection
            logger.info("2. Testing basic socket connection...")
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result == 0:
                    logger.info(f"   ✓ Socket connection successful to {host}:{port}")
                else:
                    logger.error(f"   ✗ Socket connection failed (error code: {result})")
                    continue
            except Exception as e:
                logger.error(f"   ✗ Socket test failed: {e}")
                continue
            
            # Test 3: SSL Context
            logger.info("3. Testing SSL context...")
            try:
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                with socket.create_connection((host, port), timeout=10) as sock:
                    with ssl_context.wrap_socket(sock, server_hostname=host) as ssock:
                        cert = ssock.getpeercert()
                        logger.info(f"   ✓ SSL handshake successful")
                        logger.info(f"   ✓ Certificate subject: {cert.get('subject', 'N/A')}")
            except Exception as e:
                logger.error(f"   ✗ SSL handshake failed: {e}")
                continue
            
            # Test 4: aiohttp with SSL bypass
            logger.info("4. Testing aiohttp with SSL bypass...")
            try:
                timeout = aiohttp.ClientTimeout(total=30, connect=10)
                connector = aiohttp.TCPConnector(
                    ssl=False,  # Disable SSL verification
                    use_dns_cache=True,
                    family=socket.AF_INET
                )
                
                async with aiohttp.ClientSession(
                    timeout=timeout,
                    connector=connector
                ) as session:
                    async with session.get(url) as response:
                        logger.info(f"   ✓ HTTP request successful: {response.status}")
                        if response.status == 200:
                            content_length = len(await response.text())
                            logger.info(f"   ✓ Content length: {content_length} characters")
                        else:
                            logger.warning(f"   ⚠ HTTP status: {response.status}")
                            
            except Exception as e:
                logger.error(f"   ✗ aiohttp request failed: {e}")
                
        except Exception as e:
            logger.error(f"Unexpected error testing {url}: {e}")
        
        logger.info("")

async def main():
    """Main test function"""
    logger.info("Starting SSL connectivity tests...")
    await test_ssl_connection()
    logger.info("SSL connectivity tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
