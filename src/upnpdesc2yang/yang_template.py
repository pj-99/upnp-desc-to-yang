"""Yang template for upnp to yang conversion"""

from typing import List

from common.case_helper import to_enum_upper_case


def get_service_top(service_name) -> str:
    return f"""
    uses {service_name}-top;
    """


def get_device_top_grouping(device_name) -> str:
    return f"""
    grouping {device_name}-top {{
        description "{device_name}";

        container {device_name} {{
            description "{device_name}";
            
            uses {device_name}-desc-top;
            uses {device_name}-services-top;
            uses {device_name}-devices-top;
        }}
    }}
    
    uses {device_name}-top;
    """


def combine_uses_statements(groupings):
    return "\n".join([f"uses {grouping};" for grouping in groupings])


def get_children_devices_top_grouping(device_name, devices_groupings):
    uses_statements = combine_uses_statements(devices_groupings)
    return (
        f"""
    grouping {device_name}-devices-top {{
        description "Embedded devices";
        container devices {{
            description "Embedded devices";
            {uses_statements}
        }}
    }}
    """,
        f"{device_name}-devices-top",
    )


def get_services_top_grouping(device_name, service_groupings):
    uses_statements = combine_uses_statements(service_groupings)
    return f"""
    grouping {device_name}-services-top {{
        description "Services";
        container services {{
            description "Services";
            {uses_statements}
        }}
    }}
    """


def get_device_desc_top_grouping(device_name):
    return (
        f"""
    grouping {device_name}-desc-top {{
        """
        + """
        description "Device description";
        container device {
            config false;
            description "Device description";
            
            leaf device-type {
                type string;
                description "Device type";
            }

            leaf friendly-name {
                type string;
                description "Name";
            }

            leaf manufacturer {
                type string;
                description "Manufacturer";
            }

            leaf manufacturer-URL {
                type string;
                description "Manufacturer URL";
            }

            leaf model-description {
                type string;
                description "Model description";
            }

            leaf model-name {
                type string;
                description "Model name";
            }

            leaf model-number {
                type string;
                description "Model number";
            }

            leaf model-URL {
                type string;
                description "Model URL";
            }

            leaf serial-number {
                type string;
                description "Serial number";
            }

            leaf UDN {
                type string;
                description "UUID";
            }

            leaf UPC {
                type string;
                description "UPC";
            }

            list icon-list {
                key "url";
                description  "Icons";

                leaf mimetype {
                    type string;
                    description "MIME type";
                }

                leaf width {
                    type uint32;
                    description "Width";
                }

                leaf height {
                    type uint32;
                    description "Height";
                }

                leaf depth {
                    type uint32;
                    description "Color depth";
                }

                leaf url {
                    type string;
                    description "URL";
                }
            }
            
            // TODO: check
            leaf presentation-url {
                type string;
                description "Presentation URL";
            }
        }
    }
"""
    )


def get_send_events_grouping():
    return """
    grouping send-events-grouping {
        description "Send event attribute";
        leaf send-events {
            type boolean;
            description "Send event attribute";
        }
    }
    """


def get_enum_state(enum: str):
    return f"""
    enum  {to_enum_upper_case(enum)} {{
        description "{enum}";
    }}
    """


def get_enums_block(enum_list: List[str]) -> str:
    """
     type enumeration {
      enum ACCEPT_ROUTE {
        description "default policy to accept the route";
      }
      enum REJECT_ROUTE {
        description "default policy to reject the route";
      }
    }
    """
    enum_lines = [get_enum_state(enum) for enum in enum_list]
    enum_content = "".join(enum_lines)
    return f"""
    type enumeration {{
        {enum_content}
    }}
    """
