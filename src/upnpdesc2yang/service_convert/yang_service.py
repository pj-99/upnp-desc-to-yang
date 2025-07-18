import copy
import json
from contextlib import redirect_stdout
from textwrap import dedent
from typing import Dict, List, Tuple

from common.case_helper import to_enum_upper_case
from common.util import format
from yang_template import get_enums_block

from .service import Service
from .type_convert import upnp_to_yang_type, upnp_type_to_python_type


class YangService:
    """UPnP service description by YANG"""

    def __init__(self, spec_version, rpcs, service_state_table, service_name=""):
        self.spec_version = spec_version
        self.rpcs = rpcs
        self.service_state_table = service_state_table
        self.namespace = f"http://example.com/upnp-yang-schema/{service_name}"
        self.service_name = service_name

    def __repr__(self) -> str:
        str_yang = f"""
        module {self.service_name} {{
            {module_info_str(self.namespace, self.service_name)}
            
            {self.groupings()}
            uses {self.service_name}-top;
        }}
        """
        formatted_str = ""
        ident = 0
        stack = []
        space = 0
        for line in str_yang.split("\n"):
            if line.strip() == "":
                if space >= 1:
                    continue
                else:
                    space += 1
            else:
                space = 0

            if "{" in line:
                formatted_str += "  " * ident + line.strip()
                stack.append("{")
                ident += 1
            elif "}" in line:
                stack.pop()
                ident -= 1
                formatted_str += "  " * ident + line.strip()
            else:
                formatted_str += "  " * ident + line.strip()
            formatted_str += "\n"
        return formatted_str

    def groupings(self) -> str:
        """All groupings definitions for the service"""

        grouping_service_top = f"""
        grouping {self.service_name}-top {{
            description "Service top";
            
            container {self.service_name} {{
                description "Service";
            
                uses {self.service_name}-state-top;
                uses {self.service_name}-state-attributes-top;
                uses {self.service_name}-action;
            }}
        }}
        """

        return f"""
        {self.state_table_top_grouping()}
        {self.state_table_attribute_top_grouping()}
        {self.service_action_grouping()}
        {grouping_service_top}
        """

    def groupings_and_names(self) -> Tuple[str, str]:
        print("groupings_and_names: ", f"{self.service_name}-top")
        return self.groupings(), f"{self.service_name}-top"

    def service_state_table_leaves(self):
        def bool_str_if_need(default_val):
            if type(default_val) is bool:
                return "true" if default_val else "false"
            return default_val

        content_str = ""
        for state_dict in self.service_state_table:
            allowed_range = state_dict.get("allowedValueRange", {})
            leaf = leaf_str(
                {
                    "name": format(state_dict["name"]),
                    "type": state_dict["type"],  # TODO
                    "description": f'{state_dict["name"]}',
                    "default": bool_str_if_need(state_dict["default"]),
                    "config": state_dict["config"],
                    "range": (
                        {
                            "max": allowed_range.get("maximum", "max"),
                            "min": allowed_range.get("minimum", "min"),
                        }
                        if state_dict["allowedValueRange"]
                        else None
                    ),
                    "enum": state_dict.get("allowedValueList", None),
                }
            )
            content_str += "\n" + leaf
        return content_str

    def service_state_table_attr_leaves(self):
        content_str = ""
        for state_dict in self.service_state_table:
            content_str += f"""
            container {format(state_dict["name"])} {{
                description "Variable attributes";
                uses state-variable-attributes;
            }}
            
            """
        return content_str

    def service_action_grouping(self):
        content_str = "\n".join([str(rpc) for rpc in self.rpcs])
        return f"""
        grouping {self.service_name}-action {{
            description "Service actions";
            {content_str}
        }}
        """

    def state_table_top_grouping(self):
        return f"""
        grouping {self.service_name}-state-top {{
            description "State table";
            container state {{
                description "State table";
                {self.service_state_table_leaves()}  
            }}
        }}
        """

    def state_table_attribute_top_grouping(self):
        return f"""
        grouping {self.service_name}-state-attributes-top {{
            description "Table attributes";
            container state-attributes {{
                config false;
                description "Read-only attributes";
                {self.service_state_table_attr_leaves()}  
            }}
        }}
        """

    def switch_service_action_grouping(self):
        return f"""
        grouping {self.service_name}-action-top {{
            description "Service actions";
            container action {{
                config false;
                description "Service action";
                {self.service_state_table_attr_leaves()}  
            }}
        }}
        """

    def dump_data_json(self):
        """
        Dump the data (configuration, state) of the service in JSON format
        This is for using with `gnmi`. The output json can be the config data.
        """
        dump_obj = copy.deepcopy(self)

        dump_obj.service_state_table = self.service_state_table_json_obj()
        rename_attr_by_dash_case(dump_obj, "spec_version")

        dump_obj.service_state_table_attributes = (
            self.service_state_table_attr_json_obj()
        )

        excluded_attrs = ["rpcs", "service_name", "namespace"]
        for k in excluded_attrs:
            delattr(dump_obj, k)

        # Convert all remaining attributes to dash-case
        dash_case_obj = {}
        for key, value in dump_obj.__dict__.items():
            dash_key = key.lower().replace("_", "-")
            dash_case_obj[dash_key] = value

        # Wrap with a container because of the OpenConfig gNMI convention
        wrapped = {f"{self.service_name}:{self.service_name}": dash_case_obj}
        return json.dumps(wrapped, default=lambda o: o.__dict__, indent=2)

    def service_state_table_json_obj(self):
        """
        Convert the service state table to the obj for `gnmi`.
        The state variable value will use the default if it can
        """
        service_state_table = {}
        for state_var in self.service_state_table:
            # Based on the type and default value
            service_state_table[format(state_var["name"])] = (
                state_var["default"] if state_var["default"] is not None else "#TODO"
            )

        return service_state_table

    def service_state_table_attr_json_obj(self):
        """
        Convert the service state table attributes to the obj for `gnmi`.
        """
        service_state_table = {}
        for state_var in self.service_state_table:
            # Based on the type and default value
            service_state_table[format(state_var["name"])] = {
                "send-events": state_var["sendEvents"],
            }

        return service_state_table


