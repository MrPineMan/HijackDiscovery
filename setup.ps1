Write-Output "Setting Cygwin environment variable"

[Environment]::SetEnvironmentVariable(
    "Path",
    [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine) + ";C:\cygwin64\bin",
    [EnvironmentVariableTarget]::Machine)


Set-ItemProperty -Path HKLM:SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System -Name EnableLUA -Value 0 -Type DWord
Write-Host "Disabling the UAC......Settings will be effective after restart"


wget "https://www.cygwin.com/setup-x86_64.exe" -outfile "setup-x86_64.exe"
.\setup-x86_64.exe -q -s http://cygwin.mirror.constant.com -P "x86_64-w64-mingw32-gcc.exe"


python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt