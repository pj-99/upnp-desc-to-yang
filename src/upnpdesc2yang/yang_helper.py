# Refactor
import unittest
from dataclasses import dataclass, field

import common.util as util
from yang_template import get_send_events_grouping, get_state_var_attr_grouping


class YangHelperTest(unittest.TestCase):
    def test_create_leaf(self):
        leaf = YangLeaf(
            name="example",
            type="string",
            description="this is a description",
            default="hello",
            configurable=False,
        )
        expected = util.format_yang(
            """
            leaf example {
                type string;
                config false;
                default "hello";
                description "this is a description";
            }
            """
        )
        self.assertMultiLineEqual(str(leaf), expected.strip())

    def test_create_container(self):
        content = util.format_yang(
            """
            leaf example {
                type string;
                config false;
                default "hello";
                description "this is a description";
            }
        """
        )
        container = YangContainer(
            name="example_cont",
            configurable=True,
            content=content,
            description="this is a desc",
        )
        expected = util.format_yang(
            """
            container example_cont {
                description "this is a desc";
                leaf example {
                    type string;
                    config false;
                    default "hello";
                    description "this is a description";
                }
            }
        """
        )
        self.assertMultiLineEqual(str(container), expected.strip())

    def test_container_add_child(self):
        container = YangContainer(
            name="example_cont",
            configurable=True,
            description="this is a desc",
        )
        leaf = YangLeaf(
            name="example",
            type="string",
            description="this is a description",
            default="hello",
            configurable=False,
        )
        container.add_child(leaf)
        expected = util.format_yang(
            """
            container example_cont {
                description "this is a desc";
                leaf example {
                    type string;
                    config false;
                    default "hello";
                    description "this is a description";
                }
            }
        """
        )
        self.assertMultiLineEqual(str(container), expected.strip())

    def test_yang_module(self):
        container = YangContainer(
            name="example_cont",
            configurable=True,
            description="this is a desc",
        )
        leaf = YangLeaf(
            name="example",
            type="string",
            description="this is a description",
            default="hello",
            configurable=False,
        )
        container.add_child(leaf)

        ns = "namespace_here"
        name = "test"
        module = YangModule(name, ns, str(container))
        expected = util.format_yang(
            """
            module test {
                yang-version 1.1;

                namespace "namespace_here";
                
                prefix "test";

                organization "upnp-yang-test";

                contact "upnp-yang-test";

                description
                    "Transform from UPnP";

                revision 2024-06-27 {
                    reference "RFC 8407";
                }   
                
                container example_cont {
                    description "this is a desc";
                    leaf example {
                        type string;
                        config false;
                        default "hello";
                        description "this is a description";
                    }
                }
            }
        """
        )
        self.assertMultiLineEqual(str(module), expected.strip())


@dataclass
class YangContainer:
    name: str
    configurable: bool = True
    description: str = None
    content: str = None
    _repr: str = ""
    children: list = field(default_factory=list)

    def __post_init__(self):
        self._update_repr()

    def _update_repr(self):
        self._repr = util.format_yang(
            f"""
                container {self.name} {{
                    description "{self.description}";
                    {self.content}  
            }}
            """
        )

    def __repr__(self):
        return self._repr

    def add_child(self, child):
        self.children.append(child)
        self.content = "\n".join(map(str, self.children))
        self._update_repr()


# Refactor: use OOP like by these class
@dataclass
class YangLeaf:
    name: str
    configurable: bool = True
    description: str = None
    type: str = None
    default: str = None
    leafRef: str = None
    range: str = None
    _repr: str = ""

    def __post_init__(self):
        leaf_content = [f"type {self.type};"]

        if not self.configurable:
            leaf_content.append("config false;")
        if self.default is not None:
            leaf_content.append(f'default "{self.default}";')
        if self.leafRef is not None:
            leaf_content.append(f'leafRef "{self.leafRef}";')
        if self.range is not None:
            leaf_content.append(f'range "{self.range}";')

        leaf_content.append(f'description "{self.description}";')

        content = "\n                ".join(leaf_content)

        self._repr = util.format_yang(
            f"""
            leaf {self.name} {{
                {content}
            }}
            """
        )

    def __repr__(self):
        return self._repr


@dataclass
class YangModule:
    name: str
    namespace: str
    content: str
    module_info_str: str = None

    def __post_init__(self):
        import_str = ""
        if "inet:" in self.content:
            import_str += """\n
            import ietf-inet-types {
                prefix inet;
            }
            """
        if "yang:" in self.content:
            import_str += """\n
            import ietf-yang-types {
                prefix yang;
            }
            """
        self._set_module_info_str(import_str)

    def _set_module_info_str(self, import_str=None):
        self.module_info_str = f"""\
        yang-version 1.1;

        namespace "{self.namespace}";
        
        prefix "{self.name}";

        {import_str} 

        organization "upnp-yang-test";

        contact "upnp-yang-test";

        description
            "{self.name}";

        revision 2024-06-27 {{
            reference "RFC 8407";
        }}    
        """

    def __repr__(self):

        # # common meta-data groupings
        meta_data_content = "\n".join(
            [get_send_events_grouping(), get_state_var_attr_grouping()]
        )
        return util.format_yang(
            f"""
            module {self.name} {{
                {self.module_info_str}        
                {self.content}
                {meta_data_content}
            }}
            """
        )


class YangHelper:
    @classmethod
    def create_leaf():
        return


if __name__ == "__main__":
    unittest.main()
