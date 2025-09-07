"""
Test suite for main entry point
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import main


class TestMainEntryPoint:
    """Test the main entry point functionality"""
    
    def test_list_modules(self, capsys):
        """Test listing available modules"""
        with patch('sys.argv', ['main.py', 'list']):
            with pytest.raises(SystemExit) as exc_info:
                main.main()
            assert exc_info.value.code == 0
            
        captured = capsys.readouterr()
        assert "Core:" in captured.out
        assert "Security:" in captured.out
        assert "Dolphin:" in captured.out
        assert "Automation:" in captured.out
    
    def test_invalid_module(self):
        """Test invalid module selection"""
        with patch('sys.argv', ['main.py', 'invalid_module']):
            with pytest.raises(SystemExit):
                main.main()
    
    @patch('main.Path.glob')
    def test_list_available_modules(self, mock_glob):
        """Test list_available_modules function"""
        # Mock file paths
        mock_glob.return_value = [
            Path('test1.py'),
            Path('test2.py'),
            Path('test3.py')
        ]
        
        # Should not raise any exceptions
        main.list_available_modules()
    
    def test_module_choices(self):
        """Test that all module choices are valid"""
        valid_modules = ['core', 'security', 'dolphin', 'automation', 
                        'database', 'monitoring', 'integrations', 'list']
        
        for module in valid_modules:
            with patch('sys.argv', ['main.py', module]):
                # Mock the actual module imports to avoid ImportError
                with patch.object(main, 'list_available_modules'):
                    with patch('builtins.__import__'):
                        try:
                            main.main()
                        except (SystemExit, AttributeError):
                            # Expected for some modules
                            pass


class TestModuleImports:
    """Test that modules can be imported"""
    
    def test_core_module_structure(self):
        """Test core module exists and has expected structure"""
        core_path = Path(__file__).parent.parent / 'core'
        assert core_path.exists()
        assert (core_path / '__init__.py').exists()
    
    def test_security_module_structure(self):
        """Test security module exists and has expected structure"""
        security_path = Path(__file__).parent.parent / 'security'
        assert security_path.exists()
        assert (security_path / '__init__.py').exists()
    
    def test_all_modules_have_init(self):
        """Test all module directories have __init__.py"""
        src_path = Path(__file__).parent.parent
        modules = ['core', 'security', 'dolphin', 'automation', 
                  'database', 'monitoring', 'integrations', 'utils']
        
        for module in modules:
            module_path = src_path / module
            if module_path.exists():
                assert (module_path / '__init__.py').exists(), f"{module} missing __init__.py"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])