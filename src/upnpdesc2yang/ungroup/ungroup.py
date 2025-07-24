# Un-grouping the yang file and make the content smaller
from upnpdesc2yang.common import util


class Grouping:
    def __init__(self, name, content):
        self.name = name
        self.content = content

    def __str__(self):
        return f"Grouping {self.name}:\n{self.content}"


def replace_top_level_grouping(yang_content, grouping_map, level=1, exclude=[]):
    have_use = False
    for line in yang_content.split("\n"):
        if line.strip().startswith("uses"):
            # Check if the grouping is in the exclude list
            grouping = line.split()[1][:-1]
            if grouping in exclude:
                continue

            have_use = True
    if not have_use:
        return yang_content

    # Replace "uses ${grouping}" with grouping content
    lines = yang_content.split("\n")
    brace_count = 0
    new_lines = []
    for line in lines:
        if "{" in line:
            brace_count += 1
        if "}" in line:
            brace_count -= 1
        # Note that only replace top level grouping!
        if line.strip().startswith("uses") and brace_count == level:
            # the -1 removed the ";" in the end
            grouping_name = line.split()[1][:-1]
            grouping_def = grouping_map[grouping_name]
            grouping_content = util.extract_grouping_content(grouping_def)
            new_lines.append(grouping_content)
        else:
            new_lines.append(line)

    new_content = "\n".join(new_lines)

    return replace_top_level_grouping(new_content, grouping_map, level + 1, exclude)


def ungroup(yang_content, exclude_grouping=["send-events-grouping"]):
    grouping_map, clean_content = util.extract_groupings(yang_content, exclude_grouping)
    content = replace_top_level_grouping(
        clean_content, grouping_map, 1, exclude_grouping
    )
    formatted = util.format_yang(content)
    return formatted


def minify(yang_content):
    lines = yang_content.splitlines()
    content = []
    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith("//"):
            continue
        content += [line]
    return "\n".join(content)


if __name__ == "__main__":
    yang_file_name = "light-device.yang"
    with open(yang_file_name, "r") as f:
        yang_content = f.read()

    output = ungroup(yang_content)
    # Write output to file
    minified = minify(output)

    with open("light-device-ungrouped.yang", "w") as f:
        f.write(output)

    with open("minified.yang", "w") as f:
        f.write(minified)
