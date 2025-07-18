"""
The entry point of the converter.
"""

import argparse
from pathlib import Path

import yaml

from src.upnpdesc2yang.converter import convert_device_with_services, convert_service


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
    # Read the input yaml file
    with open(input_yaml, "r") as f:
        input_dict = yaml.safe_load(f)
    print(input_dict)

    PARENT = "device_name"
    CHILDREN = "devices"
    SERVICES = "services"

    ident = 0
    queue = []
    queue.append(input_dict)

    # DFS
    cur = input_dict
    while cur:
        if CHILDREN in cur:
            cur = cur[CHILDREN]

        if CHILDREN not in cur:
            cur = None


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
