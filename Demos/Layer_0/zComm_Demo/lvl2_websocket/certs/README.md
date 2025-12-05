# Demo SSL Certificates

These are **self-signed certificates for demo purposes ONLY**. They enable WSS (WebSocket Secure) connections for local development and learning.

## Files

- `demo.cert` - SSL certificate (public key)
- `demo.key` - Private key
- `generate_demo_certs.sh` - Script to regenerate certificates

## Security Notice

**IMPORTANT:** These certificates are intentionally checked into the repository for educational purposes. 

**NEVER commit real SSL certificates or private keys to version control!**

## Production

For production WebSocket Secure (WSS) connections, use certificates from:

- **Let's Encrypt** (free, automated, recommended)
- Your organization's Certificate Authority
- Commercial SSL certificate providers (DigiCert, Comodo, etc.)

## Browser Security Warnings

When you open the WSS demo (`4_client_wss.html`), your browser will show a security warning because the certificate is self-signed. This is expected behavior.

**To proceed:**
1. Click "Advanced" or "Show Details"
2. Click "Proceed to localhost (unsafe)"
3. The warning appears because browsers trust certificates from Certificate Authorities, not self-signed ones

In production with proper certificates, users won't see this warning.

## Regenerating Certificates

If you need to regenerate the demo certificates:

```bash
cd /path/to/zolo-zcli/Demos/Layer_0/zComm_Demo/lvl2_websocket/certs
./generate_demo_certs.sh
```

Or manually:

```bash
openssl req -x509 -newkey rsa:4096 -keyout demo.key -out demo.cert \
  -days 3650 -nodes \
  -subj "/C=US/ST=Demo/L=Demo/O=zCLI/CN=localhost"
```

