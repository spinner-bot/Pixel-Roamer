"""Compatibility entry point for the expanded Grand Journey route audit."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.audit_grand_routes import main, run

if __name__ == '__main__':
    main()
