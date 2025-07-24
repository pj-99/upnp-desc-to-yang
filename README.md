# UPnP descriptions to YANG Converter

[![Test](https://github.com/pj-99/upnp-desc-to-yang/actions/workflows/test.yml/badge.svg)](https://github.com/pj-99/upnp-desc-to-yang/actions/workflows/test.yml)

Convert UPnP service and device descriptions to YANG modules (RFC 7950).

## Usage

### Service to Module
Convert a single UPnP service to YANG module:

```bash
python convert.py --service <service.xml> --module <module_name>
```

**Example:**
```bash
python convert.py --service input/upnp_specs/home_automation/lighting_control/service/SwitchPower1.xml --module switch-power
```

### Device to Module
Convert UPnP device with services to YANG module:

```bash
# Single service
python convert.py --device --services <service.xml> --module <module_name>

# Multiple services  
python convert.py --device --services <serviceA.xml> <serviceB.xml> --module <module_name>
```

**Examples:**
```bash
# Binary light (single service)
python convert.py --device \
    --services input/upnp_specs/home_automation/lighting_control/service/SwitchPower1.xml \
    --module binary-light \
    --output output/runs

# Dimmable light (multiple services)
python convert.py --device \
    --services input/upnp_specs/home_automation/lighting_control/service/Dimming1.xml \
               input/upnp_specs/home_automation/lighting_control/service/SwitchPower1.xml \
    --module dimmable-light \
    --output output/runs
```

### Device with Embedded Devices
Convert complex device structures using configuration file:

```bash
python convert.py --config <config.yaml> --output <output_dir>
```

**Example:**
```bash
python convert.py --config input.yaml --output output/runs
```

> See `input.yaml` for configuration structure.

### Ungrouping
Remove `grouping` and `uses` statements while preserving structure:

```bash
python convert.py --ungroup <input.yang> --output-path <output.yang>
```

**Example:**
```bash
python convert.py --ungroup output/runs/binary-light.yang --output-path output/runs/binary-light-ungrouped.yang
```

## Pyang Utilities

Useful commands for working with generated YANG modules:

```bash
# Validate syntax
pyang --lint <module.yang>

# Generate tree view
pyang -f tree <module.yang>
```