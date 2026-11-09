param()

$dumpFile = "ea_data_dump.json"
if (-not (Test-Path $dumpFile)) {
    Write-Error "No se encontró $dumpFile"
    exit 1
}

$jsonContent = Get-Content -Raw -Encoding UTF8 $dumpFile | ConvertFrom-Json

function Populate-Eapx($eapxPath) {
    Write-Output "=== Poblando: $eapxPath ==="
    Copy-Item "D:\Programas\EABase.eapx" $eapxPath -Force
    $connStr = "Provider=Microsoft.ACE.OLEDB.12.0;Data Source=$eapxPath;Persist Security Info=False;"
    $conn = New-Object System.Data.OleDb.OleDbConnection($connStr)
    $conn.Open()

    $cmd = $conn.CreateCommand()
    $cmd.CommandText = "DELETE FROM t_package WHERE Package_ID > 1"
    $cmd.ExecuteNonQuery() | Out-Null
    $cmd.CommandText = "DELETE FROM t_object"
    $cmd.ExecuteNonQuery() | Out-Null
    $cmd.CommandText = "DELETE FROM t_diagram"
    $cmd.ExecuteNonQuery() | Out-Null
    $cmd.CommandText = "DELETE FROM t_diagramobjects"
    $cmd.ExecuteNonQuery() | Out-Null
    $cmd.CommandText = "DELETE FROM t_connector"
    $cmd.ExecuteNonQuery() | Out-Null
    $cmd.CommandText = "DELETE FROM t_diagramlinks"
    $cmd.ExecuteNonQuery() | Out-Null
    $cmd.CommandText = "DELETE FROM t_operation"
    $cmd.ExecuteNonQuery() | Out-Null
    $cmd.CommandText = "DELETE FROM t_attribute"
    $cmd.ExecuteNonQuery() | Out-Null

    $tables = @('t_package', 't_object', 't_operation', 't_attribute', 't_diagram', 't_diagramobjects', 't_connector', 't_diagramlinks')
    foreach ($tbl in $tables) {
        $tableData = $jsonContent.$tbl
        $cols = $tableData.columns
        $rows = $tableData.rows

        $colList = ($cols | ForEach-Object { "[$_]" }) -join ", "
        $paramList = ($cols | ForEach-Object { "?" }) -join ", "
        $insertSql = "INSERT INTO [$tbl] ($colList) VALUES ($paramList)"

        $tx = $conn.BeginTransaction()
        $insertCmd = $conn.CreateCommand()
        $insertCmd.Transaction = $tx
        $insertCmd.CommandText = $insertSql

        $count = 0
        foreach ($row in $rows) {
            if ($tbl -eq 't_package' -and $row[0] -eq 1) { continue }
            $insertCmd.Parameters.Clear()
            for ($i = 0; $i -lt $cols.Count; $i++) {
                $val = $row[$i]
                if ($null -eq $val) {
                    $p = $insertCmd.Parameters.Add("p$i", [System.Data.OleDb.OleDbType]::VarWChar)
                    $p.Value = [DBNull]::Value
                }
                else {
                    $p = $insertCmd.Parameters.Add("p$i", [System.Data.OleDb.OleDbType]::VarWChar)
                    $p.Value = [string]$val
                }
            }
            try {
                $insertCmd.ExecuteNonQuery() | Out-Null
                $count++
            }
            catch {
                Write-Warning "Fila fallida en ${tbl}: $_"
            }
        }
        $tx.Commit()
        Write-Output "  -> $tbl : $count insertadas."
    }

    $conn.Close()
    Write-Output "Finalizado con éxito: $eapxPath"
}

# 1. Poblar EAPX en raíz
Populate-Eapx "D:\HDD\DOCS\docs\Universidad\ING SOFTWARE 2\2DO EXAMEN PARCIAL\2doParcialSW2\AegisCore_Perfil_C.eapx"
Populate-Eapx "D:\HDD\DOCS\docs\Universidad\ING SOFTWARE 2\2DO EXAMEN PARCIAL\2doParcialSW2\AegisCore_Perfil_B.eapx"

# 2. Copiar a .eap y docs-iconix-uml
Copy-Item "AegisCore_Perfil_C.eapx" "AegisCore_Perfil_C.eap" -Force
Copy-Item "AegisCore_Perfil_B.eapx" "AegisCore_Perfil_B.eap" -Force

if (Test-Path "docs-iconix-uml") {
    Copy-Item "AegisCore_Perfil_C.eapx" "docs-iconix-uml\AegisCore_Perfil_C.eapx" -Force
    Copy-Item "AegisCore_Perfil_B.eapx" "docs-iconix-uml\AegisCore_Perfil_B.eapx" -Force
    Copy-Item "AegisCore_Perfil_C.eap" "docs-iconix-uml\AegisCore_Perfil_C.eap" -Force
    Copy-Item "AegisCore_Perfil_B.eap" "docs-iconix-uml\AegisCore_Perfil_B.eap" -Force
}

Write-Output "=== Sincronización completa a EAPX y EAP exitosa ==="
