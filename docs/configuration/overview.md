# ProtFlow Configuration Guide

This guide explains the configuration options for ProtFlow after the project structure refactoring.

## Directory Structure Configuration

### Core Directories
- **`base_dir`**: `./outputs` - Main output directory for all results
- **`data_dir`**: `./data` - Input data directory  
- **`src_dir`**: `./src/protflow` - Python package source code
- **`notebooks_dir`**: `./notebooks` - Jupyter notebooks for analysis
- **`scripts_dir`**: `./src/scripts` - Utility scripts

### Input Data Subdirectories
- **`input_sequences_dir`**: `./data/sequences` - Protein sequence files (FASTA, etc.)
- **`input_structures_dir`**: `./data/structures` - Input structure files (PDB, etc.)
- **`input_annotations_dir`**: `./data/annotations` - Annotation files (GFF, BED, etc.)

### Output Subdirectories
- **`predictions_dir`**: `./outputs/predictions` - ESM3 prediction results
- **`structures_dir`**: `./outputs/structures` - Generated structure files
- **`logs_dir`**: `./outputs/logs` - Application logs
- **`cache_dir`**: `./outputs/cache` - Cached results for performance
- **`temp_dir`**: `./outputs/temp` - Temporary files (auto-cleaned)

## Model Configuration

### ESM3 Settings
- **`esm3_model`**: Model version (default: "esm3-sm-open-v1")
- **`esm3_num_steps`**: Number of generation steps (default: 8)
- **`esm3_device`**: Computing device ("cuda" or "cpu")
- **`esm3_precision`**: Numerical precision ("bf16", "fp16", or "fp32")

### Sequence Processing
- **`min_seq_length`**: Minimum sequence length (default: 50)
- **`max_seq_length`**: Maximum sequence length (default: 1200)
- **`max_sequences`**: Maximum sequences to process (default: 10)
- **`sequence_identity_threshold`**: Similarity threshold for filtering (default: 0.9)

## Tool-Specific Settings

### P2Rank (Binding Site Prediction)
- **`p2rank_version`**: P2Rank version (default: "2.5.1")
- **`p2rank_threads`**: Number of CPU threads (default: 2)
- **`p2rank_prediction_threshold`**: Confidence threshold (default: 0.5)

### AutoDock Vina (Docking)
- **`vina_box_size`**: Search box size in Angstroms (default: 20)
- **`vina_exhaustiveness`**: Search exhaustiveness (default: 8)
- **`vina_num_modes`**: Number of binding modes (default: 9)
- **`vina_cpu`**: CPU cores for Vina (default: 1)

### antiSMASH (Secondary Metabolite Analysis)
- **`antismash_env`**: Conda environment name (default: "antismash")
- **`antismash_taxon`**: Taxonomic group (default: "bacteria")
- **`antismash_min_cluster_size`**: Minimum gene cluster size (default: 5)

## GPU and CUDA Configuration

### CUDA 13 Support
- **`cuda_version`**: CUDA version for compatibility (default: "13.0")
- **`gpu_memory_fraction`**: Maximum GPU memory usage (default: 0.8)
- **`allow_growth`**: Allow dynamic GPU memory allocation (default: true)
- **`visible_devices`**: Visible GPU devices (default: "0")

### Server Environment
- **`server_env`**: Environment type ("development", "staging", "production")
- **`max_concurrent_jobs`**: Maximum parallel jobs (default: 4)
- **`job_timeout`**: Job timeout in seconds (default: 3600)
- **`memory_limit_gb`**: Memory limit in GB (default: 16)

## Logging Configuration

### Log Settings
- **`log_level`**: Logging level ("DEBUG", "INFO", "WARNING", "ERROR")
- **`log_file`**: Log file path (default: "./outputs/logs/protflow.log")
- **`log_format`**: Log message format
- **`log_max_bytes`**: Maximum log file size in bytes (default: 10MB)
- **`log_backup_count`**: Number of backup log files (default: 5)

## Performance Optimization

### Caching
- **`enable_cache`**: Enable result caching (default: true)
- **`cache_size_limit_gb`**: Cache size limit in GB (default: 2)
- **`cache_ttl_hours`**: Cache time-to-live in hours (default: 24)

### Parallel Processing
- **`parallel_predictions`**: Enable parallel predictions (default: false)
- **`max_workers`**: Maximum worker processes (default: 4)
- **`batch_size`**: Batch size for processing (default: 1)

## Quality Control

### Validation
- **`enable_validation`**: Enable input validation (default: true)
- **`min_structure_quality`**: Minimum structure quality score (default: 0.7)
- **`max_ram_usage_gb`**: Maximum RAM usage in GB (default: 32)

## External Tools

### Tool Paths
- **`p2rank_path`**: Custom P2Rank installation path (auto-detected if null)
- **`vina_path`**: Custom Vina installation path (auto-detected if null)
- **`antismash_path`**: Custom antiSMASH installation path (auto-detected if null)
- **`foldseek_path`**: Custom Foldseek installation path (auto-detected if null)

## API and Web Interface

### Server Settings
- **`api_host`**: API server host (default: "127.0.0.1")
- **`api_port`**: API server port (default: 8080)
- **`api_debug`**: Enable debug mode (default: false)
- **`enable_swagger`**: Enable Swagger documentation (default: true)

## Development Options

### Debug and Testing
- **`debug_mode`**: Enable debug mode (default: false)
- **`test_data_dir`**: Test data directory (default: "./tests/data")
- **`skip_expensive_operations`**: Skip expensive operations during testing (default: false)

## Usage Examples

### Basic Usage
```bash
# Use default config.json in project root
python -m protflow.main --input data/sequences/protein.fasta

# Use custom config file
python -m protflow.main --config my_config.json --input data/sequences/protein.fasta
```

### Environment-Specific Config
```bash
# Production environment
export PROTFLUX_ENV=production
python -m protflow.main --config config/production.json

# Development environment
export PROTFLUX_ENV=development
python -m protflow.main --config config/development.json
```

## Configuration Priority

1. Command-line arguments (highest priority)
2. Environment variables
3. Configuration file
4. Default values (lowest priority)

## Migration from Old Structure

If you're migrating from the old `esm3_pipeline` structure:

1. Update `base_dir` from `"./esm3_pipeline"` to `"./outputs"`
2. Move existing data to appropriate `data/` subdirectories
3. Update log file paths to use `./outputs/logs/`
4. Configure CUDA 13 settings if using newer GPU drivers
5. Review new performance and quality control options

For questions or issues, please refer to the main documentation or create an issue in the project repository.