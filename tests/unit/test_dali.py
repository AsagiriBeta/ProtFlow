"""
Tests for DALI structure alignment module.

This test suite covers:
- DaliResult dataclass
- DaliAligner initialization
- Mode detection and validation
- Result parsing
- Online/local mode switching (mocked)
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

# Import the module
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from protflow.prediction.dali import (
    DaliAligner,
    DaliResult,
    run_dali_alignment,
    batch_align,
)


class TestDaliResult:
    """Test DaliResult dataclass."""
    
    def test_creation(self):
        """Test creating a DaliResult."""
        result = DaliResult(
            query_name="test_protein",
            target_pdb="1ABC",
            rank=1,
            z_score=45.2,
            rmsd=1.8,
            lali=234,
            nres=250,
            identity=25.0,
        )
        
        assert result.query_name == "test_protein"
        assert result.target_pdb == "1ABC"
        assert result.rank == 1
        assert result.z_score == 45.2
        assert result.rmsd == 1.8
    
    def test_to_dict(self):
        """Test converting to dictionary."""
        result = DaliResult(
            query_name="test",
            target_pdb="1ABC",
            rank=1,
            z_score=45.2,
            rmsd=1.8,
        )
        
        d = result.to_dict()
        assert d['query'] == "test"
        assert d['target_pdb'] == "1ABC"
        assert d['z_score'] == 45.2


class TestDaliAlignerInitialization:
    """Test DaliAligner initialization."""
    
    def test_default_initialization(self):
        """Test default initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            aligner = DaliAligner(output_dir=Path(tmpdir))
            assert aligner.mode == 'auto'
            assert aligner.timeout == 300
            assert aligner.max_retries == 3
    
    def test_online_mode(self):
        """Test online mode initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            aligner = DaliAligner(mode='online', output_dir=Path(tmpdir))
            assert aligner.mode == 'online'
    
    def test_local_mode(self):
        """Test local mode initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Mock local DALI check to avoid requiring actual installation
            with patch.object(DaliAligner, '_check_local_dali', return_value=True):
                aligner = DaliAligner(mode='local', output_dir=Path(tmpdir))
                assert aligner.mode == 'local'
    
    def test_invalid_mode(self):
        """Test invalid mode raises error."""
        with pytest.raises(ValueError, match="Invalid mode"):
            DaliAligner(mode='invalid')
    
    def test_output_dir_creation(self):
        """Test output directory is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "dali_output"
            assert not output_dir.exists()
            
            aligner = DaliAligner(output_dir=output_dir)
            assert output_dir.exists()


class TestDaliAlignerMethods:
    """Test DaliAligner methods."""
    
    @patch('protflow.prediction.dali.subprocess.run')
    def test_check_local_dali(self, mock_run):
        """Test checking for local DALI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Mock successful dali.pl execution
            mock_run.return_value = Mock(returncode=0, stdout=b"dali help")
            
            dali_cmd = Path(tmpdir) / "dali.pl"
            dali_cmd.write_text("#!/bin/bash\necho 'dali'")
            
            aligner = DaliAligner(dali_cmd=dali_cmd, output_dir=Path(tmpdir))
            result = aligner._check_local_dali()
            assert result is True
    
    @patch('protflow.prediction.dali.requests.get')
    def test_check_online_availability(self, mock_get):
        """Test checking online DALI availability."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Mock successful response
            mock_get.return_value = Mock(status_code=200)
            
            aligner = DaliAligner(output_dir=Path(tmpdir))
            result = aligner._check_online_availability()
            assert result is True
    
    @patch('protflow.prediction.dali.requests.get')
    def test_check_online_unavailable(self, mock_get):
        """Test handling unavailable online DALI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Mock failed response
            mock_get.side_effect = Exception("Connection failed")
            
            aligner = DaliAligner(output_dir=Path(tmpdir))
            result = aligner._check_online_availability()
            assert result is False
    
    def test_parse_dali_log(self):
        """Test parsing DALI log file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create mock log file
            log_file = Path(tmpdir) / "dali.log"
            log_file.write_text("""
