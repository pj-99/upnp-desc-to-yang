import sys
from pathlib import Path
from typing import List


# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent))

from common.util import get_service_name_from_upnp_spec_file

# TODO: refactor service_convert part
from service_convert.service import Service
from service_convert.yang_service import convert_service_to_yang
from yang_helper import YangModule
from yang_template import (
    get_children_devices_top_grouping,
    get_device_desc_top_grouping,
    get_device_top_grouping,
    get_device_top_uses,
    get_service_top,
    get_services_top_grouping,
)


def get_yang_output_namespace(root_name):
    return f"http://example.com/upnp-yang-schema/{root_name}"


def get_yang_service_groupings(
    service_name,
    service_xml_file,
) -> str:
    with open(service_xml_file, "r") as f:
        xml_input = f.read()
    service = Service(xml_input, service_name)
    return convert_service_to_yang(service).groupings_and_names()


def top_grouping_name(root_name):
    return f"{root_name}-top"


class Device:

    def __init__(self, name, groupings, uses, device_top_grouping: str):
        self.name = name
        self.groupings: List = groupings
        self.uses: str = uses
        self.groupings_name = top_grouping_name(name)
        self.device_top_grouping = device_top_grouping

        # Init with no child
        self.children: List[Device] = []
        self.devices_top_grouping = get_children_devices_top_grouping(
            self.name,
            [],
        )

    def add_child(self, child_device):
        self.children.append(child_device)
        self.devices_top_grouping = get_children_devices_top_grouping(
            self.name,
            [top_grouping_name(child_device.name) for child_device in self.children],
        )

    def dump(self):
        # Collects all children groupings and names
        children_groupings = []
        children_groupings_names = []

        # BFS
        queue = self.children
        while len(queue):
            c = queue.pop(0)
            for grand_child in c.children:
                queue.append(grand_child)

            children_groupings.extend(c.groupings)
            children_groupings.append(c.devices_top_grouping)
            children_groupings.append(c.device_top_grouping)

            children_groupings_names.append(top_grouping_name(c.name))

        grouping_str = "\n".join(self.groupings)
        children_groupings_str = "\n".join(children_groupings)
        content_str = (
            self.device_top_grouping
            + grouping_str
            + self.devices_top_grouping
            + children_groupings_str
            + self.uses
        )
        return content_str

    def __repr__(self) -> str:
        return self.dump()


def make_device_with_services(
    root_name,
    service_xml_files,
) -> Device:
    """the content without module"""
    # Top level grouping
    top_grouping = get_device_top_grouping(root_name)
    top_uses = get_device_top_uses(root_name)

    # Device description
    device_desc_grouping = get_device_desc_top_grouping(root_name)

    # Service list
    all_service_names = []
    all_service_groupings = []
    for service_xml in service_xml_files:
        service_name = get_service_name_from_upnp_spec_file(service_xml)
        service_groupings, service_grouping_name = get_yang_service_groupings(
            service_name=service_name,
            service_xml_file=service_xml,
        )
        all_service_names.append(service_grouping_name)
        all_service_groupings.append(service_groupings)

    services_top_grouping = get_services_top_grouping(root_name, all_service_names)
    all_service_groupings = "\n".join(all_service_groupings)

    contents = [
        device_desc_grouping,
        services_top_grouping,
        all_service_groupings,
    ]
    device = Device(root_name, contents, top_uses, top_grouping)
    return device


def convert_device_with_services(root_name, service_xml_files) -> str:
    """Convert service and device into a YANG module"""

    device: Device = make_device_with_services(root_name, service_xml_files)

    module = wrap_content_to_module(root_name, str(device))

    module_output = str(module)
    return module_output


def convert_service(root_name, service_xml) -> str:
    """Convert service description into a service module"""
    # Top level grouping
    top_grouping_and_uses = get_service_top(root_name)

    # Service list
    service_name = root_name
    service_groupings, service_grouping_name = get_yang_service_groupings(
        service_name=service_name,
        service_xml_file=service_xml,
    )
    # Multiple service handling
    all_service_names = [service_grouping_name]
    services_top = get_services_top_grouping(root_name, all_service_names)
    all_service_groupings = "\n".join([service_groupings])

    # Combine all the groupings
    content = "\n".join(
        [
            top_grouping_and_uses,
            all_service_groupings,
            services_top,
        ]
    )
    module = wrap_content_to_module(root_name, content)

    module_output = str(module)
    return module_output


def wrap_content_to_module(root_name, content) -> YangModule:
    namespace = get_yang_output_namespace(root_name)
    module = YangModule(
        root_name,
        namespace,
        content,
    )
    return module


def handle_upnp_spec_file(input_service_file, module_name) -> str:
    """Return output file path"""
    service_path = Path(input_service_file)

    # Generate files under output folder, and use new module name
    output_dir = Path("output") / service_path.parent.relative_to("input")
    output_path = output_dir / (module_name + ".yang")
    output = convert_service(module_name, input_service_file)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(output)
    print("Written to", output_path)
    return output_path
