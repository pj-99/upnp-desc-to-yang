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
