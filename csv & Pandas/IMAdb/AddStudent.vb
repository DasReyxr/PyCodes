Option Explicit


Private Sub UserForm_Initialize()
    ' Default values

    
    ' Populate days listbox (Lunes - Sabado)
    Dim days As Variant
    days = Array("Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado")
    On Error Resume Next
    ComboBox1.Clear
    Dim d As Variant
    For Each d In days
        ComboBox1.AddItem d
    Next d
    On Error GoTo 0
   
End Sub

Private Function FindHeaderColumn(ws As Worksheet, headerNames As Variant) As Long
    ' Looks for any of the headerNames (case-insensitive) in the top 20 rows, returns column index or 0 if not found
    Dim r As Long, c As Long, lastCol As Long, cellVal As String
    Dim lastCell As Range
    On Error Resume Next
    Set lastCell = ws.Cells.Find(What:="*", After:=ws.Cells(1, 1), LookIn:=xlFormulas, LookAt:=xlPart, SearchOrder:=xlByColumns, SearchDirection:=xlPrevious)
    On Error GoTo 0
    If Not lastCell Is Nothing Then
        lastCol = lastCell.Column
    Else
        lastCol = 1
    End If
    For r = 1 To 20
        For c = 1 To lastCol
            cellVal = Trim(CStr(ws.Cells(r, c).Value))
            If Len(cellVal) > 0 Then
                Dim nm As Variant
                For Each nm In headerNames
                    If UCase(cellVal) = UCase(CStr(nm)) Then
                        FindHeaderColumn = c
                        Exit Function
                    End If
                Next nm
            End If
        Next c
    Next r
    FindHeaderColumn = 0
End Function

Private Function EnsureHeader(ws As Worksheet, wantedNames As Variant) As Long
    ' Try to find any of wantedNames; if none found, append a new column with the first name and return its column
    Dim col As Long
    col = FindHeaderColumn(ws, wantedNames)
    If col > 0 Then
        EnsureHeader = col
        Exit Function
    End If

    ' none found - append at rightmost column + 1
    Dim lastCol As Long
    Dim lastCell As Range
    On Error Resume Next
    Set lastCell = ws.Cells.Find(What:="*", After:=ws.Cells(1, 1), LookIn:=xlFormulas, LookAt:=xlPart, SearchOrder:=xlByColumns, SearchDirection:=xlPrevious)
    On Error GoTo 0
    If Not lastCell Is Nothing Then
        lastCol = lastCell.Column
    Else
        lastCol = 1
    End If
    col = lastCol + 1
    ws.Cells(1, col).Value = wantedNames(0)
    EnsureHeader = col
End Function

Private Function DetectHeaderRow(ws As Worksheet) As Long
    ' Detects which row contains headers by scanning first 20 rows for a likely header word
    Dim r As Long, c As Long, lastCol As Long, cellVal As String
    Dim lastCell As Range
    On Error Resume Next
    Set lastCell = ws.Cells.Find(What:="*", After:=ws.Cells(1, 1), LookIn:=xlFormulas, LookAt:=xlPart, SearchOrder:=xlByColumns, SearchDirection:=xlPrevious)
    On Error GoTo 0
    If Not lastCell Is Nothing Then
        lastCol = lastCell.Column
    Else
        lastCol = 1
    End If
    For r = 1 To 20
        For c = 1 To lastCol
            cellVal = Trim(CStr(ws.Cells(r, c).Value))
            If Len(cellVal) > 0 Then
                If InStr(1, UCase(cellVal), "ALUMNO") > 0 Or InStr(1, UCase(cellVal), "NOMBRE") > 0 Or InStr(1, UCase(cellVal), "PROF") > 0 Or InStr(1, UCase(cellVal), "STATUS") > 0 Then
                    DetectHeaderRow = r
                    Exit Function
                End If
            End If
        Next c
    Next r
    ' fallback to first row
    DetectHeaderRow = 1
