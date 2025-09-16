from data import FLOOD_FORMAT, RAIN_DATA_FORMAT, RAIN_ACCU_FORMAT, get_zeroes_from, fill_zeroes


def test_data_format():
    assert get_zeroes_from(FLOOD_FORMAT) == ("00000", "")
    assert get_zeroes_from(RAIN_DATA_FORMAT) == ("0000", "00")

def test_fill_zeroes():
    n = float("12.1")
    expected = "001210"
    assert fill_zeroes(n, RAIN_DATA_FORMAT) == expected
    n = "0.00012"
    expected = "0000" + "00012" + "000000000000"
    assert fill_zeroes(n, RAIN_ACCU_FORMAT) == expected

def test_fill_zeroes2():
    n = float("12.1")
    expected = "001210"
    assert fill_zeroes(n, RAIN_DATA_FORMAT) == expected
    n = "0.00012"
    expected = "0000" + "00012" + "000000000000"
    assert fill_zeroes(n, RAIN_ACCU_FORMAT) == expected
    n = "1234.2"
    expected = "123420"
    assert fill_zeroes(n, RAIN_DATA_FORMAT) == expected
    n = "1234.56"
    expected = "123456"
    assert fill_zeroes(n, RAIN_DATA_FORMAT) == expected
