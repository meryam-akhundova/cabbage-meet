"""
Test suite for init_db.py
Run with: pytest test_init_db.py -v --cov=src.backend.init_db
"""

import pytest
import subprocess
import sys
from pathlib import Path


class TestInitDbScript:
    def test_module_imports(self):
        """Test that the module can be imported"""
        import src.backend.init_db
        assert src.backend.init_db is not None
    
    def test_script_execution(self, tmp_path, monkeypatch):
        """Test running the script as main"""
        # Create a test database path
        db_path = tmp_path / "test.db"
        
        # Run the script as a subprocess
        result = subprocess.run(
            [sys.executable, '-m', 'src.backend.init_db'],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        
        # Check it ran successfully
        assert result.returncode == 0
        assert "Initializing CabbageMeet database" in result.stdout
        assert "Database initialized successfully" in result.stdout
    
    def test_init_db_is_imported(self):
        """Test that init_db function is imported from database module"""
        from src.backend.init_db import init_db
        assert callable(init_db)