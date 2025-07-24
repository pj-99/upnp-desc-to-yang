"""
The entry point of the converter.
"""

import argparse
from pathlib import Path

import yaml

from src.upnpdesc2yang.converter import (
    Device,
    convert_device_with_services,
    convert_service,
    make_device_with_services,
    wrap_content_to_module,
)


def handle_upnp_spec_file(input_service_file, module_name):
    service_path = Path(input_service_file)

    # Generate files under output folder, and use new module name
    output_dir = Path("output") / service_path.parent.relative_to("input")

    output_path = output_dir / (module_name + ".yang")

    output = convert_device_with_services(module_name, input_service_file, minify=False)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(output)
    print("Written to", output_path)


def handle_service_conversion(input_service_file_path, module_name):
    """
    Convert a UPnP service into a YANG file
    """
    print("Converting service", input_service_file_path, "to", module_name)

    output_content = convert_service(module_name, input_service_file_path)

    output_path = Path(module_name + ".yang")
    with open(output_path, "w") as f:
        f.write(output_content)

    print("Written to", output_path)


def handle_device_with_services_conversion(input_service_file_paths, module_name):
    """
    Convert a UPnP device and service(s) into a YANG file
    """

    print("Converting service", input_service_file_paths, "to", module_name)

    output_content = convert_device_with_services(module_name, input_service_file_paths)

    output_path = Path(module_name + ".yang")
    with open(output_path, "w") as f:
        f.write(output_content)

    print("Written to", output_path)


def handle_embed_device_input(input_yaml):
    NAME = "device_name"
    SERVICES = "services"
    CHILDREN = "devices"

    def _helper(device_name, services, children) -> Device:
        """Simple DFS"""
        cur_device = make_device_with_services(device_name, services)

        if len(children):
            for child in children:
                cur_device.add_child(
                    _helper(
                        child[NAME],
                        child[SERVICES],
                        child.get(CHILDREN, []),
                    )
                )
        return cur_device

    # Read the input yaml file
    with open(input_yaml, "r") as f:
        input_dict = yaml.safe_load(f)
    root_device = _helper(input_dict[NAME], input_dict[SERVICES], input_dict[CHILDREN])
    yang_module = wrap_content_to_module(root_device.name, str(root_device))

    # Write result
    output_path = Path(root_device.name + ".yang")
    with open(output_path, "w") as f:
        f.write(str(yang_module))
    return root_device


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert UPnP device and service description to YANG"
    )
    # Single service
    parser.add_argument("--module", type=str, help="Name of the output module")
    parser.add_argument(
        "--service", type=str, help="Path to the service description file"
    )

    # Device with services
    parser.add_argument(
        "--device", action=argparse.BooleanOptionalAction, help="Create a device"
    )
    parser.add_argument(
        "--services", nargs="+", help="Paths to the service description files"
    )
    # Load from config yaml file
    parser.add_argument("--config", type=str, help="Path to the config yaml file")

    args = parser.parse_args()

    if args.config:
        handle_embed_device_input(args.config)
    elif args.service:
        handle_service_conversion(args.service, args.module)
    elif args.device:
        handle_device_with_services_conversion(args.services, args.module)
