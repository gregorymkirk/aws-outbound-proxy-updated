#!/bin/bash
# update allowed domains for squid proxy
# © Copyright 2021 McAfee, Corp.

set -e

#read allowed domains from disk and append to cloudformation parameters
echo "Getting allowed domains..."
allowedDomains=$(cat ../source/allowed.domains.txt | tr -d " " | tr "\n" ",")
echo "Allowed domains: "$allowedDomains

#update secret
echo "Updating secret..."
aws secretsmanager put-secret-value --secret-id squid-proxy-allow-domain-list --secret-string $allowedDomains --output table