"""WebSocket / BE Server Configuration.

Copied from server/scripts/config_ws.py for refactor into new_robot.
"""

# ============= CHANGE THESE =============
WS_URL = "ws://192.168.31.205:8080/ws-delivery-native"
API_BASE_URL = "http://192.168.31.205:8080/api/v1/robot"
ROBOT_SHARED_SECRET = "DATN_2025_2_GIAP"
ROBOT_ID = 1

# ============= DEFAULTS =============
DEFAULT_WS_URL = WS_URL or "ws://192.168.31.205:8080/ws-delivery-native"
DEFAULT_API_BASE_URL = API_BASE_URL or "http://192.168.31.205:8080/api/v1/robot"
DEFAULT_SECRET = ROBOT_SHARED_SECRET or "DATN_2025_2_GIAP"
DEFAULT_ROBOT_ID = ROBOT_ID or 1
