import pytest

from scripts.screencam_metrics import cpu_percent, decode_marker, marker, packet_bitrate, summary


@pytest.mark.parametrize('stamp', [0, 1, 1789876543210, 2**48 - 1])
def test_timestamp_roundtrip(stamp):
    assert decode_marker(marker(stamp)) == stamp


def test_marker_rejects_corruption_and_non_marker():
    code = bytearray(marker(1789876543210))
    code[8 * 896 + 8] = 128
    assert decode_marker(code) is None
    assert decode_marker(bytes(896 * 32)) is None
    assert decode_marker(b'') is None


def test_checksum_detects_valid_cells_with_changed_bit():
    code = bytearray(marker(1789876543210))
    for row in range(32):
        for column in range(16):
            offset = row * 896 + column
            code[offset] = 255 - code[offset]
    assert decode_marker(code) is None


def test_summary_units_and_nearest_rank():
    result = summary(list(range(1, 101)))
    assert result == {'count': 100, 'mean': 50.5, 'p95': 95, 'max': 100}
    assert summary([])['p95'] is None


def test_cpu_one_core_and_pid_reuse():
    previous = {'time': 10, 'ticks': 100, 'start_ticks': 5}
    current = {'time': 12, 'ticks': 200, 'start_ticks': 5}
    assert cpu_percent(previous, current, 100) == 50
    current['start_ticks'] = 6
    assert cpu_percent(previous, current, 100) is None


def test_packet_bitrate_accounts_for_media_time_not_wall_buffering():
    result = packet_bitrate([{'pts_time': '0.0', 'size': '1000'},
                             {'pts_time': '0.1', 'size': '2000'},
                             {'pts_time': '0.2', 'size': '9999'}])
    assert result['kbit_s'] == 120
    assert packet_bitrate([]) is None
