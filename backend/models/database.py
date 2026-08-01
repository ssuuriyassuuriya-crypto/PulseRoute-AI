"""
PulseRoute AI - In-Memory Database Models
"""

# Pre-seeded Hackathon Users
USERS = {
    "admin": {
        "username": "admin",
        "password_hash": "admin123", # Simple mock hash for hackathon demo
        "role": "ADMIN",
        "name": "Traffic Control Officer"
    },
    "driver": {
        "username": "driver",
        "password_hash": "driver123",
        "role": "AMBULANCE_DRIVER",
        "name": "EMS Unit 402 - Driver"
    }
}

# Session logs and reports DB
REPORTS_DB = []
AUDIT_LOGS_DB = []
