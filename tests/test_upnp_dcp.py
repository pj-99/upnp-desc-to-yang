import os
import subprocess

import pytest

from src.upnpdesc2yang.converter import handle_upnp_spec_file
from tests.test_file_list import upnp_service_files

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestServiceFiles:

    @pytest.mark.parametrize("service_file,module_name", upnp_service_files)
    def test_handle_upnp_spec_file(self, service_file, module_name):
        try:
            output_path = handle_upnp_spec_file(
                input_service_file=service_file,
                module_name=module_name,
            )
            assert output_path is not None
            result = subprocess.run(["pyang", "--lint", "--strict", output_path])
            assert result.returncode == 0
        except Exception as e:
            pytest.fail(f"Failed to handle {service_file}: {e}")
