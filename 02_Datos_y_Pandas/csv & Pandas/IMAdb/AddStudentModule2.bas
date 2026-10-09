' Standard module to expose a macro that shows the UserForm
Option Explicit

Public Sub ShowAddStudentForm()
    On Error Resume Next
    AddStudentForm.Show vbModal
End Sub
