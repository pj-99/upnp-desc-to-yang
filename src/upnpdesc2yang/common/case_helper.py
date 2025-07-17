import re


def to_enum_upper_case(upper_camel_case):
    """
    Given: OnEffectLevel or Manual UnProtected
    Return: ON_EFFECT_LEVEL or MANUAL_UN_PROTECTED
    """
    # Remove the space
    upper_camel_case = upper_camel_case.replace(" ", "")

    # Insert the underscore whenever we find a lower followed by an upper
    result = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", upper_camel_case)
    return result.upper()
