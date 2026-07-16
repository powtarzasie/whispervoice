' WhisperVoice v3.4  |  build 15.07.2026
' Uruchomienie bez okna konsoli

Option Explicit

Dim oShell, oFSO, Q, sDir, sPython, sMainPy, sCmd, sLogDir, sLog

Set oShell = CreateObject("WScript.Shell")
Set oFSO   = CreateObject("Scripting.FileSystemObject")
Q = Chr(34)

' Folder aplikacji (z lokalizacji tego skryptu)
sDir    = oFSO.GetParentFolderName(WScript.ScriptFullName) & "\"
sMainPy = sDir & "main.py"

' Folder logow (zapisywalny nawet gdy app w Program Files)
sLogDir = oShell.ExpandEnvironmentStrings("%APPDATA%") & "\WhisperVoice"
If Not oFSO.FolderExists(sLogDir) Then
    oFSO.CreateFolder sLogDir
End If
sLog = sLogDir & "\error.log"

' Znajdz python.exe
sPython = FindPython()

' Jesli Python nie zostal znaleziony — pokaz komunikat zamiast cichem niepowodzeniu
If sPython = "" Then
    MsgBox "WhisperVoice nie moze sie uruchomic." & vbCrLf & vbCrLf & _
           "Nie znaleziono Pythona 3.10 lub nowszego." & vbCrLf & vbCrLf & _
           "Rozwiazania:" & vbCrLf & _
           "  1. Uruchom fix_python_path.bat z folderu aplikacji" & vbCrLf & _
           "  2. Zainstaluj Python z: https://www.python.org/downloads/" & vbCrLf & _
           "     (zaznacz opcje: Add Python to PATH)", _
           vbExclamation, "WhisperVoice — blad uruchamiania"
    WScript.Quit 1
End If

' Zbuduj polecenie — uruchamiamy przez cmd /c zeby przechwycic stderr Pythona
' Format: cmd /c ""python" "main.py" 2>>"error.log""
' Append mode (>>) — historia bledow nie ginie po restarcie
sCmd = "cmd /c " & Q & Q & sPython & Q & " " & Q & sMainPy & Q & _
       " 2>>" & Q & sLog & Q & Q

' Uruchom bez okna (0 = SW_HIDE), nie czekaj na zakonczenie
oShell.Run sCmd, 0, False

Set oFSO   = Nothing
Set oShell = Nothing


' ================================================================
' Szuka python.exe: PATH -> rejestr HKCU -> rejestr HKLM -> folder
' ================================================================
Function FindPython()
    Dim i, sVer, sExe, sLocalApp, rc

    ' 1. PATH
    On Error Resume Next
    Err.Clear
    rc = oShell.Run("python --version", 0, True)
    If Err.Number = 0 And rc = 0 Then
        FindPython = "python"
        On Error GoTo 0
        Exit Function
    End If
    On Error GoTo 0

    ' 2. Rejestr HKCU (instalacja dla biezacego uzytkownika)
    For i = 16 To 10 Step -1
        sVer = "3." & CStr(i)
        On Error Resume Next
        Err.Clear
        sExe = oShell.RegRead("HKCU\SOFTWARE\Python\PythonCore\" & sVer & "\InstallPath\ExecutablePath")
        On Error GoTo 0
        If Err.Number = 0 And sExe <> "" And oFSO.FileExists(sExe) Then
            FindPython = sExe
            Exit Function
        End If
    Next

    ' 3. Rejestr HKLM (instalacja dla wszystkich uzytkownikow)
    For i = 16 To 10 Step -1
        sVer = "3." & CStr(i)
        On Error Resume Next
        Err.Clear
        sExe = oShell.RegRead("HKLM\SOFTWARE\Python\PythonCore\" & sVer & "\InstallPath\ExecutablePath")
        On Error GoTo 0
        If Err.Number = 0 And sExe <> "" And oFSO.FileExists(sExe) Then
            FindPython = sExe
            Exit Function
        End If
    Next

    ' 4. Typowe foldery instalacji
    sLocalApp = oShell.ExpandEnvironmentStrings("%LOCALAPPDATA%")
    For i = 16 To 10 Step -1
        sExe = sLocalApp & "\Programs\Python\Python3" & CStr(i) & "\python.exe"
        If oFSO.FileExists(sExe) Then
            FindPython = sExe
            Exit Function
        End If
        sExe = "C:\Python3" & CStr(i) & "\python.exe"
        If oFSO.FileExists(sExe) Then
            FindPython = sExe
            Exit Function
        End If
    Next

    ' Python nie znaleziony zadna metoda — zwroc pusty string (blad obsluzony wyzej)
    FindPython = ""
End Function
