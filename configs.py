from xml.etree import ElementTree
import serial


#DRRG comm0 is read rain and accumulated rain values
DRRG_COMM_0 = b'\x01\x03\x00\x00\x00\x10\x44\x06'
#DSG comm0 is read water level
DSG_COMM_0 = b'\x01\x03\x00\x00\x00\x02\xC4\x0B'


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

    if value in KEY_MAPPING.keys():
        value = KEY_MAPPING[value]
    else:
        if value.isdigit():
            value = int(value)
    # serial.Serial(**{key: value})
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
    tree = ElementTree.parse(file_path)
    section = tree.find(subfield)
    if section is None:
        return {}

    config = {}
    for item in section:
        config[item.tag] = verify_unique_xml_value(item.tag, item.text)
        if item.text.isdigit(): # if it's a digit cast it to int
            config[item.tag] = int(item.text)
    return config


def parse_string_config(file_path: str, subfield: str) -> str:
    """ Parse XML config where the target return type is a string instead of a dictionary.

    Args:
        file_path:`str` The filepath of the xml file.
        subfield:`str` The subfield that contains the string config.

    Returns:
        `str` the content of the subfield.
    """
    tree = ElementTree.parse(file_path)
    root = tree.getroot()

    for section in root:
        if section.tag == subfield:
            return section.text
    return ''
