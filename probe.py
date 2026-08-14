# -*- coding: utf-8 -*-
"""Job 1 — measure the Beast against what Kimi K3 actually needs.

We are NOT guessing any of these. The whole feasibility call turns on four numbers:
  VRAM total, system RAM, free disk on D:, and the *unbuffered* sequential read rate of D:.
The last one is the one that decides tokens/sec, because a 2.8T MoE cannot be resident —
it has to be streamed off the disk every token.

⚠ winsat, not a hand-rolled read loop: a file you just wrote is in the OS cache, so a naive
read-back reports RAM speed and flatters the disk by ~10x. winsat does unbuffered IO.
"""
import rig

PS = r"""
'=== GPU ==='
try { & nvidia-smi --query-gpu=index,name,memory.total,driver_version --format=csv,noheader } catch { 'NO_NVIDIA_SMI' }
'=== CPU / RAM ==='
$os = Get-CimInstance Win32_OperatingSystem
'RAM_TOTAL_GB ' + [math]::Round($os.TotalVisibleMemorySize/1MB,1)
'RAM_FREE_GB ' + [math]::Round($os.FreePhysicalMemory/1MB,1)
'VIRT_TOTAL_GB ' + [math]::Round($os.TotalVirtualMemorySize/1MB,1)
Get-CimInstance Win32_Processor | ForEach-Object { 'CPU ' + $_.Name.Trim() + ' | cores=' + $_.NumberOfCores + ' threads=' + $_.NumberOfLogicalProcessors }
Get-CimInstance Win32_PhysicalMemory | ForEach-Object { 'DIMM ' + [math]::Round($_.Capacity/1GB) + 'GB @' + $_.Speed + 'MHz ' + $_.Manufacturer }
'=== LOGICAL DISKS ==='
Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | ForEach-Object { 'DRIVE ' + $_.DeviceID + ' free_GB=' + [math]::Round($_.FreeSpace/1GB,1) + ' size_GB=' + [math]::Round($_.Size/1GB,1) }
'=== PHYSICAL DISKS ==='
try { Get-PhysicalDisk | ForEach-Object { 'PHYS ' + $_.FriendlyName + ' | media=' + $_.MediaType + ' bus=' + $_.BusType + ' size_GB=' + [math]::Round($_.Size/1GB,1) } } catch { 'NO_PHYSICALDISK' }
'=== EXISTING LLM RUNTIMES ==='
foreach ($c in @('ollama','llama-server','llama-cli','lms')) {
  $g = Get-Command $c -EA SilentlyContinue
  if ($g) { 'FOUND ' + $c + ' -> ' + $g.Source } else { 'ABSENT ' + $c }
}
foreach ($p in @('D:\llama.cpp','D:\llama','C:\Users\'+$env:USERNAME+'\.ollama','D:\aifilm','D:\models','D:\aifilm\comfy')) {
  if (Test-Path $p) { 'PATH_OK ' + $p } else { 'PATH_NO ' + $p }
}
'=== D: TOP LEVEL ==='
try { Get-ChildItem D:\ -Directory -EA SilentlyContinue | Select-Object -First 25 | ForEach-Object { '  D:\' + $_.Name } } catch { 'D_LIST_FAIL' }
'=== NET DOWNLINK (Cloudflare, 200MB) ==='
$sw=[Diagnostics.Stopwatch]::StartNew()
try {
  $req=[Net.HttpWebRequest]::Create('https://speed.cloudflare.com/__down?bytes=200000000')
  $req.Timeout=180000; $req.ReadWriteTimeout=180000
  $rs=$req.GetResponse().GetResponseStream()
  $buf=New-Object byte[] 1048576; $tot=0
  while (($n=$rs.Read($buf,0,$buf.Length)) -gt 0) { $tot+=$n }
  $sw.Stop()
  'NET_BYTES ' + $tot
  'NET_SECONDS ' + [math]::Round($sw.Elapsed.TotalSeconds,2)
  'NET_MBPS ' + [math]::Round(($tot*8/1MB)/$sw.Elapsed.TotalSeconds,1)
  'NET_MBYTES_PER_S ' + [math]::Round(($tot/1MB)/$sw.Elapsed.TotalSeconds,1)
} catch { 'NET_FAIL ' + $_.Exception.Message }
'=== DISK D: unbuffered sequential (winsat) ==='
try {
  $w = & winsat disk -drive d -ran -read 2>&1 | Out-String
  ($w -split "`n") | Where-Object { $_ -match 'Disk|Random|Sequential|Throughput' } | ForEach-Object { '  ' + $_.Trim() }
} catch { 'WINSAT_FAIL ' + $_.Exception.Message }
try {
  $w2 = & winsat disk -drive d -seq -read 2>&1 | Out-String
  ($w2 -split "`n") | Where-Object { $_ -match 'Throughput' } | ForEach-Object { '  SEQ ' + $_.Trim() }
} catch { 'WINSAT_SEQ_FAIL' }
'=== DONE ==='
"""

if __name__ == '__main__':
    rig.run('k3-probe-hardware', PS, timeout_s=1500, poll=15)
