Write-Host "Running all Arbor language tests..." -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

Get-ChildItem -Path . -Filter "*.arbor" | ForEach-Object {
    Write-Host "`nRunning test: $($_.Name)" -ForegroundColor Cyan
    Write-Host "--------------------------------" -ForegroundColor Cyan
    python ../main.py $_.FullName
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Test completed successfully" -ForegroundColor Green
    } else {
        Write-Host "Test failed with exit code $LASTEXITCODE" -ForegroundColor Red
    }
}

Write-Host "`nAll tests completed" -ForegroundColor Green 