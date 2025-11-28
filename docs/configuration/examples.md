# Configuration Usage Examples

This document provides practical examples of how to use the updated ProtFlow configuration files.

## Quick Start

### 1. Basic Usage with Default Config
```bash
# Copy the example config to create your own
cp config/config.example.json config.json

# Run ProtFlow with default configuration
python -m protflow.main --input data/sequences/protein.fasta
```

### 2. Using Custom Configuration
```bash
# Use a specific configuration file
python -m protflow.main --config config/my_config.json --input data/sequences/protein.fasta

# Override specific settings from command line
python -m protflow.main --config config.json --esm3_num_steps 12 --max_sequences 50
```

### 3. Environment-Specific Configurations

#### Development Environment
```bash
# Use development config with debug mode
python -m protflow.main --config config.example.json --debug_mode true --log_level DEBUG
```

#### Production Environment (CUDA 13)
```bash
# Use server-optimized configuration
python -m protflow.main --config config/config.server.json --input data/sequences/batch.fasta
```

## Configuration Scenarios

### Scenario 1: Small Protein Analysis (Single GPU)
```json
{
  "base_dir": "./outputs",
  "data_dir": "./data",
  "esm3_model": "esm3-sm-open-v1",
  "esm3_num_steps": 8,
  "esm3_device": "cuda",
  "esm3_precision": "bf16",
  "max_sequences": 10,
  "max_seq_length": 500,
  "parallel_predictions": false,
  "max_workers": 4,
  "visible_devices": "0",
  "gpu_memory_fraction": 0.8
}
```

### Scenario 2: Large Batch Processing (Multi-GPU)
```json
{
  "base_dir": "./outputs",
  "data_dir": "./data",
  "esm3_model": "esm3-sm-open-v1",
  "esm3_num_steps": 12,
  "esm3_device": "cuda",
  "esm3_precision": "bf16",
  "max_sequences": 100,
  "max_seq_length": 1200,
  "parallel_predictions": true,
  "max_workers": 16,
  "batch_size": 8,
  "visible_devices": "0,1,2,3",
  "gpu_memory_fraction": 0.9,
  "cuda_version": "13.0"
}
```

### Scenario 3: Structure Prediction Focus
```json
{
  "base_dir": "./outputs",
  "data_dir": "./data",
  "esm3_model": "esm3-sm-open-v1",
  "esm3_num_steps": 16,
  "esm3_device": "cuda",
  "esm3_precision": "bf16",
  "predictions_dir": "./outputs/structures",
  "structures_dir": "./outputs/structures",
  "min_structure_quality": 0.8,
  "enable_validation": true,
  "p2rank_threads": 8,
  "p2rank_prediction_threshold": 0.7
}
```

### Scenario 4: Drug Discovery Pipeline
```json
{
  "base_dir": "./outputs",
  "data_dir": "./data",
  "esm3_model": "esm3-sm-open-v1",
  "esm3_num_steps": 10,
  "vina_box_size": 25,
  "vina_exhaustiveness": 16,
  "vina_num_modes": 20,
  "vina_cpu": 4,
  "p2rank_threads": 8,
  "p2rank_prediction_threshold": 0.6,
  "parallel_predictions": true,
  "max_workers": 12
}
```

### Scenario 5: Secondary Metabolite Analysis
```json
{
  "base_dir": "./outputs",
  "data_dir": "./data",
  "antismash_env": "antismash",
  "antismash_taxon": "bacteria",
  "antismash_min_cluster_size": 5,
  "input_sequences_dir": "./data/sequences",
  "input_annotations_dir": "./data/annotations",
  "logs_dir": "./outputs/logs",
  "log_level": "INFO",
  "enable_cache": true,
  "cache_ttl_hours": 48
}
```

## Advanced Configuration

### Multi-Environment Setup
Create different configs for different environments:

```bash
# Create environment-specific configs
config/
├── config.development.json    # Local development
├── config.staging.json        # Staging server
├── config.production.json     # Production server
└── config.hpc.json           # HPC cluster
```

### Configuration Templates

#### Template for CUDA 11 Systems
```json
{
  "cuda_version": "11.8",
  "gpu_memory_fraction": 0.7,
  "allow_growth": true,
  "visible_devices": "0",
  "esm3_precision": "fp16"
}
```

#### Template for CUDA 12 Systems
```json
{
  "cuda_version": "12.2",
  "gpu_memory_fraction": 0.8,
  "allow_growth": false,
  "visible_devices": "0,1",
  "esm3_precision": "bf16"
}
```

#### Template for CUDA 13 Systems
```json
{
  "cuda_version": "13.0",
  "gpu_memory_fraction": 0.9,
  "allow_growth": false,
  "visible_devices": "0,1,2,3",
  "esm3_precision": "bf16",
  "parallel_predictions": true,
  "max_workers": 32
}
```

## Validation and Testing

### Validate Configuration
```bash
# Validate your configuration
cd config
python validate_config.py my_config.json

# Validate and create missing directories
python validate_config.py my_config.json --create-dirs
```

### Test Configuration
```bash
# Quick configuration test
python -m protflow.main --config config.json --test-mode --max_sequences 2

# Test with minimal resources
python -m protflow.main --config config.json --debug_mode true --skip_expensive_operations true
```

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   ```json
   {
     "gpu_memory_fraction": 0.5,
     "batch_size": 1,
     "max_seq_length": 800
   }
   ```

2. **Slow Performance**
   ```json
   {
     "parallel_predictions": true,
     "max_workers": 8,
     "enable_cache": true,
     "cache_size_limit_gb": 5
   }
   ```

3. **Disk Space Issues**
   ```json
   {
     "cache_size_limit_gb": 1,
     "cache_ttl_hours": 6,
     "log_max_bytes": 1048576,
     "log_backup_count": 3
   }
   ```

### Environment Variables
You can override config values with environment variables:
```bash
export PROTFLOW_ESM3_DEVICE=cuda
export PROTFLOW_MAX_WORKERS=16
export PROTFLOW_LOG_LEVEL=DEBUG
```

## Migration Guide

### From Old Config (esm3_pipeline)
If you have an old configuration:
```json
{
  "base_dir": "./esm3_pipeline"
}
```

Update to new structure:
```json
{
  "base_dir": "./outputs",
  "data_dir": "./data",
  "input_sequences_dir": "./data/sequences",
  "predictions_dir": "./outputs/predictions",
  "logs_dir": "./outputs/logs"
}
```

### Path Updates
- `./esm3_pipeline` → `./outputs`
- `./esm3_pipeline/logs` → `./outputs/logs`
- `./data` → `./data/sequences` (move sequence files)
- Create new subdirectories as needed

For more information, see `CONFIG_README.md` and run the configuration validator.