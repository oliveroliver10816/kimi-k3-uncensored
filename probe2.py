# -*- coding: utf-8 -*-
"""Job 2 — the two numbers that decide whether Ryanchen911's K3 is usable on the Beast.

A 539.7 GiB model on a 189.6 GB machine can only run one way: llama.cpp mmaps the GGUF and
streams experts off D: on demand. So the speed is set by exactly two things:

  1. HOW MUCH OF IT WE CAN CACHE  -> total RAM the BOARD can take (not what's fitted).
     If the board is consumer AM5 it caps ~192-256 GB and the model can never be resident.
     If it's Threadripper PRO / Xeon W (8ch RDIMM) it goes to 512GB-1TB and this becomes easy.
  2. HOW FAST THE REST STREAMS    -> unbuffered random+sequential read on D:.

⚠ winsat, not a read-back loop: a file you just wrote sits in the OS cache and a naive
re-read reports RAM speed, flattering the disk ~10x. winsat does unbuffered IO.
⚠ Read-only. Nothing installed, nothing downloaded.
"""
import rig

PS = r"""
'=== BOARD / CPU ==='
$b = Get-CimInstance Win32_BaseBoard
'BOARD ' + $b.Manufacturer + ' | ' + $b.Product
Get-CimInstance Win32_Processor | ForEach-Object {
  'CPU ' + $_.Name.Trim() + ' | cores=' + $_.NumberOfCores + ' threads=' + $_.NumberOfLogicalProcessors + ' socket=' + $_.SocketDesignation }
$cs = Get-CimInstance Win32_ComputerSystem
'MODEL ' + $cs.Manufacturer + ' ' + $cs.Model
'=== MEMORY: fitted vs capacity ==='
$os = Get-CimInstance Win32_OperatingSystem
'RAM_FITTED_GB ' + [math]::Round($os.TotalVisibleMemorySize/1MB,1)
'RAM_FREE_GB ' + [math]::Round($os.FreePhysicalMemory/1MB,1)
$arr = Get-CimInstance Win32_PhysicalMemoryArray
foreach ($a in $arr) { 'ARRAY_MAX_CAPACITY_GB ' + [math]::Round($a.MaxCapacityEx/1MB,0) + ' | slots=' + $a.MemoryDevices }
$dimms = @(Get-CimInstance Win32_PhysicalMemory)
'DIMMS_POPULATED ' + $dimms.Count
foreach ($d in $dimms) {
  'DIMM ' + $d.DeviceLocator + ' | ' + [math]::Round($d.Capacity/1GB) + 'GB | ' + $d.Speed + 'MT/s | ' + $d.Manufacturer + ' | ' + $d.PartNumber }
'=== GPUs ==='
try { & nvidia-smi --query-gpu=index,name,memory.total,driver_version --format=csv,noheader } catch { 'NO_NVIDIA_SMI' }
'=== DISKS ==='
Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | ForEach-Object { 'DRIVE ' + $_.DeviceID + ' free_GB=' + [math]::Round($_.FreeSpace/1GB,1) + ' size_GB=' + [math]::Round($_.Size/1GB,1) }
try { Get-PhysicalDisk | ForEach-Object { 'PHYS ' + $_.FriendlyName + ' | media=' + $_.MediaType + ' bus=' + $_.BusType + ' size_GB=' + [math]::Round($_.Size/1GB,1) } } catch {}
'=== D: UNBUFFERED READ (winsat) ==='
try {
  $o = & winsat disk -drive d -seq -read 2>&1 | Out-String
  ($o -split "`n") | Where-Object { $_ -match 'Throughput|Disk' } | ForEach-Object { '  SEQ ' + $_.Trim() }
} catch { 'WINSAT_SEQ_FAIL ' + $_.Exception.Message }
try {
  $o2 = & winsat disk -drive d -ran -read 2>&1 | Out-String
  ($o2 -split "`n") | Where-Object { $_ -match 'Throughput|Disk' } | ForEach-Object { '  RAND ' + $_.Trim() }
} catch { 'WINSAT_RAN_FAIL' }
'=== DONE ==='
"""

if __name__ == '__main__':
    rig.run('k3-probe-board-and-disk', PS, timeout_s=1200, poll=15)
