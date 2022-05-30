

## Issue Description
Adversaries can use DLL search order hijacking to execute, stage and evade protective restrictions in a reliable and unobtrusive manner. DLL search order hijacking or DLL preloading is popular among attackers because it allows them to deliver malicious programs to a host system in a way that is difficult to detect. An attacker can use search order hijacking to load a malicious DLL into a process that is hosted by a legal, high-reputation executable.

When an application dynamically loads a dynamic link library (DLL) without supplying a fully qualified path, Windows searches a predefined set of folders to find the DLL. If an attacker takes control of one of the folders, they can force the program to load a malicious copy of the DLL instead of the expected DLL. DLL preloading exploits are ubiquitous across all operating systems that enable dynamically loading shared DLL libraries. An attacker might execute code in the context of the user who is executing the application as a result of such assaults. When the program is executed as Administrator, a local elevation of privilege may occur.


## How do adversaries use DLL preloading?
In many circumstances, a program will specify the location of the DLL it wants to run, bypassing the search order process entirely. If the DLL is already loaded into a process' memory, the search order process is likewise superfluous. If a program or executable does not provide the location of the DLL it wants to load and the DLL has not been loaded into memory, the application or executable will follow a predefined order of actions to locate the DLL. The DLL search order procedure, which Microsoft outlines in detail in its literature, is what this is called [1](https://docs.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-search-order).

For our purposes, all you need to know is that the process calling the DLL will look for the DLL in question in the directory from which it is being executed before iterating through other places in a preset sequence. To put it another way, if `process.exe` is running from the Program Files directory and needs to contact `module.dll`, it will first check in the Program Files directory.

Adversaries can take advantage of this search order procedure by relocating normal system binaries into non-standard folders that include malicious DLLs labeled after legitimate DLLs. Continuing with the previous example, if `process.exe` and `module.dll` are both in the System32 directory, `process.exe` will search that directory for the genuine `module.dll` and launch it. An opponent, on the other hand, can place a malicious version of `module.dll` in the temp directory and relocate `process.exe` there as well. When `process.exe` runs and looks for `module.dll` in the temp directory, it grabs the malicious version rather than the original version in the system32 directory. Even if the maliciously crafted DLL is not signed, the dynamic linking procedure is carried out. The executable `process.exe` then calls the DLL's export functions; however, if the malicious `module.dll` contains the identical DLL export functions, the malicious payload will be loaded into memory by `process.exe`.


### Consider the following scenario:
1. A program loads a DLL without specifying the fully qualified path it expects to find in the program's CWD.
2. The program is well equipped to handle the situation when the DLL cannot be found.
3. The attacker has access to the application's information and copies the target executable to the CWD.
4. The attacker replaces and DLL in the CWD with their own specially engineered version. This presupposes that the attacker has been granted authorization.
5. Windows looks for the DLL in the application's CWD by searching through the directories in the DLL Search Order.

In this scenario, the specially crafted DLL runs within the application and gains the privileges of the current user.

### Recommended steps for software developers
- Validate their applications for instances of nonsecure library loads (examples of each are given later in this article). These include the following:  
    - The use of SearchPath to identify the location of a library or component.
    - The use of LoadLibrary to identify the version of the operating system.
- Use fully qualified paths for all calls to LoadLibrary, CreateProcess, and ShellExecute where you can.
- Implement calls to SetDllDirectory with an empty string (“”) to remove the current working directory from the default DLL search order where it is required. Be aware that SetDllDirectory affects the whole process. Therefore, you should do this one time early in process initialization, not before and after calls to LoadLibrary. Because SetDllDirectory affects the whole process, multiple threads calling SetDllDirectory with different values could cause undefined behavior. (Additionally, if the process is designed to load third-party DLLs, testing will be needed to determine whether making a process-wide setting will cause incompatibilities. A known issue is that when an application depends on Visual Basic for Applications, a process-wide setting may cause incompatibilities.)
- Use the [SetSearchPathMode](http://msdn.microsoft.com/en-us/library/dd266735(vs.85).aspx)function to enable safe process search mode for the process. This moves the current working directory to the last place in the SearchPath search list for the lifetime of the process.
- Avoid using SearchPath to check for the existence of a DLL without specifying a fully qualified path, even if safe search mode is enabled, because this can still lead to DLL Preloading attacks.

### Guidance on identifying nonsecure library loads
In source code, the following are examples of nonsecure library loads:  
- In the following code example, the application searches for `cryptbase.dll` by using the least secure search path. If an attacker can place `cryptbase.dll` in CWD, it will load even before the application searches the Windows directories for the appropriate library.
  `DWORD retval = SearchPath(NULL, "cryptbase", ".dll", err, result, NULL);    HMODULE handle = LoadLibrary(result);`
- In the following code example, the application tries to load the library from the various application and operating system locations described in the beginning of this document for the LoadLibrary() call. If there is any risk that the file is not present, the application may try to load the file from the current working directory. This scenario is slightly less dangerous than the previous example. However, it still exposes the application user to risk if the environment is not completely predictable.
    `HMODULE handle = LoadLibrary("cryptbase.dll");`
The following are examples of better, more secure library loads:  
- In the following code example, the library is loaded directly by using a fully qualified path. There is no risk of the attacker introducing malicious code unless he already has write permissions to the application’s target directory.  
    `HMODULE handle = LoadLibrary("c:\\windows\\system32\\cryptbase.dll");`    
    Note, for information about how to determine the system directory, see the following resources:  
    - [GetSystemDirectory](http://msdn.microsoft.com/en-us/library/ms724373%28vs.85%29.aspx)
    - [SHGetKnownFolderPath](http://msdn.microsoft.com/en-us/library/bb762188%28v=vs.85%29.aspx)
- In the following code example, the current working directory is removed from the search path before calling LoadLibrary. This reduces the risk significantly, as the attacker would have to control either the application directory, the Windows directory, or any directories that are specified in the user’s path in order to use a DLL preloading attack.
    `SetDllDirectory ("");`
    `HMODULE handle = LoadLibrary("cryptbase.dll");`
- In the following code example, the current working directory is removed from the search path before calling LoadLibrary. This reduces the risk significantly, as the attacker would have to control either the application directory, the windows directory, or any directories that are specified in the user’s path in order to use a DLL preloading attack.
    `SetSearchPathMode (BASE_SEARCH_PATH_ENABLE_SAFE_SEARCHMODE | BASE_SEARCH_PATH_PERMANENT);`
    `HMODULE handle = LoadLibrary("cryptbase.dll");`


