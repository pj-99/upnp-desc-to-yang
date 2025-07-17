import json
import xml.etree.ElementTree as ET
from typing import Any, Dict, List


class Service:
    """Represent a UPnP service. Its values stored in string format"""

    def __init__(self, xml_string: str, service_name: str) -> None:
        self.xml_string: str = xml_string.strip()
        self.spec_version: Dict[str, int] = {}
        self.actions: List[Dict[str, Any]] = []
        self.state_variables: List[Dict[str, Any]] = []
        self.service_name = service_name
        self.parse_xml()

    def parse_xml(self):
        root = ET.fromstring(self.xml_string)

        # The normal service description should have the upnp srv namespace
        prefix = "upnp:"
        ns = {"upnp": "urn:schemas-upnp-org:service-1-0"}

        # Check if root have the upnp srv namespace
        # Since some spec file have no namespace
        if not root.tag.startswith("{"):
            ns = {"upnp": ""}

        # Parse actionList
        action_list = root.find(f"{prefix}actionList", ns)
        for action in action_list.findall(f"{prefix}action", ns):
            action_name = action.find(f"{prefix}name", ns).text
            arguments = []
            argument_list = action.find(f"{prefix}argumentList", ns)
            if argument_list:
                for argument in argument_list.findall(f"{prefix}argument", ns):
                    arg_name = argument.find(f"{prefix}name", ns).text
                    related_state_variable = argument.find(
                        f"{prefix}relatedStateVariable", ns
                    ).text
                    direction = argument.find(f"{prefix}direction", ns).text
                    arguments.append(
                        {
                            "name": arg_name,
                            "relatedStateVariable": related_state_variable.strip(),
                            "direction": direction,
                        }
                    )
            self.actions.append({"name": action_name, "arguments": arguments})

        # Parse serviceStateTable
        state_table = root.find(f"{prefix}serviceStateTable", ns)
        for state_variable in state_table.findall(f"{prefix}stateVariable", ns):
            send_events = state_variable.attrib.get("sendEvents", "no")
            name = state_variable.find(f"{prefix}name", ns).text
            data_type = state_variable.find(f"{prefix}dataType", ns).text
            default_value = (
                state_variable.find(f"{prefix}defaultValue", ns).text
                if state_variable.find(f"{prefix}defaultValue", ns) is not None
                else None
            )

            # Parse allowed value range
            allowed_value_range = {}
            if state_variable.find(f"{prefix}allowedValueRange", ns):
                minimum_elem = state_variable.find(
                    f"{prefix}allowedValueRange/upnp:minimum", ns
                )
                maximum_elem = state_variable.find(
                    f"{prefix}allowedValueRange/upnp:maximum", ns
                )
                step_elem = state_variable.find(
                    f"{prefix}allowedValueRange/upnp:step", ns
                )

                if minimum_elem is not None:
                    min_val = minimum_elem.text.strip()

                    if min_val == "vendor-defined":
                        min_val = "min"
                    allowed_value_range["minimum"] = min_val

                if maximum_elem is not None:
                    max_val = maximum_elem.text.strip()

                    if max_val == "vendor-defined":
                        max_val = "max"
                    allowed_value_range["maximum"] = max_val

                if step_elem is not None:
                    # Note that the current YANG don't support step in `range`
                    allowed_value_range["step"] = step_elem.text.strip()

            allowed_value_list = None
            if state_variable.find(f"{prefix}allowedValueList", ns):
                allowed_value_list = [
                    el.text
                    for el in state_variable.findall(
                        f"{prefix}allowedValueList/{prefix}allowedValue", ns
                    )
                ]

            self.state_variables.append(
                {
                    "name": name,
                    "dataType": data_type,
                    "defaultValue": default_value,
                    "sendEvents": send_events,
                    "allowedValueRange": allowed_value_range,
                    "allowedValueList": allowed_value_list,
                }
            )

    def __repr__(self) -> str:
        """Default representation like json"""
        return json.dumps(
            {
                "spec_version": self.spec_version,
                "actions": self.actions,
                "state_variables": self.state_variables,
            },
            indent=2,
        )

    def to_yang(self) -> str:
        """Convert to yang format"""
        return


if __name__ == "__main__":
    xml_string = """
    <?xml version="1.0"?>
    <scpd xmlns="urn:schemas-upnp-org:service-1-0">
    <specVersion>
        <major>1</major>
        <minor>0</minor>
    </specVersion>
    <actionList>
        <action>
            <name>SetTarget</name>
            <argumentList>
                <argument>
                    <name>newTargetValue</name>
                    <relatedStateVariable>Target</relatedStateVariable>
                    <direction>in</direction>
                </argument>
            </argumentList>
        </action> 
        <action>
            <name>GetTarget</name>
            <argumentList>
                <argument>
                    <name>RetTargetValue</name>
                    <relatedStateVariable>Target</relatedStateVariable>
                    <direction>out</direction>
                </argument>
            </argumentList>
        </action> 
        <action>
            <name>GetStatus</name>
            <argumentList>
                <argument>
                    <name>ResultStatus</name>
                    <relatedStateVariable>Status</relatedStateVariable>
                    <direction>out</direction>
                </argument>
            </argumentList>
        </action>
    </actionList>
    <serviceStateTable>
        <stateVariable sendEvents="no">
            <name>Target</name>
            <dataType>boolean</dataType>
            <defaultValue>0</defaultValue>
        </stateVariable> 
        <stateVariable sendEvents="yes">
            <name>Status</name>
            <dataType>boolean</dataType>
            <defaultValue>0</defaultValue>
        </stateVariable>
    </serviceStateTable>
    </scpd>
    """

    service = Service(xml_string)
    print(service)
