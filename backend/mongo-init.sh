#!/bin/bash
set -e

# Start mongod in background (MONGOD_EXTRA_ARGS can be set via environment)
mongod --replSet rs0 --bind_ip_all ${MONGOD_EXTRA_ARGS} &
MONGOD_PID=$!

# Wait for mongod to be ready
until mongosh --eval "db.adminCommand({ping:1})" --quiet 2>/dev/null; do
  sleep 1
done

# Initiate replica set (ignore if already initiated)
mongosh --eval 'try { rs.status() } catch(e) { rs.initiate({_id:"rs0", members:[{_id:0, host:"mongodb:27017"}]}) }' --quiet || true

# Keep mongod in foreground
wait $MONGOD_PID
