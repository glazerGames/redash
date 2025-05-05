#!/usr/bin/env python

import psycopg2
import sys

def test_connection(sslmode):
    try:
        conn = psycopg2.connect(
            host='pg-2c599df7-glazertech1-225a.h.aivencloud.com',
            port=19346,
            user='readonly_users',
            password='StrongReadOnlyPassword123',
            dbname='defaultdb',
            sslmode=sslmode
        )
        print(f"Connection successful with sslmode={sslmode}")
        
        # Test a simple query
        cur = conn.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        print(f"Query result: {result}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"Error with sslmode={sslmode}: {e}")
        return False

# Try different SSL modes
modes = ['require', 'prefer', 'allow', 'disable']
for mode in modes:
    print(f"\nTesting with sslmode={mode}:")
    test_connection(mode) 