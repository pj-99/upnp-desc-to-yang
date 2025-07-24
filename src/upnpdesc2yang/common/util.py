import inspect
import unittest
from pathlib import Path

from xml.etree.ElementTree import Element


def find(e: Element, tag: str, namespace: dict):
    try:
        return e.find(f"{list(namespace.keys())[0]}:{tag}", namespace)
    except Exception as e:
        print("Error when find:" + f"{list(namespace.keys())[0]}:{tag}")
        raise e


def find_all(e: Element, tag: str, namespace: dict):
    try:
        return e.findall(f"{list(namespace.keys())[0]}:{tag}", namespace)
    except Exception as e:
        print("Error when find_all: ", f"{list(namespace.keys())[0]}:{tag}")
        raise e


def format(identifier: str):
    """Format identifier to yang format"""
    if "_" in identifier:
        return identifier.replace("_", "-").lower()

    # Insert '-' between words and convert to lower case
    new_identifier = ""
    for i, c in enumerate(identifier):
        if c.isupper() and i != 0:
            new_identifier += "-" + c.lower()
        else:
            new_identifier += c.lower()
    return new_identifier


def format_yang(str_yang):
    formatted_str = ""
    indent = 0
    indent_steps = 1
    stack = []
    for line in str_yang.split("\n"):
        if line.strip() == "":
            continue
        if "{" in line:
            formatted_str += "  " * indent + line.strip()
            stack.append("{")
            indent += indent_steps
        elif "}" in line:
            stack.pop()
            indent -= indent_steps
            formatted_str += "  " * indent + line.strip()
            formatted_str += "\n"
        else:
            formatted_str += "  " * indent + line.strip()
        formatted_str += "\n"

    content = formatted_str.strip()
    return content


class UtilTest(unittest.TestCase):
    def test_format_yang(self):
        input_str = """
            leaf example {
                type string;
                    config false;
                    default "hello";
                description "this is a description";
            }
        """
        actual = format_yang(input_str).strip()

        expected = inspect.cleandoc(
            """
            leaf example {
                type string;
                config false;
                default "hello";
                description "this is a description";
            }                  
            """
        ).strip()
        self.assertMultiLineEqual(actual, expected)


def extract_groupings(yang_content, exclude):
    """
    Extracts groupings from the given YANG content.

    Returns:
        dict: A dictionary where the keys are grouping names and the values are content.
        str: The cleaned YANG content without groupings.
    """
    groupings = {}
    lines = yang_content.split("\n")
    current_grouping = None
    current_content = []
    brace_count = 0

    cleaned_content = []

    for line in lines:
        stripped_line = line.strip()

        # Enter grouping and start counting braces
        # Count until braces are balanced
        if not current_grouping and stripped_line.startswith("grouping"):
            grouping_name = stripped_line.split()[1]
            if grouping_name not in exclude:
                current_grouping = grouping_name

        if current_grouping:
            current_content.append(line)
            if "{" in stripped_line:
                brace_count += 1
            if "}" in stripped_line:
                brace_count -= 1

            # If brace count is zero, we have reached the end of the grouping
            if brace_count == 0:
                groupings[current_grouping] = "\n".join(current_content)
                current_grouping = None
                current_content = []
        else:
            cleaned_content.append(line)
    cleaned_content = "\n".join(cleaned_content)
    return groupings, cleaned_content


def extract_grouping_content(grouping_definition):
    new_lines = []
    first_descriptions = False
    # Ignore the last line  "}"
    for line in grouping_definition.split("\n")[:-1]:
        # Remove line.strip() start with grouping
        if line.strip().startswith("grouping"):
            continue
        # Remove line.strip() start with "description"
        if not first_descriptions and line.strip().startswith("description"):
            first_descriptions = True
            continue
        new_lines.append(line)
    return "\n".join(new_lines)


def get_service_name_from_upnp_spec_file(service_xml_file_path: str):
    file_name = Path(service_xml_file_path).stem
    # Remove the `1` or `2` version string in service_name`
    if file_name[-1].isdigit() and file_name[-2].isalpha():
        return file_name[:-1]
    return file_name


if __name__ == "__main__":
    unittest.main()
