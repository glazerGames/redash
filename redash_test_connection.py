#!/usr/bin/env python

import psycopg2
import json
import sys

def test_connection(connection_params):
    """
    Test a PostgreSQL connection using the provided parameters
    """
    try:
        print(f"Connecting with parameters: {connection_params}")
        
        # Extract parameters
        user = connection_params.get("user")
        password = connection_params.get("password")
        host = connection_params.get("host")  
        port = connection_params.get("port", 19346)
        dbname = connection_params.get("dbname")
        sslmode = connection_params.get("sslmode", "require")
        
        # Connect with specified parameters
        conn_string = f"host={host} port={port} user={user} password={password} dbname={dbname} sslmode={sslmode}"
        print(f"Connection string: {conn_string}")
        
        conn = psycopg2.connect(conn_string)
        
        # Test query
        cur = conn.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        print(f"Query result: {result}")
        
        # Close connection
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error connecting: {e}")
        return False

# Parameters for Aiven PostgreSQL - adjust as needed
params = {
    "user": "readonly_users",
    "password": "StrongReadOnlyPassword123",
    "host": "pg-2c599df7-glazertech1-225a.h.aivencloud.com",
    "port": 19346,
    "dbname": "defaultdb",
    "sslmode": "require"
}

# Test connection
success = test_connection(params)
print(f"Connection test {'succeeded' if success else 'failed'}")

# If you want to test different SSL modes
for mode in ["require", "prefer", "allow", "disable"]:
    params["sslmode"] = mode
    print(f"\nTesting with sslmode={mode}:")
    success = test_connection(params) 