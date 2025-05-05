#!/usr/bin/env python

import sys
import psycopg2
import json

# Try to connect directly to the Redash database to add a data source
try:
    # Connect to the Redash PostgreSQL database
    conn = psycopg2.connect(
        host="postgres",
        port=5432,
        user="postgres",
        password="postgres",
        dbname="postgres"
    )
    
    print("Connected to Redash database")
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Check if we already have a data source with this name
    cursor.execute("SELECT id FROM data_sources WHERE name = 'Aiven PostgreSQL'")
    result = cursor.fetchone()
    
    # Data source configuration
    options = {
        "dbname": "defaultdb",
        "host": "pg-2c599df7-glazertech1-225a.h.aivencloud.com",
        "port": 19346,
        "user": "readonly_users",
        "password": "StrongReadOnlyPassword123",
        "sslmode": "require"
    }
    
    if result:
        # Update existing data source
        ds_id = result[0]
        print(f"Updating existing data source with ID {ds_id}")
        cursor.execute(
            "UPDATE data_sources SET options = %s WHERE id = %s",
            (json.dumps(options), ds_id)
        )
        print(f"Updated data source with ID {ds_id}")
    else:
        # Create new data source
        print("Creating new data source")
        cursor.execute(
            """
            INSERT INTO data_sources (name, type, options, created_at)
            VALUES ('Aiven PostgreSQL', 'pg', %s, now())
            RETURNING id
            """,
            (json.dumps(options),)
        )
        ds_id = cursor.fetchone()[0]
        print(f"Created data source with ID {ds_id}")
    
    # Close connection
    cursor.close()
    conn.close()
    
    print("Done!")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1) 