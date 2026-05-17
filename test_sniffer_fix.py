#!/usr/bin/env python3
"""Test script to verify cicflow_fast sniffer fix."""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def log(msg):
    print(f"[{datetime.now().isoformat()}] {msg}", flush=True)

def main():
    # Step 1: Login
    log("Step 1: Attempting login...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "admin@aegis-ids.local",
            "password": "admin123"
        },
        timeout=10
    )
    
    if login_response.status_code != 200:
        log(f"✗ Login failed: {login_response.status_code}")
        log(f"  Response: {login_response.text}")
        return
    
    token = login_response.json().get("access_token")
    if not token:
        log("✗ No access token in response")
        log(f"  Response: {login_response.json()}")
        return
    
    log(f"✓ Login successful, token: {token[:20]}...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Check current sniffer status
    log("\nStep 2: Checking sniffer status...")
    status_response = requests.get(
        f"{BASE_URL}/sniffer/status",
        headers=headers,
        timeout=10
    )
    log(f"  Status: {status_response.json()}")
    
    # Step 3: Start sniffer
    log("\nStep 3: Starting sniffer...")
    start_response = requests.post(
        f"{BASE_URL}/sniffer/start",
        json={"interface": "eth0"},
        headers=headers,
        timeout=10
    )
    
    if start_response.status_code != 200:
        log(f"✗ Start failed: {start_response.status_code}")
        log(f"  Response: {start_response.text}")
        return
    
    log(f"✓ Start successful: {start_response.json()}")
    
    # Step 4: Monitor sniffer for 10 seconds
    log("\nStep 4: Monitoring sniffer for 10 seconds...")
    for i in range(10):
        time.sleep(1)
        status_response = requests.get(
            f"{BASE_URL}/sniffer/status",
            headers=headers,
            timeout=10
        )
        status = status_response.json()
        is_running = status.get("is_running", False)
        symbol = "●" if is_running else "○"
        log(f"  [{i+1}/10] Sniffer running: {symbol} ({is_running})")
        if not is_running:
            log("  WARNING: Sniffer stopped")
            break
    
    # Step 5: Stop sniffer
    log("\nStep 5: Stopping sniffer...")
    stop_response = requests.post(
        f"{BASE_URL}/sniffer/stop",
        headers=headers,
        timeout=10
    )
    log(f"  Stop response: {stop_response.json()}")
    
    log("\n✓ Test completed")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"✗ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
