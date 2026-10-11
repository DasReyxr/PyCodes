VERSION 5.00
Begin VB.UserForm AddStudentForm  frmAddStudent
    Caption         =   "Add Student"
    ClientHeight    =   2700
    ClientLeft      =   120
    ClientTop       =   45
    ClientWidth     =   4800
    Begin VB.Label lblName
        Caption         =   "Alumno"
        Height          =   255
        Left            =   120
        Top             =   120
        Width           =   900
    End
    Begin VB.TextBox txtName
        Height          =   255
        Left            =   1020
        Top             =   120
        Width           =   3360
    End
    Begin VB.Label lblProfesor
        Caption         =   "Profesor"
        Height          =   255
        Left            =   120
        Top             =   420
        Width           =   900
    End
    Begin VB.TextBox txtProfesor
        Height          =   255
        Left            =   1020
        Top             =   420
        Width           =   3360
    End
    Begin VB.Label lblStatus
        Caption         =   "Status"
        Height          =   255
        Left            =   120
        Top             =   720
        Width           =   900
    End
    Begin VB.TextBox txtStatus
        Height          =   255
        Left            =   1020
        Top             =   720
        Width           =   900
    End
    Begin VB.Label lblClase
        Caption         =   "Clase"
        Height          =   255
        Left            =   2040
        Top             =   720
        Width           =   540
    End
    Begin VB.TextBox txtClase
        Height          =   255
        Left            =   2640
        Top             =   720
        Width           =   1740
    End
    Begin VB.Label lblDuracion
        Caption         =   "Duración"
        Height          =   255
        Left            =   120
        Top             =   1020
        Width           =   900
    End
    Begin VB.TextBox txtDuracion
        Height          =   255
        Left            =   1020
        Top             =   1020
        Width           =   900
    End
    Begin VB.Label lblHorario
        Caption         =   "Horario"
        Height          =   255
        Left            =   2040
        Top             =   1020
        Width           =   540
    End
    Begin VB.TextBox txtHorario
        Height          =   255
        Left            =   2640
        Top             =   1020
        Width           =   1740
    End
    Begin VB.Label lblDia
        Caption         =   "Día"
        Height          =   255
        Left            =   120
        Top             =   1320
        Width           =   900
    End
    Begin VB.TextBox txtDia
        Height          =   255
        Left            =   1020
        Top             =   1320
        Width           =   900
    End
    Begin VB.Label lblClases
        Caption         =   "Clases"
        Height          =   255
        Left            =   2040
        Top             =   1320
        Width           =   540
    End
    Begin VB.TextBox txtClases
        Height          =   255
        Left            =   2640
        Top             =   1320
        Width           =   1740
    End
    Begin VB.Label lblPagoProp
        Caption         =   "Pago Prop"
        Height          =   255
        Left            =   120
        Top             =   1620
        Width           =   900
    End
    Begin VB.TextBox txtPagoProp
        Height          =   255
        Left            =   1020
        Top             =   1620
        Width           =   900
    End
    Begin VB.Label lblRecibo
        Caption         =   "Recibo"
        Height          =   255
        Left            =   2040
        Top             =   1620
        Width           =   540
    End
    Begin VB.TextBox txtRecibo
        Height          =   255
        Left            =   2640
        Top             =   1620
        Width           =   1740
    End
    Begin VB.CommandButton cmdAdd
        Caption         =   "Add Student"
        Height          =   360
        Left            =   1020
        Top             =   2040
        Width           =   1500
    End
    Begin VB.CommandButton cmdCancel
        Caption         =   "Cancel"
        Height          =   360
        Left            =   2640
        Top             =   2040
        Width           =   1500
    End
End
Attribute VB_Name = "AddStudentForm"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = False
Option Explicit

Private Sub UserForm_Initialize()
    ' Default values
    On Error Resume Next
    txtStatus.Text = "Activo"
    txtClases.Text = "4"
    On Error GoTo 0
    
    ' Populate days listbox (Lunes - Sabado)
    Dim days As Variant
    days = Array("Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado")
    On Error Resume Next
    ListBox1.Clear
    Dim d As Variant
    For Each d In days
        ListBox1.AddItem d
    Next d
    On Error GoTo 0

    ' Ensure ListBox1 is visible and sized sensibly — locate an anchor control (txtDia) safely
    Dim anchor As Object
    On Error Resume Next
    Set anchor = Me.Controls("txtDia")
    If anchor Is Nothing Then Set anchor = Me.Controls("txtDia1")
    On Error GoTo 0

    If anchor Is Nothing Then
        ' Try to find a Label with caption "Día" / "DIA" and pick the nearest control to its right
        Dim lbl As Object, c As Object, candidate As Object
        Dim bestDist As Long: bestDist = 999999
        For Each lbl In Me.Controls
            If TypeName(lbl) = "Label" Then
                If Trim(UCase$(lbl.Caption)) = "DÍA" Or Trim(UCase$(lbl.Caption)) = "DIA" Then
                    For Each c In Me.Controls
                        If c.Left > lbl.Left And Abs(c.Top - lbl.Top) < 400 Then
                            If (c.Left - lbl.Left) < bestDist Then
                                Set candidate = c
                                bestDist = c.Left - lbl.Left
                            End If
                        End If
                    Next c
                    If Not candidate Is Nothing Then
                        Set anchor = candidate
                        Exit For
                    End If
                End If
            End If
        Next lbl
    End If

    If Not anchor Is Nothing Then
        With ListBox1
            .Left = anchor.Left
            .Top = anchor.Top
            .Width = anchor.Width
            .Height = anchor.Height * 4
            .ListStyle = 0
            .ColumnCount = 1
        End With
    Else
        ' Final fallback: sensible defaults
        With ListBox1
            .Left = 1020
            .Top = 1320
            .Width = 900
            .Height = 255 * 4
            .ListStyle = 0
            .ColumnCount = 1
        End With
    End If
