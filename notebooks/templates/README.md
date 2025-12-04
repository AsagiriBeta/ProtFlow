# Notebook Initialization Templates

This directory contains reusable templates for notebook initialization cells.

## Usage

Copy the appropriate template cell to the beginning of your notebook.

## Available Templates

### 1. `esm3_notebook_init.py`
For notebooks that use ESM3 for protein structure prediction.

### 2. `analysis_notebook_init.py`
For notebooks that perform analysis and visualization.

### 3. `conda_tool_notebook_init.py`
For notebooks that use conda-based tools (Prokka, antiSMASH, etc.)

## Template Structure

Each template follows this structure:
1. Install/check protflow package
2. Import notebook utilities
3. Setup environment and paths
4. Check and install dependencies
5. Print environment info

## Example

```python
# At the start of a notebook, add:
%run templates/esm3_notebook_init.py
```

Or copy the content directly into a cell.
