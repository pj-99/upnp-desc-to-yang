
# UPnP service and device description to YANG (RFC 7950)

[![Test](https://github.com/pj-99/upnp-desc-to-yang/actions/workflows/test.yml/badge.svg)](https://github.com/pj-99/upnp-desc-to-yang/actions/workflows/test.yml)
## Use case

**Convert a UPnP service into a single module**

Usage:
```sh
python convert.py --service [service.xml] --module [output_module_name]
```

Example:
```sh
python convert.py --service input/upnp_specs/home_automation/lighting_control/service/SwitchPower1.xml --module switch-power
```

**Convert a UPnP device with service(s) into a single module**
Usage:
```sh
# Single service
python convert.py --device --services [serviceA.xml] --module [output_module_name]
# Multiple services
python convert.py --device --services [serviceA.xml] [serviceB.xml] --module [output_module_name]
```

Example:
```sh
# Single service
python convert.py --device \
    --services \
        input/upnp_specs/home_automation/lighting_control/service/SwitchPower1.xml \
    --module binary-light

# Multiple service
python convert.py --device \
    --services \
        input/upnp_specs/home_automation/lighting_control/service/Dimming1.xml \
        input/upnp_specs/home_automation/lighting_control/service/SwitchPower1.xml \
    --module dimmable-light
```

**Convert a UPnP device with embed device(s) into a single module**

- See `input.yaml` for input structure

Usage
```sh
python convert.py --config [config.yaml]
```

Example:
```sh
python convert.py --config input.yaml
```



### Ungroup options


---

## Useful commands by Pyang

- Linting
- Output

---

## Test
