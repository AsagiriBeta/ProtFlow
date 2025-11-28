#!/usr/bin/env python3
"""
Configuration validator for ProtFlow.
Validates JSON configuration files and checks directory structure.
"""

import json
import os
import sys
from pathlib import Path

def validate_config(config_path):
    """Validate a ProtFlow configuration file."""
    
    print(f"Validating configuration: {config_path}")
    
    # Load configuration
    try:
        with open(config_path, 'r') as f:
            # Remove comments (lines starting with #)
            lines = [line for line in f if not line.strip().startswith('#') and line.strip()]
            config = json.loads(''.join(lines))
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading config file: {e}")
        return False
    
    # Required fields
    required_fields = [
        'base_dir', 'data_dir', 'src_dir', 'notebooks_dir',
        'input_sequences_dir', 'input_structures_dir', 'input_annotations_dir',
        'predictions_dir', 'structures_dir', 'logs_dir', 'cache_dir', 'temp_dir'
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in config:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"❌ Missing required fields: {', '.join(missing_fields)}")
        return False
    
    # Validate directory structure
    base_path = Path(config_path).parent.parent
    
    print("\n📁 Checking directory structure:")
    
    # Check core directories
    core_dirs = ['base_dir', 'data_dir', 'src_dir', 'notebooks_dir']
    for dir_key in core_dirs:
        dir_path = base_path / config[dir_key].lstrip('./')
        if dir_path.exists():
            print(f"✅ {dir_key}: {dir_path}")
        else:
            print(f"⚠️  {dir_key}: {dir_path} (will be created)")
    
    # Check input subdirectories
    print("\n📂 Input directories:")
    input_dirs = ['input_sequences_dir', 'input_structures_dir', 'input_annotations_dir']
    for dir_key in input_dirs:
        dir_path = base_path / config[dir_key].lstrip('./')
        if dir_path.exists():
            print(f"✅ {dir_key}: {dir_path}")
        else:
            print(f"⚠️  {dir_key}: {dir_path} (will be created)")
    
    # Check output subdirectories
    print("\n📂 Output directories:")
    output_dirs = ['predictions_dir', 'structures_dir', 'logs_dir', 'cache_dir', 'temp_dir']
    for dir_key in output_dirs:
        dir_path = base_path / config[dir_key].lstrip('./')
        if dir_path.exists():
            print(f"✅ {dir_key}: {dir_path}")
        else:
            print(f"⚠️  {dir_key}: {dir_path} (will be created)")
    
    # Validate numerical values
    print("\n🔢 Validating numerical settings:")
    
    numerical_checks = [
        ('min_seq_length', 1, 1000),
        ('max_seq_length', 10, 5000),
        ('max_sequences', 1, 10000),
        ('esm3_num_steps', 1, 100),
        ('vina_box_size', 1, 100),
        ('vina_exhaustiveness', 1, 32),
        ('max_workers', 1, 64),
        ('batch_size', 1, 100)
    ]
    
    for field, min_val, max_val in numerical_checks:
        if field in config:
            value = config[field]
            if isinstance(value, (int, float)) and min_val <= value <= max_val:
                print(f"✅ {field}: {value}")
            else:
                print(f"❌ {field}: {value} (should be between {min_val} and {max_val})")
                return False
    
    # Validate CUDA settings
    print("\n🚀 CUDA configuration:")
    if 'cuda_version' in config:
        cuda_version = config['cuda_version']
        print(f"✅ CUDA version: {cuda_version}")
        
        if 'gpu_memory_fraction' in config:
            frac = config['gpu_memory_fraction']
            if 0.1 <= frac <= 1.0:
                print(f"✅ GPU memory fraction: {frac}")
            else:
                print(f"❌ GPU memory fraction: {frac} (should be 0.1-1.0)")
                return False
    
    # Validate paths
    print("\n🔧 Tool paths:")
    tool_paths = ['p2rank_path', 'vina_path', 'antismash_path', 'foldseek_path']
    for path_key in tool_paths:
        if path_key in config and config[path_key]:
            tool_path = Path(config[path_key])
            if tool_path.exists():
                print(f"✅ {path_key}: {tool_path}")
            else:
                print(f"⚠️  {path_key}: {tool_path} (not found, will use system PATH)")
    
    print(f"\n✅ Configuration validation completed successfully!")
    return True

def create_directories(config_path):
    """Create missing directories based on configuration."""
    
    print(f"\n📂 Creating directories for: {config_path}")
    
    try:
        with open(config_path, 'r') as f:
            lines = [line for line in f if not line.strip().startswith('#') and line.strip()]
            config = json.loads(''.join(lines))
    except Exception as e:
        print(f"❌ Error reading config file: {e}")
        return False
    
    base_path = Path(config_path).parent.parent
    created_count = 0
    
    # Get all directory paths from config
    dir_keys = [key for key in config.keys() if 'dir' in key and key != 'scripts_dir']
    
    for dir_key in dir_keys:
        dir_path = base_path / config[dir_key].lstrip('./')
        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created: {dir_path}")
            created_count += 1
        except Exception as e:
            print(f"❌ Failed to create {dir_path}: {e}")
    
    print(f"\n✅ Created {created_count} directories")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_config.py <config_file> [--create-dirs]")
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    if not os.path.exists(config_file):
        print(f"❌ Config file not found: {config_file}")
        sys.exit(1)
    
    # Validate configuration
    is_valid = validate_config(config_file)
    
    # Create directories if requested
    if '--create-dirs' in sys.argv:
        create_directories(config_file)
    
    sys.exit(0 if is_valid else 1)