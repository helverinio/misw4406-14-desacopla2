# Troubleshooting Guide

## Docker Build Issues

### Issue: `uv.lock` not found
**Error**: `error: Unable to find lockfile at uv.lock`

**Solution**:
```bash
# Generate the lock file
uv lock

# Then rebuild
docker build -t saga-orchestrator .
```

### Issue: Version attribute obsolete
**Error**: `the attribute 'version' is obsolete`

**Solution**: Remove the `version:` line from docker-compose files (already fixed).

### Issue: Dependencies not installing
**Error**: Various dependency installation errors

**Solution**:
1. Make sure `uv.lock` exists
2. Check that all dependencies in `pyproject.toml` are valid
3. Try rebuilding with `--no-cache`:
   ```bash
   docker build --no-cache -t saga-orchestrator .
   ```

## Runtime Issues

### Issue: Cannot connect to PostgreSQL
**Error**: Connection refused to PostgreSQL

**Solution**:
1. Check if PostgreSQL container is running:
   ```bash
   docker ps | grep postgres
   ```
2. Check PostgreSQL logs:
   ```bash
   docker logs saga-postgres-dev
   ```
3. Wait for PostgreSQL to be ready:
   ```bash
   docker exec saga-postgres-dev pg_isready -U postgres
   ```

### Issue: Cannot connect to Pulsar
**Error**: Connection refused to Pulsar broker

**Solution**:
1. Check if Pulsar container is running:
   ```bash
   docker ps | grep pulsar
   ```
2. Check Pulsar health:
   ```bash
   docker exec saga-pulsar-dev bin/pulsar-admin brokers healthcheck
   ```
3. Check Pulsar logs:
   ```bash
   docker logs saga-pulsar-dev
   ```

### Issue: Health check failing
**Error**: Health check endpoint returns 500 or connection refused

**Solution**:
1. Check application logs:
   ```bash
   docker logs saga-orchestrator
   ```
2. Check if all dependencies are available:
   - PostgreSQL connection
   - Pulsar connection
3. Test health endpoint manually:
   ```bash
   curl http://localhost:5003/health
   ```

## Development Issues

### Issue: Port already in use
**Error**: Port 5003 (or others) already in use

**Solution**:
1. Check what's using the port:
   ```bash
   netstat -ano | findstr :5003
   ```
2. Stop the conflicting service or change ports in docker-compose

### Issue: Permission denied
**Error**: Permission denied when running scripts

**Solution**:
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Or run with bash directly
bash scripts/start-dev-environment.sh
```

## Testing and Debugging

### Quick Health Check
```bash
# Test all components
make status

# Test specific service
curl http://localhost:5003/health
curl http://localhost:8081/admin/v2/brokers/health
```

### View Logs
```bash
# All services
make logs

# Specific service
docker logs saga-orchestrator
docker logs saga-postgres-dev
docker logs saga-pulsar-dev
```

### Clean Reset
```bash
# Stop everything and clean up
make clean

# Start fresh
make dev-up
```

## Common Commands

### Development Workflow
```bash
# Start infrastructure only
make dev-up

# Run orchestrator locally
make run

# In another terminal, monitor events
make monitor

# Stop when done
make dev-down
```

### Full Docker Workflow
```bash
# Start everything in containers
make simple-up

# Check status
docker-compose -f docker-compose.simple.yml ps

# View logs
docker-compose -f docker-compose.simple.yml logs -f

# Stop everything
make simple-down
```

### Testing
```bash
# Run integration tests
make test

# Test Docker build
python scripts/test_docker_build.py
```

## Environment Variables

Make sure these are set correctly:

```bash
# For local development
export BROKER_URL=pulsar://localhost:6650
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/saga_db
export INTEGRACIONES_API_URL=http://localhost:5001
export ALIANZAS_API_URL=http://localhost:5002

# For Docker containers (set in docker-compose)
BROKER_URL=pulsar://pulsar:6650
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/saga_db
```

## Getting Help

1. Check service status: `make status`
2. View logs: `make logs`
3. Run health checks: `curl http://localhost:5003/health`
4. Test integration: `make test`
5. Clean and restart: `make clean && make dev-up`
