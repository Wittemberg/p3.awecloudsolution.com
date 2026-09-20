"""Synthetic visual timestamp and measured decoder arrival latency (same host clock)."""

import argparse
import json
import math
import os
from pathlib import Path
import selectors
import subprocess
import sys
import time
from urllib.parse import quote

try:
    from .screencam_config import load_config
except ImportError:
    from screencam_config import load_config


WIDTH, HEIGHT, CELL = 896, 32, 16
FRAME_SIZE = WIDTH * HEIGHT


def marker(timestamp_ms):
    raw = timestamp_ms.to_bytes(6, "big")
    checksum = 0
    for value in raw:
        checksum ^= value
    bits = ''.join(f'{value:08b}' for value in raw + bytes([checksum]))
    row = b''.join(bytes([255 if bit == '1' else 0]) * CELL for bit in bits)
    inverse = bytes(255 - value for value in row)
    return row * 16 + inverse * 16


def decode_marker(frame):
    if len(frame) != FRAME_SIZE:
        return None
    bits = []
    for column in range(56):
        top = frame[8 * WIDTH + column * CELL + CELL // 2]
        bottom = frame[24 * WIDTH + column * CELL + CELL // 2]
        if top > 192 and bottom < 64:
            bits.append('1')
        elif top < 64 and bottom > 192:
            bits.append('0')
        else:
            return None
    raw = bytes(int(''.join(bits[i:i + 8]), 2) for i in range(0, 56, 8))
    checksum = 0
    for value in raw[:6]:
        checksum ^= value
    return int.from_bytes(raw[:6], "big") if checksum == raw[6] else None


def summary(values):
    if not values:
        return {"count": 0, "mean": None, "p95": None, "max": None}
    ordered = sorted(values)
    return {"count": len(values), "mean": round(sum(values) / len(values), 3),
            "p95": round(ordered[math.ceil(len(values) * 0.95) - 1], 3),
            "max": round(ordered[-1], 3)}


def process_sample(pid):
    # /proc stat comm may contain spaces and parentheses; fields start after final ')'.
    fields = Path(f"/proc/{pid}/stat").read_text().rsplit(')', 1)[1].split()
    return {"time": time.monotonic(), "ticks": int(fields[11]) + int(fields[12]),
            "start_ticks": int(fields[19]), "rss_bytes": int(fields[21]) * os.sysconf('SC_PAGE_SIZE')}


def cpu_percent(previous, current, ticks_per_second):
    elapsed = current["time"] - previous["time"]
    if current["start_ticks"] != previous["start_ticks"] or elapsed <= 0:
        return None
    delta = current["ticks"] - previous["ticks"]
    return 100 * delta / ticks_per_second / elapsed if delta >= 0 else None


def packet_bitrate(packets):
    samples = [(float(packet['pts_time']), int(packet['size'])) for packet in packets
               if 'pts_time' in packet and 'size' in packet]
    samples.sort()
    if len(samples) < 2 or samples[-1][0] <= samples[0][0]:
        return None
    span = samples[-1][0] - samples[0][0]
    if any(size < 0 or not math.isfinite(pts) for pts, size in samples):
        return None
    return {'kbit_s': round(sum(size for _, size in samples[:-1]) * 8 / span / 1000, 3),
            'media_span_s': round(span, 3), 'packets': len(samples),
            'method': 'elementary video payload; last packet excluded; network overhead excluded'}


def source():
    # Timestamp generated before presentation. Measured latency includes ffplay and encoder/decoder buffers.
    number = 0
    deadline = time.monotonic()
    while True:
        pixels = bytearray(bytes([30 + number % 150]) * (1280 * 720))
        code = marker(int(time.time() * 1000))
        for row in range(HEIGHT):
            pixels[row * 1280:row * 1280 + WIDTH] = code[row * WIDTH:(row + 1) * WIDTH]
        sys.stdout.buffer.write(pixels)
        sys.stdout.buffer.flush()
        number += 1
        deadline += 0.1
        time.sleep(max(0, deadline - time.monotonic()))


def measure(config, pid, duration=10):
    host = config['host'] if ':' not in config['host'] else f"[{config['host']}]"
    user, password = (quote(config[key], safe='') for key in ('username', 'password'))
    url = f"rtsp://{user}:{password}@{host}:{config['port']}/{config['path']}"
    args = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-rtsp_transport', 'tcp',
            '-fflags', 'nobuffer', '-flags', 'low_delay', '-probesize', '32768',
            '-analyzeduration', '0', '-i', url, '-an', '-vf', f'crop={WIDTH}:{HEIGHT}:0:0',
            '-pix_fmt', 'gray', '-f', 'rawvideo', 'pipe:1']
    latencies, gaps, cpu, rss, arrivals, stamps = [], [], [], [], [], []
    invalid = 0
    previous = None
    start = time.monotonic()
    buffer = b''
    process = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                               stderr=subprocess.DEVNULL)
    try:
        with selectors.DefaultSelector() as selector:
            os.set_blocking(process.stdout.fileno(), False)
            selector.register(process.stdout, selectors.EVENT_READ)
            while time.monotonic() - start < duration:
                if previous is None or time.monotonic() - previous['time'] >= 1:
                    current = process_sample(pid)
                    rss.append(current['rss_bytes'])
                    if previous:
                        percent = cpu_percent(previous, current, os.sysconf('SC_CLK_TCK'))
                        if percent is not None:
                            cpu.append(percent)
                    previous = current
                for key, _ in selector.select(timeout=0.1):
                    data = os.read(key.fileobj.fileno(), 65536)
                    if not data:
                        raise RuntimeError('decoder ended before measurement finished')
                    buffer += data
                    while len(buffer) >= FRAME_SIZE:
                        frame, buffer = buffer[:FRAME_SIZE], buffer[FRAME_SIZE:]
                        now = time.monotonic()
                        stamp = decode_marker(frame)
                        arrivals.append(now)
                        if stamp is None or not 0 <= time.time() * 1000 - stamp < 60000:
                            invalid += 1
                            continue
                        latency = time.time() * 1000 - stamp
                        latencies.append(latency)
                        stamps.append(stamp)
                        if len(arrivals) > 1:
                            gaps.append((arrivals[-1] - arrivals[-2]) * 1000)
    finally:
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=3)
        process.stdout.close()
    elapsed = time.monotonic() - start
    delivered_fps = ((len(arrivals) - 1) / (arrivals[-1] - arrivals[0])
                     if len(arrivals) > 1 and arrivals[-1] > arrivals[0] else None)
    probe = subprocess.run(['ffprobe', '-v', 'error', '-rtsp_transport', 'tcp',
                            '-read_intervals', '%+3', '-select_streams', 'v:0', '-show_packets',
                            '-show_entries', 'packet=pts_time,size', '-of', 'json', url],
                           capture_output=True, text=True, timeout=20)
    bitrate = packet_bitrate(json.loads(probe.stdout).get('packets', [])) if probe.returncode == 0 else None
    return {'duration_s': round(elapsed, 3), 'decoded_frames': len(arrivals),
            'delivered_fps': delivered_fps, 'invalid_markers': invalid,
            'unique_markers': len(set(stamps)), 'latency_ms': summary(latencies),
            'arrival_gap_ms': summary(gaps), 'encoder_cpu_percent_one_core': summary(cpu),
            'encoder_rss_bytes': summary(rss),
            'video_payload_bitrate': bitrate,
            'latency_method': 'synthetic timestamp generation to decoded arrival; same host wall clock',
            'latency_includes': ['source presentation', 'capture', 'encode', 'transport', 'decode', 'buffering']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['source', 'measure'])
    parser.add_argument('--config')
    parser.add_argument('--pid', type=int)
    args = parser.parse_args()
    try:
        if args.mode == 'source':
            source()
        else:
            if args.pid is None or args.pid <= 0 or not args.config:
                parser.error('measure requires --pid and --config')
            print(json.dumps(measure(load_config(args.config), args.pid)))
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired):
        print('{"error":"measurement_failed"}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