End Sub

Private Function FindHeaderColumn(ws As Worksheet, headerNames As Variant) As Long
    Dim r As Long, c As Long, lastCol As Long, cellVal As String
    lastCol = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column
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
    Dim col As Long
    col = FindHeaderColumn(ws, wantedNames)
    If col > 0 Then
        EnsureHeader = col
        Exit Function
    End If
    Dim lastCol As Long
    lastCol = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column
    col = lastCol + 1
    ws.Cells(1, col).Value = wantedNames(0)
    EnsureHeader = col
End Function

Private Function DetectHeaderRow(ws As Worksheet) As Long
    Dim r As Long, c As Long, lastCol As Long, cellVal As String
    lastCol = ws.Cells(1, ws.Columns.Count).End(xlToLeft).Column
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
    DetectHeaderRow = 1
End Function

Private Sub cmdAdd_Click()
    On Error GoTo ErrHandler
    Dim ws As Worksheet
    Dim sheetName As String
    sheetName = "Tradicional"
    Set ws = ThisWorkbook.Worksheets(sheetName)

    Dim headerRow As Long
    headerRow = DetectHeaderRow(ws)

    Dim lastRow As Long
    lastRow = ws.Cells(ws.Rows.Count, 1).End(xlUp).Row
    If lastRow < headerRow Then lastRow = headerRow
    Dim insertRow As Long
    insertRow = lastRow + 1

    Dim colName As Long
    colName = EnsureHeader(ws, Array("ALUMNO", "Alumno", "Nombre"))
    ws.Cells(insertRow, colName).Value = Trim(txtName.Text)

    colName = EnsureHeader(ws, Array("PROFESOR", "Profesor", "Maestro"))
    ws.Cells(insertRow, colName).Value = Trim(txtProfesor.Text)

    colName = EnsureHeader(ws, Array("Status", "STATUS", "ESTADO"))
    ws.Cells(insertRow, colName).Value = Trim(txtStatus.Text)

    colName = EnsureHeader(ws, Array("CLASE", "Clase", "Tipo"))
    ws.Cells(insertRow, colName).Value = Trim(txtClase.Text)

    colName = EnsureHeader(ws, Array("DURACIÓN", "Duracion", "Duración", "Dur"))
    ws.Cells(insertRow, colName).Value = Trim(txtDuracion.Text)

    colName = EnsureHeader(ws, Array("HORARIO", "Horario", "Hora"))
    ws.Cells(insertRow, colName).Value = Trim(txtHorario.Text)

    colName = EnsureHeader(ws, Array("DÍA", "DIA", "Dia"))
    ws.Cells(insertRow, colName).Value = Trim(txtDia.Text)

    colName = EnsureHeader(ws, Array("Clases", "CLASES"))
    ws.Cells(insertRow, colName).Value = Trim(txtClases.Text)

    colName = EnsureHeader(ws, Array("Pago Prop", "Pago", "Propina"))
    ws.Cells(insertRow, colName).Value = Trim(txtPagoProp.Text)

    colName = EnsureHeader(ws, Array("RECIBO ACTUAL", "Recibo", "RECIBO"))
    ws.Cells(insertRow, colName).Value = Trim(txtRecibo.Text)

    Dim c As Long, lastCol As Long
    lastCol = ws.Cells(headerRow, ws.Columns.Count).End(xlToLeft).Column
    For c = 1 To lastCol
        ws.Cells(insertRow, c).Borders.LineStyle = xlContinuous
    Next c

    MsgBox "Student added at row " & insertRow, vbInformation
    Me.Hide
    Exit Sub

ErrHandler:
    MsgBox "Error adding student: " & Err.Description, vbExclamation
End Sub

Private Sub cmdCancel_Click()
    Me.Hide
End Sub