End Function
Private Sub CommandButton1_Click()
    ' On Error GoTo ErrHandler
    Dim ws As Worksheet
    Dim sheetName As String
    sheetName = "Tradicional" ' change if your alumni DB sheet name is different
    Set ws = ThisWorkbook.Worksheets(sheetName)

    Dim headerRow As Long
    headerRow = DetectHeaderRow(ws)

    ' Determine the insert row (first blank row after header)
    Dim lastRow As Long
    lastRow = ws.Cells(ws.Rows.Count, headerRow).End(xlUp).Row
    If lastRow < headerRow Then lastRow = headerRow
    Dim insertRow As Long
    insertRow = lastRow + 1

    ' Map fields to header names (try several alternatives)
    Dim colName As Long
    colName = EnsureHeader(ws, Array("Status", "STATUS", "ESTADO"))
    ws.Cells(insertRow, colName).Value = "Activo"
    ws.Cells(insertRow, colName).Interior.Color = RGB(112, 173, 71)
    
    
    colName = EnsureHeader(ws, Array("ALUMNO", "Alumno", "Nombre"))
    ws.Cells(insertRow, colName).Value = Trim(txtName.Text)
    ws.Cells(insertRow, colName).Interior.Color = RGB(180, 198, 231)

    colName = EnsureHeader(ws, Array("PROFESOR", "Profesor", "Maestro"))
    ws.Cells(insertRow, colName).Value = Trim(txtProfesor.Text)
    
    Select Case txtProfesor.Text
    Case "Beto", "beto", "Oscar", "oscar"
        ws.Cells(insertRow, colName).Interior.Color = RGB(255, 192, 0)
    Case "Pavel", "pavel"
        ws.Cells(insertRow, colName).Interior.Color = RGB(51, 204, 255)
    Case "Fernando", "Fer", "fernando", "fer"
        ws.Cells(insertRow, colName).Interior.Color = RGB(0, 102, 255)
        ws.Cells(insertRow, colName).Font.Color = RGB(242, 242, 242)
    Case "Valentín", "valentin", "Valentin"
        ws.Cells(insertRow, colName).Interior.Color = RGB(244, 176, 132)
    Case "Alex", "alex"
        ws.Cells(insertRow, colName).Interior.Color = RGB(160, 242, 244)
    Case "Estephanie", "estephanie", "Fany", "fany"
        ws.Cells(insertRow, colName).Interior.Color = RGB(255, 204, 255)
        
    Case Else
    ws.Cells(insertRow, colName).Interior.Color = RGB(112, 173, 71)
    End Select
    colName = EnsureHeader(ws, Array("CURSO", "curso"))
    ws.Cells(insertRow, colName).Value = Trim(txtCurso.Text)
    ws.Cells(insertRow, colName).Interior.Color = RGB(198, 224, 180)

    colName = EnsureHeader(ws, Array("FECHA DE NACIMIENTO DEL ALUMNO"))
    ws.Cells(insertRow, colName).Value = Trim(txtAge.Text)
    ws.Cells(insertRow, colName).Interior.Color = RGB(252, 228, 214)


    colName = EnsureHeader(ws, Array("DIA", "DÍA"))
    ws.Cells(insertRow, colName).Value = Trim(ComboBox1.Text)
    ws.Cells(insertRow, colName).Interior.Color = RGB(180, 198, 231)

    colName = EnsureHeader(ws, Array("HORARIO", "HORARIO"))
    ws.Cells(insertRow, colName).Value = Trim(txtHorario.Text)
    ws.Cells(insertRow, colName).Interior.Color = RGB(180, 198, 231)

    colName = EnsureHeader(ws, Array("DURACIÓN", "DURACION"))
    ws.Cells(insertRow, colName).Value = Trim(txtDuracion.Text)
    ws.Cells(insertRow, colName).Interior.Color = RGB(180, 198, 231)

    colName = EnsureHeader(ws, Array("NUMERO CONTACTO", "CONTACTO"))
    ws.Cells(insertRow, colName).Value = Trim(txtNumber.Text)
    ws.Cells(insertRow, colName).Interior.Color = RGB(252, 228, 214)

    
    colName = EnsureHeader(ws, Array("CLASE", "Clase", "Tipo"))
    ws.Cells(insertRow, colName).Value = Trim(txtClase.Text)
    ws.Cells(insertRow, colName).Interior.Color = RGB(180, 198, 231)


    ' Optionally format the inserted row (thin borders)
    Dim c As Long, lastCol As Long
    Dim lastCell As Range
    On Error Resume Next
    Set lastCell = ws.Cells.Find(What:="*", After:=ws.Cells(1, 1), LookIn:=xlFormulas, LookAt:=xlPart, SearchOrder:=xlByColumns, SearchDirection:=xlPrevious)
    On Error GoTo 0
    If Not lastCell Is Nothing Then
        lastCol = lastCell.Column
    Else
        lastCol = 1
    End If
    For c = 1 To lastCol
        ws.Cells(insertRow, c).Borders.LineStyle = xlContinuous
    Next c

    MsgBox "Student added at row " & insertRow, vbInformation
    Me.Hide
    Exit Sub
End Sub