#!/bin/bash
echo "Creating test audio files..."

# Normal Audio 1
espeak -s 150 "Hi, can we schedule a meeting for tomorrow? Let me know your availability." -w normal-meeting.wav
echo "✅ Created: normal-meeting.wav"

# Normal Audio 2
espeak -s 150 "Your order has been confirmed and will be delivered within 5 business days. Thank you for your purchase." -w normal-order.wav
echo "✅ Created: normal-order.wav"

# Malicious Audio 1
espeak -s 150 "URGENT! Your account has been suspended. Click immediately to verify or your account will be permanently deleted." -w malicious-urgent.wav
echo "✅ Created: malicious-urgent.wav"

# Malicious Audio 2
espeak -s 150 "Congratulations! You won one million dollars. Claim your prize now at winner-claim dot com before it expires." -w malicious-lottery.wav
echo "✅ Created: malicious-lottery.wav"

echo ""
echo "All 4 audio files created successfully!"
echo "Files: normal-meeting.wav, normal-order.wav, malicious-urgent.wav, malicious-lottery.wav"
