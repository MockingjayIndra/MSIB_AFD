#!/bin/sh

ssh-add ./id_ed25519
ssh root@139.59.99.85 -i id_ed25519
