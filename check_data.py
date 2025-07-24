#!/usr/bin/env python3
"""
Simple script to check what data we have in the WordPress.org DuckDB database
"""
import duckdb

def main():
    try:
        # Connect to the database
        conn = duckdb.connect('./data/wordpress_data.duckdb')
        print("✅ Connected to WordPress.org data database!")
        
        # Show all tables
        tables = conn.execute("SHOW TABLES").fetchall()
        print(f"\n📊 Available tables ({len(tables)}):")
        for table in tables:
            table_name = table[0]
            count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            print(f"  - {table_name}: {count:,} records")
            
        # Show sample data from each table
        for table in tables:
            table_name = table[0]
            print(f"\n🔍 Sample data from {table_name}:")
            try:
                # Get column names
                columns = conn.execute(f"DESCRIBE {table_name}").fetchall()
                print("   Columns:", [col[0] for col in columns[:5]])  # Show first 5 columns
                
                # Get sample data
                sample = conn.execute(f"SELECT * FROM {table_name} LIMIT 3").fetchall()
                for i, row in enumerate(sample, 1):
                    print(f"   Row {i}: {str(row)[:100]}...")  # Truncate long rows
                    
            except Exception as e:
                print(f"   Error reading {table_name}: {e}")
        
        conn.close()
        print("\n✅ Database exploration complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()