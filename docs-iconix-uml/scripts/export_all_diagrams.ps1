$targetDir = "D:\HDD\DOCS\docs\Universidad\ING SOFTWARE 2\2DO EXAMEN PARCIAL\2doParcialSW2\docs\diagramas-exportados"
if (-not (Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
}

$ea = New-Object -ComObject "EA.App"
$rep = $ea.Repository
$project = $rep.GetProjectInterface()

$filesToExport = @(
    "D:\HDD\DOCS\docs\Universidad\ING SOFTWARE 2\2DO EXAMEN PARCIAL\2doParcialSW2\AegisCore_Perfil_C.eap",
    "D:\HDD\DOCS\docs\Universidad\ING SOFTWARE 2\2DO EXAMEN PARCIAL\2doParcialSW2\AegisCore_Perfil_B.eap"
)

function Export-Package($pkg, $prefix) {
    foreach ($d in $pkg.Diagrams) {
        $cleanName = ($d.Name -replace '[\\/:*?"<>|]', '_').Trim()
        $outFile = Join-Path $targetDir ("${prefix}_${cleanName}.png")
        Write-Host "Exporting: $($d.Name) -> $outFile"
        try {
            $res = $project.PutDiagramImageToFile($d.DiagramGUID, $outFile, 1)
            Write-Host "  Result: $res"
        } catch {
            Write-Host "  Error: $($_.Exception.Message)"
        }
    }
    foreach ($child in $pkg.Packages) {
        Export-Package $child $prefix
    }
}

foreach ($f in $filesToExport) {
    if (Test-Path $f) {
        $base = [System.IO.Path]::GetFileNameWithoutExtension($f)
        Write-Host "=== Opening: $f ==="
        $opened = $rep.OpenFile($f)
        if ($opened) {
            foreach ($m in $rep.Models) {
                Export-Package $m $base
            }
            $rep.CloseFile()
        }
    }
}

$rep.Exit()
Write-Host "ALL DIAGRAMS EXPORTED TO $targetDir"
