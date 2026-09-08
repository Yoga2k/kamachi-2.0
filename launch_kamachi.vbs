Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
currentDir = fso.GetParentFolderName(WScript.ScriptFullName)
WshShell.CurrentDirectory = currentDir

' Universal Python discovery across any Windows PC
userProfile = WshShell.ExpandEnvironmentStrings("%USERPROFILE%")
localPy310 = userProfile & "\AppData\Local\Programs\Python\Python310\pythonw.exe"
localPy311 = userProfile & "\AppData\Local\Programs\Python\Python311\pythonw.exe"
localPy312 = userProfile & "\AppData\Local\Programs\Python\Python312\pythonw.exe"

If fso.FileExists(localPy310) Then
    pythonwExe = """" & localPy310 & """"
ElseIf fso.FileExists(localPy311) Then
    pythonwExe = """" & localPy311 & """"
ElseIf fso.FileExists(localPy312) Then
    pythonwExe = """" & localPy312 & """"
Else
    pythonwExe = "pythonw.exe"
End If

WshShell.Run pythonwExe & " run_with_avatar.py", 0, False
