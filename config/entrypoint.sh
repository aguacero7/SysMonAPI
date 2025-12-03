#!/bin/bash
set -e
sysctl -w net.ipv4.ip_forward=1
sysctl -w net.ipv6.conf.all.forwarding=0

mkdir -p /var/log/supervisor
mkdir -p /var/run/frr
mkdir -p /var/log/frr
mkdir -p /var/log/chrony
mkdir -p /var/lib/chrony


chown -R frr:frr /var/log/frr /var/run/frr /etc/frr
chmod 755 /etc/frr
if [ -f /etc/frr/frr.conf ]; then
    chmod 640 /etc/frr/frr.conf
    chown frr:frr /etc/frr/frr.conf
fi
if [ -f /etc/frr/vtysh.conf ]; then
    chmod 640 /etc/frr/vtysh.conf
    chown frr:frrvty /etc/frr/vtysh.conf
fi

chown -R _chrony:_chrony /var/lib/chrony /var/log/chrony 2>/dev/null || \
    chown -R chrony:chrony /var/lib/chrony /var/log/chrony 2>/dev/null || true

if command -v vtysh &> /dev/null; then
    echo "Testing FRR configuration..."
    vtysh -d -C || echo "Warning: FRR configuration check failed (this is normal during first build)"
fi

echo "Network interfaces:"
ip addr show

echo "Network routes:"
ip route show

# executer supervisord
exec "$@"
