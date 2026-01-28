"""
src/rtc_config.py

WebRTC Configuration for Streamlit-WebRTC.
Handles ICE server configuration with STUN and TURN servers for reliable
connectivity across various network environments (symmetric NATs, firewalls, etc.)

Solution: Uses Metered.ca's Open Relay free TURN servers (20GB/month free)
https://www.metered.ca/tools/openrelay/
"""

import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_ice_servers():
    """
    Returns the ICE servers configuration for WebRTC.
    
    This configuration uses a combination of:
    1. Google's public STUN servers (for simple NAT traversal)
    2. Metered.ca's Open Relay TURN servers (for relay when direct connection fails)
    
    The TURN servers run on ports 80/443 to bypass most corporate firewalls
    and support both TCP and UDP protocols.
    
    Environment Variables Required:
        TURN_SERVER_URL: The TURN server URL (e.g., "a]turn:a]@relay.metered.ca:443")
        TURN_USERNAME: The TURN server username (from Metered.ca dashboard)
        TURN_CREDENTIAL: The TURN server credential/password
    
    If environment variables are not set, falls back to static Open Relay servers
    which require Metered.ca free account API credentials.
    
    Returns:
        list: Array of ICE server configurations
    """
    
    # Try to get credentials from environment variables (for production/Hugging Face)
    turn_url = os.environ.get("TURN_SERVER_URL", "")
    turn_username = os.environ.get("TURN_USERNAME", "")
    turn_credential = os.environ.get("TURN_CREDENTIAL", "")
    
    # Base STUN servers (always included for basic NAT traversal)
    ice_servers = [
        {"urls": ["stun:stun.l.google.com:19302"]},
        {"urls": ["stun:stun1.l.google.com:19302"]},
    ]
    
    # Check if custom TURN credentials are provided via environment
    if turn_url and turn_username and turn_credential:
        logger.info("Using custom TURN server credentials from environment variables")
        ice_servers.append({
            "urls": turn_url if isinstance(turn_url, list) else [turn_url],
            "username": turn_username,
            "credential": turn_credential
        })
    else:
        # Use Metered.ca Open Relay free TURN servers (static configuration)
        # These servers provide 20GB free TURN usage per month
        # Running on ports 80/443 to bypass corporate firewalls
        logger.info("Using Metered.ca Open Relay free TURN servers")
        
        # Metered.ca Open Relay TURN servers - Multiple ports for firewall bypass
        # Note: For production, sign up at https://dashboard.metered.ca/signup?tool=turnserver
        # and use the API to get personalized credentials with better reliability
        ice_servers.extend([
            # TURN servers on standard ports (bypass most firewalls)
            {
                "urls": "turn:openrelay.metered.ca:80",
                "username": "openrelayproject",
                "credential": "openrelayproject"
            },
            {
                "urls": "turn:openrelay.metered.ca:80?transport=tcp",
                "username": "openrelayproject",
                "credential": "openrelayproject"
            },
            {
                "urls": "turn:openrelay.metered.ca:443",
                "username": "openrelayproject",
                "credential": "openrelayproject"
            },
            {
                "urls": "turn:openrelay.metered.ca:443?transport=tcp",
                "username": "openrelayproject",
                "credential": "openrelayproject"
            },
            # TURNS (TURN over TLS) - For deep packet inspection firewalls
            {
                "urls": "turns:openrelay.metered.ca:443?transport=tcp",
                "username": "openrelayproject",
                "credential": "openrelayproject"
            },
        ])
    
    return ice_servers


def get_rtc_configuration():
    """
    Returns the complete RTC configuration dictionary for streamlit-webrtc.
    
    Returns:
        dict: RTC configuration with iceServers array
    """
    return {
        "iceServers": get_ice_servers(),
        # Additional ICE configuration options
        "iceCandidatePoolSize": 10,  # Pre-gather ICE candidates for faster connection
    }


# For debugging - print configuration on import if DEBUG mode
if os.environ.get("DEBUG_RTC", "").lower() == "true":
    import json
    print("=" * 50)
    print("RTC Configuration (DEBUG MODE):")
    print(json.dumps(get_rtc_configuration(), indent=2))
    print("=" * 50)
