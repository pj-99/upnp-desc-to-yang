from pathlib import Path

from src.upnpdesc2yang.converter import convert_service


def handle_upnp_spec_file(input_service_file, module_name):
    service_path = Path(input_service_file)

    # Generate files under output folder, and use new module name
    output_dir = Path("output") / service_path.parent.relative_to("input")

    output_path = output_dir / (module_name + ".yang")

    output = convert_service(module_name, input_service_file, minify=False)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(output)
    print("Written to", output_path)


if __name__ == "__main__":
    main()
