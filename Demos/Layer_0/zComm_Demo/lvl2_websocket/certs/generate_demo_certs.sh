#!/bin/bash
# Generate self-signed SSL certificate for WSS demo
# 
# This creates a certificate valid for 10 years (3650 days)
# FOR DEMO/DEVELOPMENT USE ONLY - NOT FOR PRODUCTION

echo "Generating self-signed SSL certificate for WSS demo..."

openssl req -x509 -newkey rsa:4096 -keyout demo.key -out demo.cert \
  -days 3650 -nodes \
  -subj "/C=US/ST=Demo/L=Demo/O=zCLI/CN=localhost"

echo ""
echo "✓ Generated demo.cert and demo.key"
echo ""
echo "⚠️  WARNING: These are for DEMO ONLY!"
echo "   Never use self-signed certificates in production."
echo "   Use Let's Encrypt or a proper Certificate Authority."

