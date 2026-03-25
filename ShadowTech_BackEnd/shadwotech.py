import subprocess
import re
import time
import matplotlib.pyplot as plt

#########################
# Plug in Rooted Android
# Enable Wireled USB Debugging (Should pop up, otherwise check dev settings)
# If both phone and computer turn off plug the phone in and repeat the first two steps

PATTERN = re.compile(
    r"rssi=(-?\d+)\s+"
    r"rsrp=(-?\d+)\s+"
    r"rsrq=(-?\d+)\s+"
    r"rssnr=(-?\d+)"
)

CELL_PATTERN = re.compile(r"(pci|earfcn|nrarfcn|ci|nci)=([0-9]+)")

RRC_PATTERN = re.compile(r"mRrcState=(\w+)")

timestamps = []
rssi_vals = []
rsrp_vals = []
rsrq_vals = []
rssnr_vals = []
current_cell = {}
last_cell = {}
rrc_state = None

plt.ion()
fig, ax = plt.subplots()

proc = subprocess.Popen(
    ["adb", "shell", "dumpsys", "telephony.registry"],
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True,
)

while True:
    # re-run dumpsys every second
    output = subprocess.check_output(
        ["adb", "shell", "dumpsys", "telephony.registry"],
        text=True,
        stderr=subprocess.DEVNULL,
    )

    for line in output.splitlines():
        if "mSignalStrength=" not in line:
            continue

        match = PATTERN.search(line)
        if not match:
            continue

        rssi, rsrp, rsrq, rssnr = map(int, match.groups())
        t = time.time()

        timestamps.append(t)
        rssi_vals.append(rssi)
        rsrp_vals.append(rsrp)
        rsrq_vals.append(rsrq)
        rssnr_vals.append(rssnr)

    # keep last 100 points
    timestamps[:] = timestamps[-100:]
    rssi_vals[:] = rssi_vals[-100:]
    rsrp_vals[:] = rsrp_vals[-100:]
    rsrq_vals[:] = rsrq_vals[-100:]
    rssnr_vals[:] = rssnr_vals[-100:]

    ax.clear()
    # ax.plot(timestamps, rssi_vals, label="RSSI")
    ax.plot(timestamps, rsrp_vals, label="RSRP")
    # ax.plot(timestamps, rsrq_vals, label="RSRQ")
    # ax.plot(timestamps, rssnr_vals, label="RSSNR")

    ax.set_title("Live RSRP Readings")
    ax.legend()
    ax.grid(True)

    plt.pause(0.1)
    time.sleep(0.1)
