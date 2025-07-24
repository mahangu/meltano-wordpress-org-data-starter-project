# WordPress.org Data Pipeline Makefile

.PHONY: help setup install extract extract-plugins extract-events extract-all \
        check-data clean-data notebook test requirements clean clean-all status config check-uv

# Check if uv is installed
check-uv:
	@command -v uv >/dev/null 2>&1 || { \
		echo "❌ Error: uv is not installed!"; \
		echo ""; \
		echo "Please install uv first:"; \
		echo "  macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		echo "  macOS (Homebrew): brew install uv"; \
		echo "  Windows: powershell -ExecutionPolicy ByPass -c \"irm https://astral.sh/uv/install.ps1 | iex\""; \
		echo "  Alternative: pip install uv"; \
		echo ""; \
		echo "Then restart your terminal and try again."; \
		exit 1; \
	}

# UV command prefix
UV_RUN = uv run

# Default target
help: ## Show this help message
	@echo "WordPress.org Data Pipeline - Available targets:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Setup and Installation
setup: check-uv ## Set up dependencies using uv
	@echo "Setting up project with uv..."
	uv sync
	@echo "✅ Setup complete!"

install: ## Install/reinstall Meltano plugins
	@echo "Installing Meltano plugins..."
	$(UV_RUN) meltano install
	@echo "✅ Plugins installed!"

# Data Extraction
extract: extract-plugins ## Default extract (plugins only)

extract-plugins: ## Extract WordPress plugins data only
	@echo "🔄 Extracting WordPress plugins data..."
	$(UV_RUN) meltano config tap-wordpress-org set stream_selection '["plugins"]'
	$(UV_RUN) meltano el tap-wordpress-org target-duckdb
	@echo "✅ Plugins extraction complete!"

extract-events: ## Extract WordPress events data only
	@echo "🔄 Extracting WordPress events data..."
	$(UV_RUN) meltano config tap-wordpress-org set stream_selection '["events"]'
	$(UV_RUN) meltano el tap-wordpress-org target-duckdb
	@echo "✅ Events extraction complete!"

extract-themes: ## Extract WordPress themes data only
	@echo "🔄 Extracting WordPress themes data..."
	$(UV_RUN) meltano config tap-wordpress-org set stream_selection '["themes"]'
	$(UV_RUN) meltano el tap-wordpress-org target-duckdb
	@echo "✅ Themes extraction complete!"

extract-all: ## Extract all available data streams
	@echo "🔄 Extracting all WordPress.org data streams..."
	$(UV_RUN) meltano config tap-wordpress-org set stream_selection ''
	$(UV_RUN) meltano el tap-wordpress-org target-duckdb
	@echo "✅ Full extraction complete!"

extract-quick: ## Quick extraction with limited data for testing
	@echo "🔄 Running quick extraction (plugins only, limited)..."
	$(UV_RUN) meltano config tap-wordpress-org set stream_selection '["plugins"]'
	@echo "✅ Quick extraction complete!"

sample-data: ## Create sample data from WordPress.org API for testing
	@echo "🔄 Creating sample data from WordPress.org API..."
	$(UV_RUN) python create_sample_data.py
	@echo "✅ Sample data creation complete!"

# Data Management and Analysis
check-data: ## Check what data is in the database
	@echo "📊 Checking database contents..."
	$(UV_RUN) python check_data.py

notebook: ## Start Jupyter notebook with the analysis notebook open
	@echo "📓 Starting Jupyter notebook with analysis notebook..."
	$(UV_RUN) jupyter notebook notebook/wordpress_org_data_analysis.ipynb

# Configuration and Status
config: ## Show current Meltano configuration
	@echo "⚙️  Current Meltano configuration:"
	$(UV_RUN) meltano config list

status: ## Show project status and installed plugins
	@echo "📋 Project Status:"
	@echo "Python version: $$(python3 --version)"
	@echo "UV virtual environment: $$(if [ -d .venv ]; then echo '✅ Exists'; else echo '❌ Missing'; fi)"
	@if [ -f ./data/wordpress_data.duckdb ]; then \
		echo "Database file: ✅ Exists ($$(du -h ./data/wordpress_data.duckdb | cut -f1))"; \
	else \
		echo "Database file: ❌ Missing"; \
	fi
	@echo ""
	@echo "📊 Data Summary:"
	@$(UV_RUN) python3 -c "import duckdb; conn = duckdb.connect('./data/wordpress_data.duckdb'); tables = conn.execute('SHOW TABLES').fetchall(); print(f'Tables: {len(tables)}'); [print(f'  - {t[0]}: {conn.execute(f\"SELECT COUNT(*) FROM {t[0]}\").fetchone()[0]:,} records') for t in tables]; conn.close()" 2>/dev/null || echo "  No data available"
	@echo ""
	@echo "Installed plugins:"
	@echo "  - tap-wordpress-org (WordPress.org extractor)"
	@echo "  - target-duckdb (DuckDB loader)"

# Testing
test: ## Run basic tests to verify setup
	@echo "🧪 Running tests..."
	@echo "1. Checking UV virtual environment..."
	@test -d .venv && echo "✅ UV virtual environment exists" || (echo "❌ UV virtual environment missing" && exit 1)
	@echo "2. Checking Meltano installation..."
	@$(UV_RUN) meltano --version > /dev/null && echo "✅ Meltano installed" || (echo "❌ Meltano not installed" && exit 1)
	@echo "3. Checking DuckDB installation..."
	@$(UV_RUN) python3 -c "import duckdb; print('✅ DuckDB available')" || (echo "❌ DuckDB not installed" && exit 1)
	@echo "✅ All tests passed!"

# Maintenance and Cleanup
clean-data: ## Remove extracted data (keeps database structure)
	@echo "🧹 Cleaning extracted data..."
	@if [ -f ./data/wordpress_data.duckdb ]; then \
		$(UV_RUN) python3 -c "import duckdb; conn = duckdb.connect('./data/wordpress_data.duckdb'); tables = [t[0] for t in conn.execute('SHOW TABLES').fetchall()]; [conn.execute(f'DELETE FROM {table}') for table in tables]; conn.close(); print('✅ Data cleaned')"; \
	else \
		echo "No database file found"; \
	fi

clean-db: ## Remove database files completely
	@echo "🧹 Removing database files..."
	rm -f ./data/wordpress_data.duckdb*
	@echo "✅ Database files removed!"

clean: ## Clean cache and temporary files
	@echo "🧹 Cleaning temporary files..."
	rm -rf .meltano/run/
	rm -rf notebook/.ipynb_checkpoints/
	@echo "✅ General cleanup complete!"

clean-all: clean-db clean ## Remove all data and cache (complete reset)
	@echo "🧹 Complete cleanup performed!"

# Development
requirements: ## Generate requirements.txt file (for compatibility)
	@echo "📝 Generating requirements.txt from uv.lock..."
	uv export --format requirements-txt > requirements.txt
	@echo "✅ requirements.txt generated from uv.lock!"

# Quick start for new users
quickstart: check-uv install sample-data check-data notebook ## Complete quickstart: install, create sample data, check results, and launch notebook
	@echo ""
	@echo "🎉 Quickstart complete! Your WordPress.org data pipeline is ready and Jupyter notebook is starting..."
	@echo ""
	@echo "Other available commands:"
	@echo "  make extract-all    # Extract all data (takes longer)"
	@echo "  make help          # See all available commands"