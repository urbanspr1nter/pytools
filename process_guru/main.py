import os
import datetime
import sys
import psutil
import time
import json

"""
@Author: urbanspr1nter@gmail.com
@Date: 2023-07-23
"""

"""
Constants defined to map configuration-based compute priority
to process priorities in which Windows can recognize and manage.
"""
priority_map = {
    "default": psutil.NORMAL_PRIORITY_CLASS,
    "realtime": psutil.REALTIME_PRIORITY_CLASS,
    "high": psutil.HIGH_PRIORITY_CLASS,
    "above normal": psutil.ABOVE_NORMAL_PRIORITY_CLASS,
    "normal": psutil.NORMAL_PRIORITY_CLASS,
    "background": psutil.BELOW_NORMAL_PRIORITY_CLASS,
    "idle": psutil.IDLE_PRIORITY_CLASS
}

"""
Same as compute priority, but for I/O
"""
io_priority_map = {
    "default": psutil.IOPRIO_NORMAL,
    "high": psutil.IOPRIO_HIGH,
    "normal": psutil.IOPRIO_NORMAL,
    "low": psutil.IOPRIO_LOW,
    "very low": psutil.IOPRIO_VERYLOW
}


def read_config(config_filename):
    """
    Reads a configuration file specified by `config_filename`.
    If the file does not exist, a default configuration will
    be returned.
    """
    default_config = {
        "forever": False,
        "polling_interval_seconds": 0,
        "processes": []
    }

    try:
        with open(config_filename, "r") as config_file:
            config_as_text = config_file.read()
            default_config = json.loads(config_as_text)
    except FileNotFoundError:
        pass

    return default_config


def get_process_config(name, process_configs):
    """
    A helper to get a process by name from the process configs
    """
    for current_process_config in process_configs:
        if current_process_config["name"] == name:
            return current_process_config

    return None


def govern_processes(process_configs):
    """
    Main process governor algorithm which gets the list of current PIDs
    and applies the specific configuration against them.
    """

    pid_list = psutil.pids()

    for pid in pid_list:
        if psutil.pid_exists(pid):
            p = psutil.Process(pid)

            found_process_config = get_process_config(p.name(), process_configs)
            if found_process_config is None:
                continue

            compute_priority = found_process_config["cpu_priority"]
            io_priority = found_process_config["io_priority"]

            p.cpu_affinity(found_process_config["cpu_affinity"])
            p.nice(priority_map[compute_priority])
            p.ionice(io_priority_map[io_priority])

            print(f'[{datetime.datetime.now()}]\t✔️ Process {found_process_config["name"]} PID={pid} managed.')


def detect_system_battery_state():
    """
    The system is considered to be on battery state if sensors_battery detects
    that `power_plugged` is False. True/NoneType will be considered AC power.
    """
    battery_stats = psutil.sensors_battery()
    on_ac_power = True

    if battery_stats is not None:
        on_ac_power = battery_stats.power_plugged

    return on_ac_power


def __main__():
    # Read the default config -- in the future, make this configurable
    configuration = read_config("config.json")

    # run_forever will indicate to continuously check for relevant processes to control
    run_forever = configuration["forever"]
    if type(run_forever) is not bool:
        print("specified configuration key [forever] must be value in: {true, false}")
        sys.exit(1)

    polling_interval_seconds = configuration["polling_interval_seconds"]
    if type(polling_interval_seconds) is not int:
        print("specified configuration key [polling_interval_seconds] must be an integer")
        sys.exit(1)

    processes = configuration["processes"]
    if len(processes) == 0:
        print("no processes to govern.")
        sys.exit(1)

    # First set up as high priority for this script...
    self_pid = os.getpid()
    self_p = psutil.Process(self_pid)
    self_p.nice(psutil.HIGH_PRIORITY_CLASS)

    process_names = []
    for process_config in processes:
        process_names.append(process_config["name"])

    total_cpus = psutil.cpu_count()

    while True:
        print(f"[{datetime.datetime.now()}]\t⚙️ Total logical processors: {total_cpus}")

        is_on_ac_power = detect_system_battery_state()
        if not is_on_ac_power:
            print(f"[{datetime.datetime.now()}]\t🔋 Detected system on BATTERY")
        else:
            print(f"[{datetime.datetime.now()}]\t🔌 Detected system on AC POWER")

        print(f"[{datetime.datetime.now()}]\t🛠️ Applying ruleset to processes {process_names}...")

        try:
            govern_processes(processes)
        except Exception:
            print(f"[{datetime.datetime.now()}]\t❌ Couldn't apply settings to processes. Will wait for next pass.")
            pass

        if run_forever:
            print(f"[{datetime.datetime.now()}]\t💤 Sleeping now. Will activate again in {polling_interval_seconds}s")
            time.sleep(polling_interval_seconds)
        else:
            break


print(f"🦉 process_guru - last updated: 2023-07-23")
# Start it all!
__main__()
