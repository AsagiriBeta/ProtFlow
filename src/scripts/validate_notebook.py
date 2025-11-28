#!/usr/bin/env python3
"""
Test script to validate ProtFlow notebook for Colab compatibility.
"""

import json
import sys
from pathlib import Path


def validate_notebook(notebook_path):
    """Validate notebook structure and content."""
    print(f"🔍 Validating {notebook_path}...")

    errors = []
    warnings = []

    try:
        with open(notebook_path) as f:
            nb = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False

    # Check required fields
    if 'cells' not in nb:
        errors.append("Missing 'cells' field")

    if 'metadata' not in nb:
        warnings.append("Missing 'metadata' field")

    # Check cells
    cells = nb.get('cells', [])
    print(f"   Found {len(cells)} cells")

    # Count cell types
    code_cells = sum(1 for c in cells if c.get('cell_type') == 'code')
    markdown_cells = sum(1 for c in cells if c.get('cell_type') == 'markdown')

    print(f"   Code cells: {code_cells}")
    print(f"   Markdown cells: {markdown_cells}")

    # Check for critical cells
    critical_keywords = [
        'git clone',
        'pip install',
        'huggingface_hub',
        'extract_proteins_from_gbk',
        'load_esm3_small',
        'ensure_p2rank',
        'smiles_or_file_to_pdbqt',
        'run_vina',
        'build_report'
    ]

    found_keywords = {kw: False for kw in critical_keywords}

    for cell in cells:
        if cell.get('cell_type') == 'code':
            source = ''.join(cell.get('source', []))
            for kw in critical_keywords:
                if kw in source:
                    found_keywords[kw] = True

    print("\n   Critical components:")
    for kw, found in found_keywords.items():
        status = "✅" if found else "❌"
        print(f"   {status} {kw}")
        if not found:
            warnings.append(f"Missing keyword: {kw}")

    # Check for common issues
    for i, cell in enumerate(cells):
        if cell.get('cell_type') == 'code':
            source = ''.join(cell.get('source', []))

            # Check for problematic patterns
            if 'import *' in source:
                warnings.append(f"Cell {i}: Uses wildcard import")

            # Check for hardcoded paths
            if '/home/' in source or '/Users/' in source:
                if '/content' not in source:  # Allow /content for Colab
                    warnings.append(f"Cell {i}: Contains hardcoded local path")

    # Check metadata for Colab
    metadata = nb.get('metadata', {})
    if 'colab' in metadata:
        print("\n   ✅ Colab metadata present")
        colab_meta = metadata['colab']
        if 'gpuType' in colab_meta:
            print(f"   GPU type: {colab_meta['gpuType']}")
    else:
        warnings.append("No Colab metadata (will still work)")

    if 'accelerator' in metadata:
        print(f"   Accelerator: {metadata['accelerator']}")

    # Summary
    print("\n" + "=" * 60)
    if errors:
        print("❌ ERRORS:")
        for err in errors:
            print(f"   - {err}")

    if warnings:
        print("⚠️  WARNINGS:")
        for warn in warnings:
            print(f"   - {warn}")

    if not errors:
        if warnings:
            print("✅ Notebook is valid with warnings")
            return True
        else:
            print("✅ Notebook is valid and ready for Colab!")
            return True
    else:
        print("❌ Notebook has errors")
        return False


def check_imports():
    """Check if critical imports are available."""
    print("\n🔍 Checking Python environment...")

    critical_modules = [
        'pathlib',
        'json',
        'sys',
        'subprocess',
    ]

    optional_modules = [
        'torch',
        'esm',
        'Bio',
        'pandas',
        'reportlab',
        'py3Dmol'
    ]

    print("\n   Critical modules:")
    all_critical = True
    for mod in critical_modules:
        try:
            __import__(mod)
            print(f"   ✅ {mod}")
        except ImportError:
            print(f"   ❌ {mod}")
            all_critical = False

    print("\n   Optional modules (for running the pipeline):")
    for mod in optional_modules:
        try:
            __import__(mod)
            print(f"   ✅ {mod}")
        except ImportError:
            print(f"   ⚠️  {mod} (not installed)")

    return all_critical


def main():
    """Main validation routine."""
    print("=" * 60)
    print("ProtFlow Notebook Validator")
    print("=" * 60)

    # Find notebook
    repo_root = Path(__file__).parent.parent
    notebook_path = repo_root / 'ProtFlow.ipynb'

    if not notebook_path.exists():
        print(f"❌ Notebook not found: {notebook_path}")
        return 1

    # Validate notebook
    nb_valid = validate_notebook(notebook_path)

    # Check environment
    env_valid = check_imports()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if nb_valid and env_valid:
        print("✅ All checks passed!")
        print("   The notebook is ready for use on Google Colab.")
        return 0
    elif nb_valid and not env_valid:
        print("⚠️  Notebook is valid but some modules are missing")
        print("   This is OK - they will be installed in the notebook")
        return 0
    else:
        print("❌ Validation failed")
        print("   Please fix the errors above")
        return 1


if __name__ == '__main__':
    sys.exit(main())

