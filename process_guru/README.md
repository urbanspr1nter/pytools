# process_guru

![ss.png](assets%2Fss.png)

**process_guru** is a tool to take control of CPU affinity, priority, and IO priority for known processes defined by
you! All the logic is within 2 files, the main python script and a `config.json` configuration file.

An example use case of this tool is if you want to limit the number of logical CPUs (or threads) a process such as Slack,
the messaging application can run on, you can do so by adding a profile in the `config.json`:

```json
{
  ...
  "processes": [
    {
      "name": "slack.exe",
      "comment": "Limits Slack to use 4 logical CPU cores",
      "cpu_affinity": [0, 1, 2, 3],
      "cpu_priority": "default",
      "io_priority": "default"
    }
  ]
}
```
The above profile will limit `slack.exe` to only use 4 logical CPU cores with "default" priority.

### Requirements
* Python 3.10
* Windows 10 or 11.

### How to Run

1. Use **elevated** permission (Aka: "Run as Administrator") instance of PowerShell/Command/Windows Terminal
2. Invoke the script:
```python
python main.py
```
3. Watch it run...


### Config Structure
The config is a JSON file. Here are some basic attributes needed:

* `forever` - **required** - `{true, false}` - If `true`, then watch processes for the lifetime of `process_guru`.
* `polling_interval_seconds` - **required** - `int` - Seconds to allow `process_guru` to "sleep" after it has applied settings to processes.
* `comment` - What this config is for.
* `processes` - **required** - A list of processes to allow **process_guru** to apply settings onto. Each entry is an JSON object which contains:
  * `name` - **required** - This is the name of the process that would appear in Process Explorer or Task Manager. (Basically the EXE file)
  * `comment` - What this setting does
  * `cpu_affinity` - A list of logical CPUs to force the process to be restricted to running on. **NOTE** logical CPUs begin with core `0` and up to the total number of logical CPUs - 1. Varies from system to system.
    * An `[]` empty array indicates the process will fixed to ALL logical CPUs.
  * `cpu_priority` - Defined priority for process to run in context to the OS scheduler.
    * Valid values: `"default" | "realtime" | "high" | "above normal" | "normal" | "background" | "idle"`
    * Note about `realtime` - Be careful about this setting... It can cause your system to lock up...
  * `io_priority` - Defined priority for process to gain run IO operations in context to the OS scheduler
    * Valid values: `"default" | "high" | "normal" | "low" | "very low"`

Sample:
```json 
{
  "forever": true,
  "polling_interval_seconds": 30,
  "comment": "Sample profile. Assumes computer has 16 logical CPUs (8c/16t)",
  "processes": [
    {
      "name": "node.exe",
      "comment": "(4 cores) Put this only on 4 physical cores so my computer does not lock up",
      "cpu_affinity": [0, 1, 2, 3, 4, 5, 6, 7],
      "cpu_priority": "above normal",
      "io_priority": "default"
    },
    {
      "name": "msedge.exe",
      "comment": "Use all logical cores for Edge but with background priority",
      "cpu_affinity": [],
      "cpu_priority": "background",
      "io_priority": "default"
    }
  ]
}
```

### CPU Affinity

`cpu_affinity` is an array of integers where each integer corresponds to a specific CPU core ID. For example, if your
CPU has 16 logical cores, usually a 8 core, 16 thread system, then each logical core is identified as: 0, 1, 2, ..., 15.

So the maximum ID here in this scenario is `[# logical cores]  - 1`. Some combinations could be:

**Lock down a process to _first_ 8 _logical_ cores**: `[0, 1, 2, 3, 4, 5, 6, 7]`

**Lock down a process to _last_ 4 _logical_ cores**: `[12, 13, 14, 15]`

**Lock down a process to 2 specific _logical_ cores**: `[6, 7]`

### CPU Affinity in Hybrid CPU Scenarios
If you're running 12th, or 13th generation Intel Core CPUs, then the _EFFICIENCY_ cores will be the last set of cores.
For example, in a 4P/8E core scenario, then P-cores correspond to logical cores 0-7, while, E-cores corresponds to logical cores
8-15. Just follow this assumption, and things should behave fine.

### CPU Priority

Valid values are: `"default" | "realtime" | "high" | "above normal" | "normal" | "background" | "idle"`

`default` is the **same** as NORMAL priority. Be careful about using `realtime` as it may over-prioritize execution of the process
and cause system instability.

### Using `pyinstaller` to create an EXE

```powershell
pyinstaller --clean --onefile -i gear.ico --name="process_guru" main.py
```