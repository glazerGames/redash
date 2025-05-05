#!/usr/bin/env python

import psycopg2
import sys

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
    cursor = conn.cursor()
    
    # Get column names for the data_sources table
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'data_sources'
        ORDER BY ordinal_position
    """)
    
    print("\nColumns in data_sources table:")
    for column in cursor.fetchall():
        print(f"  {column[0]} ({column[1]})")
    
    # Get a sample data_source record
    cursor.execute("SELECT * FROM data_sources LIMIT 1")
    row = cursor.fetchone()
    
    if row:
        print("\nSample data_source record:")
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'data_sources' ORDER BY ordinal_position")
        columns = [col[0] for col in cursor.fetchall()]
        
        for i, column_name in enumerate(columns):
            if i < len(row):
                print(f"  {column_name}: {row[i]}")
    else:
        print("\nNo data_source records found")
    
    # Close connection
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1) 