def module_info_str(namespace, service_name):
    return f"""\
    yang-version 1.1;
    
    namespace "{namespace}";
    
    prefix "{service_name}";

    organization "upnp-yang-test";

    contact "upnp-yang-test";

    description
        "UPnP service module";

    revision 2024-06-27 {{
        reference "RFC 8407";
    }}
    
    """


def leaf_str(leaf):
    def get_default_state(default_value):
        return "" if default_value is None else f"default {default_value};"

    def get_type_block(leaf) -> str:
        """
        Return the type block containing default
        """
        # REFACTOR: improve readability
        type_block = ""
        if leaf.get("leafref"):
            type_block = f"""type leafref {{
                    path "{leaf["leafref"]}";
                }}"""
        elif leaf.get("range"):
            type_block = f"""type {leaf['type']} {{
                    range "{leaf['range']['min']} .. {leaf['range']['max']}";
                }}"""
            type_block += "\n" + get_default_state(leaf.get("default"))
        elif leaf.get("enum"):
            type_block = get_enums_block(leaf["enum"])
            if leaf.get("default"):
                type_block += "\n" + get_default_state(
                    to_enum_upper_case(leaf.get("default"))
                )
        else:
            type_block = f"type {leaf['type']};"
            type_block += "\n" + get_default_state(leaf.get("default"))
        return type_block

    type_line = get_type_block(leaf)

    config_line = "" if leaf.get("config", "false") else "config false;"
    desc_line = f'description "{leaf["description"]}";'

    all_lines = [type_line, config_line, desc_line]
    content = "\n".join(filter(lambda line: len(line) > 0, all_lines))

    leaf = f"""leaf {leaf['name']} {{
            {content}
            }}"""

    return leaf


def rename_attr_by_dash_case(instance, attr_name):
    dash_case = "-".join(list(map(lambda x: x.lower(), attr_name.split("_"))))
    setattr(instance, dash_case, getattr(instance, attr_name))
    delattr(instance, attr_name)


