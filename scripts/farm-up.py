#!/usr/bin/env python

# Import all required libs
import sys, json, pipes, os, subprocess, time, re

# Fetch a list of all farm-roles
data = json.loads(subprocess.check_output(["szradm", "queryenv", "--format=json", "list-roles"]))

# Check if all instances are up
for role in data["roles"]:
    if int(role["scaling-min-instances"]) != len(role["hosts"]):
        quit()

# Fire FarmUp event
subprocess.call(["szradm", "fire-event", "FarmUp"])
