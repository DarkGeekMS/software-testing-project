#!/bin/bash
# This script resets all used ports in case of failure

# back ports
sudo fuser -k 5557/tcp
sudo fuser -k 5560/tcp
sudo fuser -k 5561/tcp
sudo fuser -k 5562/tcp
sudo fuser -k 5563/tcp

#common ports
sudo fuser -k 5570/tcp
sudo fuser -k 5571/tcp
sudo fuser -k 5572/tcp
sudo fuser -k 5573/tcp

#front ports
sudo fuser -k 5578/tcp