class YangRpc:
    def __init__(self, name, description, inputs, outputs):
        self.name = format(name)
        self.description: str = description
        self.inputs: None | List[Dict[str, str]] = inputs
        self.outputs: None | List[Dict[str, str]] = outputs

    def leaf_str(self, input):
        if input["direction"] == "out":
            leafref = f"../../state/{format(input['relatedStateVariable'])}"
        else:  # Input cannot be constrained
            leafref = None
        return leaf_str(
            {
                "name": format(input["name"]),
                "type": input["type"],
                "description": f"Related to {input['relatedStateVariable']}",
                "leafref": leafref,
            }
        )

    def create_in_out_str(self, items, is_input):
        container_name = "input" if is_input else "output"
        str_block = "\n".join([self.leaf_str(item) for item in items])

        block = dedent(
            f"""\
{container_name} {{
    {str_block}
}}"""
        )
        return block

    def __repr__(self) -> str:
        input_str = ""
        output_str = ""
        if self.inputs and len(self.inputs) > 0:
            input_str = self.create_in_out_str(self.inputs, is_input=True)
        if self.outputs and len(self.outputs) > 0:
            output_str = self.create_in_out_str(self.outputs, is_input=False)

        return dedent(
            f"""\
action {self.name} {{
    description "{self.description}";
    {input_str}
    {output_str}
}}
        """
        )


def parse_upnp_data_val(val_type: type, val: str) -> type:
    if val_type is bool:
        return val == "1"
    return val_type(val)


def convert_service_to_yang(service: Service) -> YangService:
    # Mapping state variable name to data type
    state_var_to_type = {}

    # To check if a state variable has setter(configurable)
    has_setter = {}
    for action in service.actions:
        if action["name"].startswith("Set"):
            var_name = action["name"][3:]
            has_setter[var_name] = True

    # Convert service state table
    state_table = []
    for state_var in service.state_variables:
        state_var_name = state_var["name"].strip()

        # Create python type value in default
        val_type = upnp_type_to_python_type(state_var["dataType"])
        default_val = (
            parse_upnp_data_val(val_type, state_var["defaultValue"])
            if state_var["defaultValue"] is not None
            else None
        )
        configurable = has_setter.get(state_var["name"], False)

        # REFACTOR: the following code duplicates
        state_table.append(
            {
                "name": state_var_name,
                "type": upnp_to_yang_type(state_var["dataType"]),
                "default": default_val,
                "sendEvents": state_var["sendEvents"] == "yes",
                "config": configurable,
                "allowedValueRange": state_var["allowedValueRange"],
                "allowedValueList": state_var["allowedValueList"],
            }
        )

        # For rpc lookup related state variable type
        state_var_to_type[state_var_name] = state_var["dataType"]

    # Convert rpc
    rpcs = []
    for action in service.actions:
        inputs = list(filter(lambda arg: arg["direction"] == "in", action["arguments"]))
        for item in inputs:
            item["type"] = upnp_to_yang_type(
                state_var_to_type[item["relatedStateVariable"]]
            )

        outputs = list(
            filter(lambda arg: arg["direction"] == "out", action["arguments"])
        )
        for item in outputs:
            item["type"] = upnp_to_yang_type(
                state_var_to_type[item["relatedStateVariable"]]
            )

        rpc = YangRpc(
            name=action["name"],
            description=f"Action {action['name']}",
            inputs=inputs,
            outputs=outputs,
        )
        rpcs.append(rpc)
    return YangService(
        spec_version=service.spec_version,
        rpcs=rpcs,
        service_state_table=state_table,
        service_name=format(service.service_name),
    )


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

    yang_service = convert_service_to_yang(service)

    with open("output-service.yang", "w") as f:
        with redirect_stdout(f):
            str_yang = str(yang_service)
            ident = 0
            stack = []
            space = 0
            for line in str_yang.split("\n"):
                if line.strip() == "":
                    if space >= 1:
                        continue
                    else:
                        space += 1
                else:
                    space = 0

                if "{" in line:
                    print("  " * ident + line.strip())
                    stack.append("{")
                    ident += 1
                elif "}" in line:
                    stack.pop()
                    ident -= 1
                    print("  " * ident + line.strip())
                else:
                    print("  " * ident + line.strip())
