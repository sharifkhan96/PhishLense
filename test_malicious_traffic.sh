#!/bin/bash
# Script to generate malicious traffic events for testing

echo "🚨 Generating malicious traffic events..."

# 1. SQL Injection Attack
echo "1. Creating SQL Injection attack..."
curl -X POST http://localhost:8000/api/traffic/receive/ \
  -H "Content-Type: application/json" \
  -d '{
    "source_ip": "192.168.1.100",
    "destination_ip": "10.0.0.1",
    "port": 80,
    "payload": "GET /login.php?username=admin'\'' OR '\''1'\''='\''1&password=test HTTP/1.1",
    "payload_type": "sqli",
    "organization": "test-org"
  }'
echo -e "\n"

# 2. XSS Attack
echo "2. Creating XSS attack..."
curl -X POST http://localhost:8000/api/traffic/receive/ \
  -H "Content-Type: application/json" \
  -d '{
    "source_ip": "203.0.113.45",
    "destination_ip": "10.0.0.1",
    "port": 80,
    "payload": "GET /search?q=<script>alert(\"XSS\")</script> HTTP/1.1",
    "payload_type": "xss",
    "organization": "test-org"
  }'
echo -e "\n"

# 3. Command Injection
echo "3. Creating Command Injection attack..."
curl -X POST http://localhost:8000/api/traffic/receive/ \
  -H "Content-Type: application/json" \
  -d '{
    "source_ip": "198.51.100.23",
    "destination_ip": "10.0.0.1",
    "port": 80,
    "payload": "GET /api/exec?cmd=cat /etc/passwd HTTP/1.1",
    "payload_type": "command_injection",
    "organization": "test-org"
  }'
echo -e "\n"

# 4. Path Traversal Attack
echo "4. Creating Path Traversal attack..."
curl -X POST http://localhost:8000/api/traffic/receive/ \
  -H "Content-Type: application/json" \
  -d '{
    "source_ip": "203.0.113.67",
    "destination_ip": "10.0.0.1",
    "port": 80,
    "payload": "GET /../../etc/passwd HTTP/1.1",
    "payload_type": "path_traversal",
    "organization": "test-org"
  }'
echo -e "\n"

# 5. Remote Code Execution Attempt
echo "5. Creating RCE attack..."
curl -X POST http://localhost:8000/api/traffic/receive/ \
  -H "Content-Type: application/json" \
  -d '{
    "source_ip": "198.51.100.89",
    "destination_ip": "10.0.0.1",
    "port": 443,
    "payload": "POST /upload.php HTTP/1.1\nContent-Type: multipart/form-data\n\n<?php system($_GET[\"cmd\"]); ?>",
    "payload_type": "rce",
    "organization": "test-org"
  }'
echo -e "\n"

# 6. Brute Force Login Attempt
echo "6. Creating Brute Force attack..."
curl -X POST http://localhost:8000/api/traffic/receive/ \
  -H "Content-Type: application/json" \
  -d '{
    "source_ip": "192.168.1.200",
    "destination_ip": "10.0.0.1",
    "port": 22,
    "payload": "SSH-2.0-OpenSSH_7.4\nInvalid user: admin\nInvalid password attempt #47",
    "payload_type": "brute_force",
    "organization": "test-org"
  }'
echo -e "\n"

# 7. Port Scanning Activity
echo "7. Creating Port Scan activity..."
curl -X POST http://localhost:8000/api/traffic/receive/ \
  -H "Content-Type: application/json" \
  -d '{
    "source_ip": "203.0.113.123",
    "destination_ip": "10.0.0.1",
    "port": 8080,
    "payload": "GET / HTTP/1.1\nHost: 10.0.0.1:8080\nUser-Agent: Nmap",
    "payload_type": "port_scan",
    "organization": "test-org"
  }'
echo -e "\n"

# 8. Malicious File Upload
echo "8. Creating Malicious File Upload..."
curl -X POST http://localhost:8000/api/traffic/receive/ \
  -H "Content-Type: application/json" \
  -d '{
    "source_ip": "198.51.100.156",
    "destination_ip": "10.0.0.1",
    "port": 80,
    "payload": "POST /upload.php HTTP/1.1\nContent-Type: multipart/form-data\n\n[Malicious PHP shell code]",
    "payload_type": "malicious_upload",
    "organization": "test-org"
  }'
echo -e "\n"

echo "✅ Done! Check your dashboard for the new malicious traffic events."


