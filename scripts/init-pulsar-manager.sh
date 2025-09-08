#!/bin/bash

# Wait for pulsar-manager to be ready
# echo "Waiting for pulsar-manager to be ready..."
# until curl -f http://broker-manager:7750 > /dev/null 2>&1; do
#     echo "Pulsar Manager not ready yet, waiting..."
#     sleep 5
# done

echo "Pulsar Manager is ready, creating user..."

# Get CSRF token
echo "Getting CSRF token..."
CSRF_TOKEN=$(curl http://localhost:7750/pulsar-manager/csrf-token)

# Create user in pulsar-manager
echo "Creating user with CSRF token..."
curl -X PUT \
  http://localhost:7750/pulsar-manager/users/superuser \
  -H "X-XSRF-TOKEN: $CSRF_TOKEN" \
  -H "Cookie: XSRF-TOKEN=$CSRF_TOKEN;" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "admin",
    "password": "apachepulsar",
    "description": "Administrator user",
    "email": "admin@example.com"
  }'

echo "User created successfully!"