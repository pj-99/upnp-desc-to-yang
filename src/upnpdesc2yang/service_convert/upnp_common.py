"""Common part of UPnP service description to YANG"""


def upnp_common_groupings():
    """spec version and state variable attribute of UPnP service description to YANG"""
    return _upnp_state_var_attr_grouping()


def _upnp_state_var_attr_grouping():
    return """
    grouping state-variable-attributes {
        description "upnp state variable attributes";
        uses send-events-grouping;
    }
    """


def _upnp_spec_version_grouping():
    return """
    grouping upnp-spec-version-top {
        description "upnp specVersion grouping";
        container spec-version {
            config false;
            description "upnp spec version";
            
            leaf major {
                type uint8;
                default 1;
                description "upnp specVersion.major";
            }

            leaf minor {
                type uint8;
                default 0;
                description "upnp specVersion.minor";
            }
        }
    }
    """
