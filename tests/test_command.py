import difflib
import subprocess


class TestCommand:

    def test_command_single_service(self):
        output_path = "test-switch-power.yang"

        convert_result = subprocess.run(
            [
                "python",
                "convert.py",
                "--service",
                "input/upnp_specs/home_automation/lighting_control/service/SwitchPower1.xml",
                "--module",
                "test-switch-power",
            ],
            capture_output=True,
            text=True,
        )
        assert convert_result.returncode == 0, "Convert single service failed"

        result = subprocess.run(
            ["pyang", "--lint", "--strict", output_path],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, "Lint single service failed"

        # Clean up
        subprocess.run(["rm", output_path])

    def test_command_device_with_services(self):
        output_path = "test-light-device.yang"

        convert_result = subprocess.run(
            [
                "python",
                "convert.py",
                "--device",
                "--services",
                "input/upnp_specs/home_automation/lighting_control/service/SwitchPower1.xml",
                "input/upnp_specs/home_automation/lighting_control/service/Dimming1.xml",
                "--module",
                "test-light-device",
            ],
            capture_output=True,
            text=True,
        )
        assert convert_result.returncode == 0, "Convert device with service failed"

        result = subprocess.run(
            ["pyang", "--lint", "--strict", output_path],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, "Lint device with service failed"

        # Clean up
        subprocess.run(["rm", output_path])

    def test_command_device_with_embed_devices(self):
        module_name = "test-embed-device"
        output_path = f"{module_name}.yang"

        convert_result = subprocess.run(
            ["python", "convert.py", "--config", "tests/test.yaml"],
            capture_output=True,
            text=True,
        )
        assert (
            convert_result.returncode == 0
        ), "Convert device with embed devices failed"

        result = subprocess.run(
            ["pyang", "--lint", "--strict", output_path],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, "Lint device with service failed"

        # Use the following command to check if the embed device is present
        result = subprocess.run(
            [
                "pyang",
                "-f",
                "tree",
                f"--tree-path={module_name}/devices/child-device-name/devices/another-grandchild-device",
                output_path,
            ],
            capture_output=True,
            text=True,
        )
        assert (
            result.stdout.find("another-grandchild-device") != -1
        ), "Embed device not found"

        # Clean up
        subprocess.run(["rm", output_path])

    def test_command_ungroup(self):
        input_path = "tests/test_input/ungroup-input.yang"
        output_path = "ungroup-input.yang"

        convert_result = subprocess.run(
            [
                "python",
                "convert.py",
                "--ungroup",
                input_path,
                "--output-path",
                f"{output_path}",
            ],
            capture_output=True,
            text=True,
        )
        assert convert_result.returncode == 0, "Ungroup failed"

        original_tree = subprocess.run(
            ["pyang", "-f", "tree", input_path],
            capture_output=True,
            text=True,
        )
        assert original_tree.returncode == 0, "Original tree failed"
        ungrouped_tree = subprocess.run(
            ["pyang", "-f", "tree", output_path],
            capture_output=True,
            text=True,
        )
        assert ungrouped_tree.returncode == 0, "Ungrouped tree failed"

        diff = list(
            difflib.unified_diff(
                original_tree.stdout,
                ungrouped_tree.stdout,
            )
        )
        assert not diff, "Ungrouping has differences:\n" + "\n".join(diff)
        # Clean up
        subprocess.run(["rm", output_path])
