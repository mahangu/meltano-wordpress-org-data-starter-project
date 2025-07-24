#!/usr/bin/env python3
"""
Create sample WordPress.org data directly from the API for testing purposes
"""
import requests
import duckdb
import json
from datetime import datetime

def create_sample_data():
    print("🔄 Creating sample WordPress.org data...")
    
    # Connect to DuckDB
    conn = duckdb.connect('./data/wordpress_data.duckdb')
    
    # Clear existing plugins table to avoid duplicates
    print("🧹 Clearing existing plugin data...")
    conn.execute("DROP TABLE IF EXISTS plugins")
    
    # Create plugins table
    conn.execute("""
        CREATE TABLE plugins (
            slug VARCHAR,
            name VARCHAR,
            short_description TEXT,
            description TEXT,
            version VARCHAR,
            author VARCHAR,
            author_profile VARCHAR,
            contributors JSON,
            requires VARCHAR,
            tested VARCHAR,
            requires_php VARCHAR,
            requires_plugins JSON,
            compatibility JSON,
            rating DOUBLE,
            num_ratings INTEGER,
            support_threads INTEGER,
            support_threads_resolved INTEGER,
            active_installs INTEGER,
            downloaded INTEGER,
            last_updated TIMESTAMP,
            added TIMESTAMP,
            homepage VARCHAR,
            download_link VARCHAR,
            tags JSON,
            stable_tag VARCHAR,
            versions JSON,
            donate_link VARCHAR,
            banners JSON,
            icons JSON,
            blocks JSON,
            block_assets JSON,
            author_block_count INTEGER,
            author_block_rating INTEGER,
            blueprints JSON,
            preview_link VARCHAR
        )
    """)
    
    # Get some popular plugins from WordPress.org API
    try:
        print("📥 Fetching plugin data from WordPress.org API...")
        
        # Fetch multiple pages to get 500+ plugins for better rating distribution
        all_plugins = []
        per_page = 100
        max_pages = 6  # Will give us 600 plugins
        
        for page in range(1, max_pages + 1):
            print(f"📥 Fetching page {page}/{max_pages} from WordPress.org API...")
            response = requests.get(f"https://api.wordpress.org/plugins/info/1.2/?action=query_plugins&request[browse]=popular&request[per_page]={per_page}&request[page]={page}")
            
            if response.status_code == 200:
                data = response.json()
                page_plugins = data.get('plugins', [])
                all_plugins.extend(page_plugins)
                print(f"  ✅ Got {len(page_plugins)} plugins from page {page}")
                
                # If we got fewer plugins than requested, we've reached the end
                if len(page_plugins) < per_page:
                    print(f"  📄 Reached end of available plugins at page {page}")
                    break
            else:
                print(f"  ❌ Failed to fetch page {page}: {response.status_code}")
                break
        
        plugins = all_plugins
        
        if len(plugins) > 0:
            
            print(f"📦 Found {len(plugins)} plugins to insert...")
            
            for plugin in plugins:
                try:
                    # Convert contributors and tags to JSON strings
                    contributors = json.dumps(plugin.get('contributors', {}))
                    tags = json.dumps(plugin.get('tags', {}))
                    versions = json.dumps(plugin.get('versions', {}))
                    banners = json.dumps(plugin.get('banners', {}))
                    icons = json.dumps(plugin.get('icons', {}))
                    blocks = json.dumps(plugin.get('blocks', {}))
                    block_assets = json.dumps(plugin.get('block_assets', {}))
                    blueprints = json.dumps(plugin.get('blueprints', {}))
                    requires_plugins = json.dumps(plugin.get('requires_plugins', []))
                    compatibility = json.dumps(plugin.get('compatibility', {}))
                    
                    # Parse dates
                    last_updated = None
                    added = None
                    if plugin.get('last_updated'):
                        try:
                            last_updated = datetime.strptime(plugin['last_updated'], '%Y-%m-%d %I:%M%p GMT')
                        except:
                            pass
                    if plugin.get('added'):
                        try:
                            added = datetime.strptime(plugin['added'], '%Y-%m-%d')
                        except:
                            pass
                    
                    # Insert plugin data
                    conn.execute("""
                        INSERT INTO plugins VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        plugin.get('slug'),
                        plugin.get('name'),
                        plugin.get('short_description'),
                        plugin.get('description'),
                        plugin.get('version'),
                        plugin.get('author'),
                        plugin.get('author_profile'),
                        contributors,
                        plugin.get('requires'),
                        plugin.get('tested'),
                        plugin.get('requires_php'),
                        requires_plugins,
                        compatibility,
                        float(plugin.get('rating', 0)) if plugin.get('rating') else None,
                        int(plugin.get('num_ratings', 0)) if plugin.get('num_ratings') else None,
                        int(plugin.get('support_threads', 0)) if plugin.get('support_threads') else None,
                        int(plugin.get('support_threads_resolved', 0)) if plugin.get('support_threads_resolved') else None,
                        int(plugin.get('active_installs', 0)) if plugin.get('active_installs') else None,
                        int(plugin.get('downloaded', 0)) if plugin.get('downloaded') else None,
                        last_updated,
                        added,
                        plugin.get('homepage'),
                        plugin.get('download_link'),
                        tags,
                        plugin.get('stable_tag'),
                        versions,
                        plugin.get('donate_link'),
                        banners,
                        icons,
                        blocks,
                        block_assets,
                        int(plugin.get('author_block_count', 0)) if plugin.get('author_block_count') else None,
                        int(plugin.get('author_block_rating', 0)) if plugin.get('author_block_rating') else None,
                        blueprints,
                        plugin.get('preview_link')
                    ))
                    
                except Exception as e:
                    print(f"⚠️  Error inserting plugin {plugin.get('slug', 'unknown')}: {e}")
                    continue
            
            # Check how many records we inserted
            count = conn.execute("SELECT COUNT(*) FROM plugins").fetchone()[0]
            print(f"✅ Successfully inserted {count} plugins into the database!")
            
            # Show sample data
            print("\n📊 Sample plugin data:")
            sample = conn.execute("SELECT name, rating, num_ratings, active_installs FROM plugins ORDER BY active_installs DESC LIMIT 5").fetchall()
            for row in sample:
                print(f"  - {row[0]}: Rating {row[1]}, {row[2]} reviews, {row[3]} active installs")
                
        else:
            print("❌ No plugins were fetched from WordPress.org API")
            
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    create_sample_data()