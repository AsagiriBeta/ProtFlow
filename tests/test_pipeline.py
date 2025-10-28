"""
Unit tests for ProtFlow pipeline components.
"""
import unittest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock

from esm3_pipeline import config, exceptions
from esm3_pipeline.seq_parser import extract_proteins_from_gbk, filter_and_select, validate_sequence
from esm3_pipeline.ligand_prep import check_obabel_available, validate_pdbqt
from esm3_pipeline.p2rank import check_java_available
from esm3_pipeline.vina_dock import check_vina_available, parse_vina_output


class TestConfig(unittest.TestCase):
    """Test configuration management."""

    def test_default_config(self):
        """Test default configuration creation."""
        cfg = config.ProtFlowConfig()
        self.assertIsNotNone(cfg.base_dir)
        self.assertEqual(cfg.esm3_model, 'esm3-sm-open-v1')
        self.assertEqual(cfg.min_seq_length, 50)
        self.assertEqual(cfg.max_seq_length, 1200)

    def test_config_paths(self):
        """Test path initialization."""
        cfg = config.ProtFlowConfig()
        self.assertIsInstance(cfg.base_dir, Path)
        self.assertIsInstance(cfg.gbk_dir, Path)
        self.assertIsInstance(cfg.pdb_dir, Path)

    def test_config_to_dict(self):
        """Test config serialization."""
        cfg = config.ProtFlowConfig()
        data = cfg.to_dict()
        self.assertIsInstance(data, dict)
        self.assertIn('base_dir', data)
        self.assertIn('esm3_model', data)

    def test_config_from_file_json(self):
        """Test loading config from JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"min_seq_length": 100, "max_seq_length": 1000}')
            f.flush()

            try:
                cfg = config.ProtFlowConfig.from_file(Path(f.name))
                self.assertEqual(cfg.min_seq_length, 100)
                self.assertEqual(cfg.max_seq_length, 1000)
            finally:
                Path(f.name).unlink()


class TestSequenceParser(unittest.TestCase):
    """Test sequence parsing utilities."""

    def test_validate_sequence(self):
        """Test sequence validation."""
        self.assertTrue(validate_sequence('ACDEFGHIKLMNPQRSTVWY'))
        self.assertTrue(validate_sequence('ACDEFGHIKLMNPQRSTVWYX'))
        self.assertTrue(validate_sequence('ACDEFG*'))
        self.assertFalse(validate_sequence('ACDEFGZ'))
        self.assertFalse(validate_sequence('123456'))

    def test_extract_proteins_empty_dir(self):
        """Test extraction from empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            out_fasta = tmpdir / 'output.faa'

            count = extract_proteins_from_gbk(tmpdir, out_fasta)
            self.assertEqual(count, 0)

    def test_filter_and_select(self):
        """Test sequence filtering."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            in_fasta = tmpdir / 'input.faa'
            out_fasta = tmpdir / 'output.faa'

            # Create test FASTA
            with open(in_fasta, 'w') as f:
                f.write('>seq1\n')
                f.write('A' * 30 + '\n')  # Too short
                f.write('>seq2\n')
                f.write('A' * 100 + '\n')  # OK
                f.write('>seq3\n')
                f.write('A' * 200 + '\n')  # OK
                f.write('>seq4\n')
                f.write('A' * 2000 + '\n')  # Too long

            selected = filter_and_select(in_fasta, min_len=50, max_len=1200, limit=10, out_fasta=out_fasta)
            self.assertEqual(len(selected), 2)


class TestDependencies(unittest.TestCase):
    """Test dependency checking."""

    def test_check_obabel(self):
        """Test OpenBabel availability check."""
        result = check_obabel_available()
        self.assertIsInstance(result, bool)

    def test_check_java(self):
        """Test Java availability check."""
        result = check_java_available()
        self.assertIsInstance(result, bool)

    def test_check_vina(self):
        """Test Vina availability check."""
        result = check_vina_available()
        self.assertIsInstance(result, bool)


class TestVinaUtils(unittest.TestCase):
    """Test Vina utilities."""

    def test_parse_vina_output(self):
        """Test parsing Vina log file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            log_file = tmpdir / 'vina.log'

            # Create mock log file
            with open(log_file, 'w') as f:
                f.write('Some header\n')
                f.write('REMARK VINA RESULT:    -8.5      0.000      0.000\n')
                f.write('Some footer\n')

            affinity = parse_vina_output(log_file)
            self.assertEqual(affinity, -8.5)

    def test_parse_vina_output_no_file(self):
        """Test parsing non-existent log file."""
        affinity = parse_vina_output(Path('/nonexistent/file.log'))
        self.assertIsNone(affinity)


class TestPDBQTValidation(unittest.TestCase):
    """Test PDBQT validation."""

    def test_validate_pdbqt_nonexistent(self):
        """Test validation of non-existent file."""
        result = validate_pdbqt(Path('/nonexistent.pdbqt'))
        self.assertFalse(result)

    def test_validate_pdbqt_valid(self):
        """Test validation of valid PDBQT."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdbqt', delete=False) as f:
            f.write('ATOM      1  C   LIG A   1       0.000   0.000   0.000  1.00  0.00     0.000 C\n')
            f.write('ROOT\n')
            f.write('TORSDOF 0\n')
            f.flush()

            try:
                result = validate_pdbqt(Path(f.name))
                self.assertTrue(result)
            finally:
                Path(f.name).unlink()


class TestExceptions(unittest.TestCase):
    """Test exception classes."""

    def test_protflow_error(self):
        """Test base exception."""
        with self.assertRaises(exceptions.ProtFlowError):
            raise exceptions.ProtFlowError("Test error")

    def test_dependency_error(self):
        """Test dependency error."""
        with self.assertRaises(exceptions.DependencyError):
            raise exceptions.DependencyError("Dependency missing")

    def test_model_load_error(self):
        """Test model load error."""
        with self.assertRaises(exceptions.ModelLoadError):
            raise exceptions.ModelLoadError("Model failed to load")


if __name__ == '__main__':
    unittest.main()

