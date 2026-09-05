# VHDX Compactor

A drag-and-drop batch script that compacts (shrinks) `.vhdx` / `.vhd` virtual disk files using Windows `diskpart`.

Dynamically expanding virtual disks grow as data is written but never shrink on their own when files are deleted inside the guest. This script reclaims that unused space on the host, which is especially useful for WSL2 distributions (`ext4.vhdx`) and Hyper-V virtual machines.

## Features
- Drag and drop a `.vhdx` or `.vhd` file onto the script to compact it.
- Automatically requests administrative privileges (required by `diskpart`).
- Attaches the disk read-only so the contents cannot be modified during compaction.
- Reports the `diskpart` exit code instead of failing silently.
- No dependencies beyond what ships with Windows.

## Usage
Drag a virtual disk file onto `compact_vhdx.bat`.

It can also be run from a command prompt:
```bat
compact_vhdx.bat "C:\path\to\disk.vhdx"
```

The script pauses before starting so the disk can be released. **The virtual machine or WSL instance using the file must be completely shut down**, otherwise `diskpart` cannot attach it.

For WSL2, shut everything down first from a normal command prompt:
```bat
wsl --shutdown
```

WSL2 disks are typically found under:
```
%LOCALAPPDATA%\Packages\<DistroPackageName>\LocalState\ext4.vhdx
```

## How It Works
The script writes a temporary `diskpart` script and runs it:
```
select vdisk file="<path>"
attach vdisk readonly
compact vdisk
detach vdisk
```
The temporary file is deleted afterwards.

## Notes
- Only dynamically expanding disks can be compacted; fixed-size disks will not shrink.
- Freeing space inside the guest first (e.g. `fstrim -a` on Linux) gives much better results.
- Compaction time scales with disk size and may take several minutes.
