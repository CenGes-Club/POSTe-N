from xml.etree import ElementTree
import serial


KEY_MAPPING = {
    'PARITY_NONE': serial.PARITY_NONE,
    'PARITY_ODD': serial.PARITY_ODD,
    'PARITY_EVEN': serial.PARITY_EVEN,
    'PARITY_MARK': serial.PARITY_MARK,
    'PARITY_SPACE': serial.PARITY_SPACE,

    'STOPBITS_ONE': serial.STOPBITS_ONE,
    'STOPBITS_ONE_POINT_FIVE': serial.STOPBITS_ONE_POINT_FIVE,
    'STOPBITS_TWO': serial.STOPBITS_TWO,

    'FIVEBITS': serial.FIVEBITS,
    'SIXBITS': serial.SIXBITS,
    'SEVENBITS': serial.SEVENBITS,
    'EIGHTBITS': serial.EIGHTBITS
}

def verify_unique_xml_value(key, value):
    # if key not in ('parity', 'stopbits', 'bytesize'):
    #     return
    if value in KEY_MAPPING.keys():  # wait, how does this make sense?
       value = KEY_MAPPING[value]
    serial.Serial(**{key: value})
    return value


def _read_config(file_path):
    tree = ElementTree.parse(file_path)
    root = tree.getroot()

    config = {}

    # Loop through top-level elements
    for section in root:
        section_dict = {}
        for item in section:
            section_dict[item.tag] = item.text
        config[section.tag] = section_dict

    return config


def parse_serial_config(file_path, subfield) -> dict:  # `subfield` needs to be renamed
    config = _read_config(file_path)
    for root in config:
        for section_key in config[root]:
            section = config[root]
            if section[section_key].isdigit() is True: # if it's a digit cast it to int
                section[section_key] = int(section[section_key])
            section[section_key] = verify_unique_xml_value(section_key, section[section_key])
    return config[subfield]


def parse_string_config(file_path, subfield) -> str:
    """ Parse XML config where the target return type is a string instead of a dictionary.

    Args:
        file_path:
        subfield:

    Returns:
        `str` the content of the subfield.
    """
    pass
