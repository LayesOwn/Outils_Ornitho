' Lanceur silencieux ORNI-LAB — ouvre l'app sans fenêtre noire
Dim batPath, shell
batPath = Replace(WScript.ScriptFullName, "ORNI-LAB_silencieux.vbs", "ORNI-LAB.bat")
Set shell = CreateObject("WScript.Shell")
shell.Run "cmd /c """ & batPath & """", 0, False
