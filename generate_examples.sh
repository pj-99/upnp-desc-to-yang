# Single service
python convert.py --device \
    --services \
        input/upnp_specs/home_automation/lighting_control/service/SwitchPower1.xml \
    --module binary-light \
    --output output/runs

# Multiple service
python convert.py --device \
    --services \
        input/upnp_specs/home_automation/lighting_control/service/Dimming1.xml \
        input/upnp_specs/home_automation/lighting_control/service/SwitchPower1.xml \
    --module dimmable-light \
    --output output/runs

# Multiple service with config file
python convert.py --config input.yaml \
    --output output/runs

# Ungroup
python convert.py --ungroup output/runs/binary-light.yang \
    --output-path output/runs/binary-light-ungrouped.yang