import sys
from pathlib import Path


# Add parent directory to Python path
sys.path.append(str(Path(__file__).parent))

from common.util import get_service_name_from_upnp_spec_file

# TODO: refactor service_convert part
from service_convert.service import Service
from service_convert.yang_service import YangService, convert_service_to_yang
from yang_helper import YangModule
from yang_template import (
    get_children_devices_top_grouping,
    get_device_desc_top_grouping,
    get_device_top_grouping,
    get_send_events_grouping,
    get_service_top,
    get_services_top_grouping,
    get_state_var_attr_grouping,
)


def get_yang_output_namespace(root_name):
    return f"http://example.com/upnp-yang-schema/{root_name}"


def get_yang_service_groupings(
    service_name,
    service_xml_file,
    has_state_attr_grouping=True,
) -> str:
    with open(service_xml_file, "r") as f:
        xml_input = f.read()
    service = Service(xml_input, service_name)
    return convert_service_to_yang(service).groupings_and_names(
        has_state_attr_grouping=has_state_attr_grouping
    )


def convert_device_with_services(root_name, service_xml_files) -> str:
    """Convert service and device into a YANG module"""
    # Top level grouping
    top_grouping_and_uses = get_device_top_grouping(root_name)

    # Device description
    device_desc = get_device_desc_top_grouping(root_name)

    # Service list
    all_service_names = []
    all_service_groupings = []
    for service_xml in service_xml_files:
        service_name = get_service_name_from_upnp_spec_file(service_xml)
        service_groupings, service_grouping_name = get_yang_service_groupings(
            service_name=service_name,
            service_xml_file=service_xml,
            has_state_attr_grouping=False,  # Prevent duplicate state-variable-attributes
        )
        all_service_names.append(service_grouping_name)
        all_service_groupings.append(service_groupings)

    services_top = get_services_top_grouping(root_name, all_service_names)
    all_service_groupings = "\n".join(all_service_groupings)

    # Device list
    # TODO: embed devices
    all_devices = []
    devices, devices_grouping_name = get_children_devices_top_grouping(
        root_name, all_devices
    )

    # UPnP send events grouping
    send_events_grouping = get_send_events_grouping()

    # Combine all the groupings
    content = "\n".join(
        [
            device_desc,
            all_service_groupings,
            services_top,
            devices,
            top_grouping_and_uses,
            send_events_grouping,
            get_state_var_attr_grouping(),
        ]
    )

    module = YangModule(root_name, get_yang_output_namespace(root_name), content)
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

    # UPnP send events grouping
    send_events_grouping = get_send_events_grouping()

    # Combine all the groupings
    content = "\n".join(
        [
            top_grouping_and_uses,
            all_service_groupings,
            services_top,
            send_events_grouping,
        ]
    )
    yang_output_namespace = get_yang_output_namespace(root_name)
    module = YangModule(root_name, yang_output_namespace, content)

    module_output = str(module)
    return module_output


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