# Rank PDB    Z    rmsd lali nres  %id  Description
1    1ABC   45.2  1.8  234  250   25   Test protein 1
2    2DEF   42.1  2.1  228  250   23   Test protein 2
3    3GHI   38.5  2.5  220  250   21   Test protein 3
""")
            
            aligner = DaliAligner(output_dir=Path(tmpdir))
            results = aligner._parse_dali_log(log_file, "test_query")
            
            assert len(results) == 3
            assert results[0].target_pdb == "1ABC"
            assert results[0].z_score == 45.2
            assert results[0].rmsd == 1.8
            assert results[0].rank == 1
    
    def test_save_results(self):
        """Test saving results to CSV."""
        with tempfile.TemporaryDirectory() as tmpdir:
            aligner = DaliAligner(output_dir=Path(tmpdir))
            
            results = [
                DaliResult("test", "1ABC", 1, 45.2, 1.8),
                DaliResult("test", "2DEF", 2, 42.1, 2.1),
            ]
            
            aligner._save_results(results, "test_protein")
            
            csv_file = Path(tmpdir) / "test_protein_results.csv"
            assert csv_file.exists()
            
            content = csv_file.read_text()
            assert "1ABC" in content
            assert "2DEF" in content
            assert "45.2" in content


class TestDaliAlignerIntegration:
    """Integration tests for DaliAligner."""
    
    @patch('protflow.prediction.dali.subprocess.run')
    def test_local_align(self, mock_run):
        """Test local alignment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create mock structure file
            structure = tmpdir / "test.pdb"
            structure.write_text("ATOM  1  CA  ALA A   1")
            
            # Create mock log file that will be "created" by DALI
            def create_log(*args, **kwargs):
                log_dir = tmpdir / "dali" / "test"
                log_dir.mkdir(parents=True, exist_ok=True)
                log_file = log_dir / "dali.log"
                log_file.write_text("1 1ABC 45.2 1.8 234 250 25\n")
                return Mock(returncode=0, stdout="", stderr="")
            
            mock_run.side_effect = create_log
            
            aligner = DaliAligner(
                mode='local',
                dali_cmd=tmpdir / "dali.pl",
                output_dir=tmpdir / "dali"
            )
            
            with patch.object(aligner, '_check_local_dali', return_value=True):
                results = aligner._align_local(structure, "test")
                assert len(results) > 0
                assert results[0].target_pdb == "1ABC"


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @patch.object(DaliAligner, 'align')
    def test_run_dali_alignment(self, mock_align):
        """Test run_dali_alignment convenience function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            structure = tmpdir / "test.pdb"
            structure.write_text("ATOM  1  CA  ALA A   1")
            
            mock_align.return_value = [
                DaliResult("test", "1ABC", 1, 45.2, 1.8)
            ]
            
            results = run_dali_alignment(structure, mode='online')
            assert len(results) == 1
            assert results[0].target_pdb == "1ABC"
    
    @patch.object(DaliAligner, 'align_batch')
    def test_batch_align(self, mock_batch):
        """Test batch_align convenience function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create mock structures
            for i in range(3):
                (tmpdir / f"protein{i}.pdb").write_text(f"ATOM  1  CA  ALA A   {i}")
            
            mock_batch.return_value = [
                ("protein0", [DaliResult("protein0", "1ABC", 1, 45.2, 1.8)]),
                ("protein1", [DaliResult("protein1", "2DEF", 1, 42.1, 2.1)]),
                ("protein2", [DaliResult("protein2", "3GHI", 1, 38.5, 2.5)]),
            ]
            
            results = batch_align(tmpdir, pattern="*.pdb")
            assert len(results) == 3
            assert results[0][0] == "protein0"


def test_module_imports():
    """Test that module imports work correctly."""
    from protflow.prediction import dali
    
    assert hasattr(dali, 'DaliAligner')
    assert hasattr(dali, 'DaliResult')
    assert hasattr(dali, 'run_dali_alignment')
    assert hasattr(dali, 'batch_align')


if __name__ == '__main__':
    # Run tests if pytest is available
    try:
        import pytest
        pytest.main([__file__, '-v'])
    except ImportError:
        print("pytest not available, running manual tests...")
        
        # Run a few basic tests manually
        test_result = TestDaliResult()
        test_result.test_creation()
        test_result.test_to_dict()
        print("✓ DaliResult tests passed")
        
        test_init = TestDaliAlignerInitialization()
        test_init.test_default_initialization()
        print("✓ DaliAligner initialization tests passed")
        
        print("\n✓ All manual tests passed!")
