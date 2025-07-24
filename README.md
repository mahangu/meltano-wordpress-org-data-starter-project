# WordPress.org Data Pipeline with Meltano

[![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)](./pyproject.toml)
[![Python](https://img.shields.io/badge/python-3.11+-brightgreen.svg)](https://python.org)
[![uv](https://img.shields.io/badge/uv-dependency_manager-orange.svg)](https://docs.astral.sh/uv/)

A complete data pipeline that extracts data from the WordPress.org API using Meltano, stores it in DuckDB for fast analytics, and provides interactive analysis through Jupyter notebooks.

**🚀 Quick Start**: `make quickstart` - Get up and running in minutes!

> **Note**: This project requires `uv` to be installed. If you see "uv: command not found", please follow the installation instructions below.

## Overview

The pipeline extracts data from WordPress.org including:
- **Plugins**: Plugin information, ratings, download counts, etc.
- **Events**: WordPress community events
- **Themes**: WordPress theme data
- **Stats**: Various WordPress.org statistics

## Project Structure

```
meltano-wordpress-org-data-starter-project/
├── data/                           # DuckDB database files
│   └── wordpress_data.duckdb       # Main database file
├── notebook/                       # Jupyter notebooks
│   └── wordpress_org_data_analysis.ipynb  # Data analysis notebook
├── analyze/                        # Analysis scripts
├── extract/                        # Extract configurations
├── load/                          # Load configurations
├── transform/                     # Transform configurations
├── orchestrate/                   # Orchestration configurations
├── plugins/                       # Meltano plugin configurations
├── meltano.yml                    # Meltano configuration
├── pyproject.toml                 # Python project configuration
├── uv.lock                        # Dependency lock file
├── check_data.py                  # Utility script to inspect data
├── create_sample_data.py          # Create sample data for testing
├── Makefile                       # Build and utility commands
└── README.md                      # This file
```

## Getting Started

### Prerequisites

- Python 3.11+
- **[uv](https://docs.astral.sh/uv/) (REQUIRED)** - Fast Python package manager

### Installation

1. **Install uv** (required):
   
   **macOS/Linux:**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
   
   **macOS (Homebrew):**
   ```bash
   brew install uv
   ```
   
   **Windows:**
   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```
   
   **Alternative (any platform):**
   ```bash
   pip install uv
   ```

2. **Verify uv installation:**
   ```bash
   uv --version
   ```

3. **Clone and navigate to the project:**
   ```bash
   git clone https://github.com/mahangu/meltano-wordpress-org-data-starter-project.git
   cd meltano-wordpress-org-data-starter-project
   ```

4. **Install dependencies and create virtual environment:**
   ```bash
   uv sync
   ```

5. **Verify project installation:**
   ```bash
   uv run meltano --version
   ```

### Running the Data Pipeline

**Using Make (Recommended):**
```bash
# See all available commands
make help

# Quick start (install plugins, extract sample data, check results)
make quickstart

# Extract specific data streams
make extract-plugins    # WordPress plugins only
make extract-events     # WordPress events only  
make extract-themes     # WordPress themes only
make extract-all        # All available data streams

# Check what data you have
make check-data

# Start Jupyter notebook for analysis
make notebook
```

**Using Meltano directly:**
```bash
# Extract and load data from WordPress.org
uv run meltano el tap-wordpress-org target-duckdb

# Check extracted data
uv run python check_data.py
```

### Data Analysis

1. **Start Jupyter notebook:**
   ```bash
   uv run jupyter notebook
   ```

2. **Open the analysis notebook:**
   Navigate to `notebook/wordpress_org_data_analysis.ipynb`

3. **Run the notebook cells** to explore the WordPress.org data and create visualizations

## Makefile Commands

This project includes a comprehensive Makefile with convenient targets:

| Command | Description |
|---------|-------------|
| `make help` | Show all available commands |
| `make quickstart` | Complete setup: install plugins, extract sample data, check results |
| `make extract-plugins` | Extract WordPress plugins data only |
| `make extract-events` | Extract WordPress events data only |
| `make extract-themes` | Extract WordPress themes data only |
| `make extract-all` | Extract all available data streams |
| `make sample-data` | Create sample data from WordPress.org API for testing |
| `make check-data` | Check what data is in the database |
| `make notebook` | Start Jupyter notebook with the analysis notebook open |
| `make status` | Show project status and installed plugins |
| `make test` | Run basic tests to verify setup |
| `make clean-data` | Remove extracted data (keeps database structure) |
| `make clean-db` | Remove database files completely |

**Examples:**
```bash
# Quick start for new users
make quickstart

# Create sample data for testing
make sample-data

# Extract live data from WordPress.org
make extract-plugins

# Check what you have
make check-data

# Start analysis
make notebook
```

## Configuration

### Extracting Specific Streams

You can configure which data streams to extract:

```bash
# Extract only plugins data
uv run meltano config tap-wordpress-org set stream_selection '["plugins"]'

# Extract plugins and events
uv run meltano config tap-wordpress-org set stream_selection '["plugins", "events"]'

# Extract all available streams (default)
uv run meltano config tap-wordpress-org set stream_selection ''
```

### Available Streams

The WordPress.org extractor provides several data streams:
- `plugins` - WordPress plugin information
- `events` - WordPress community events
- `themes` - WordPress theme data
- `stats` - WordPress.org statistics

## Database Schema

The DuckDB database contains tables corresponding to each extracted stream:
- `plugins` - Plugin details, ratings, downloads, etc.
- `events` - Event information, locations, dates
- `stats` - Various WordPress.org metrics

## Example Queries

Here are some interesting queries you can run:

```sql
-- Top 10 most popular plugins
SELECT name, active_installs, rating 
FROM plugins 
WHERE active_installs IS NOT NULL 
ORDER BY active_installs DESC 
LIMIT 10;

-- Plugin rating distribution
SELECT 
    CASE 
        WHEN rating >= 4.5 THEN '4.5-5.0'
        WHEN rating >= 4.0 THEN '4.0-4.4'
        ELSE 'Below 4.0'
    END as rating_range,
    COUNT(*) as plugin_count
FROM plugins 
WHERE rating IS NOT NULL 
GROUP BY rating_range;
```

## Troubleshooting

### No Data in Database
If the database appears empty:
1. Check that the extraction completed successfully
2. Verify the target-duckdb configuration
3. Check the logs for any errors

### Slow Extraction
The WordPress.org API has rate limits. Large extractions may take time:
- Use stream selection to focus on specific data
- Consider running extractions during off-peak hours

## Next Steps

1. **Add Transformations**: Use dbt with Meltano to transform your raw data
2. **Create Dashboards**: Build visualizations with tools like Streamlit or Grafana
3. **Add More Sources**: Combine with other data sources for richer analysis
4. **Automate**: Set up CI/CD pipelines for regular data updates

## Links

- [Meltano Documentation](https://docs.meltano.com/)
- [WordPress.org API](https://codex.wordpress.org/WordPress.org_API)
- [DuckDB Documentation](https://duckdb.org/docs/)
- [tap-wordpress-org on GitHub](https://github.com/Automattic/tap-wordpress-org)
- [uv Documentation](https://docs.astral.sh/uv/)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Meltano](https://meltano.com/) for the excellent ELT framework
- [Automattic](https://automattic.com/) for the WordPress.org tap
- [DuckDB](https://duckdb.org/) for the fast analytical database
- [WordPress.org](https://wordpress.org/) for providing the API
- [uv](https://github.com/astral-sh/uv) for fast Python dependency management