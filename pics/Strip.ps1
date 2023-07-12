Write-Output "Stripping"
Get-ChildItem -Path .\* -Include *.png -Exclude *-stripped.png | ForEach-Object {
    pngstuff -i $_.FullName -o $(-join($_.BaseName, "-stripped", $_.Extension)) -a strip
}

Write-Output "Dumping"
Get-ChildItem -Path .\* -Include *-stripped.png | ForEach-Object {
    pngstuff -i $_.FullName -a dump
}

Write-Output "Removing"
Get-ChildItem -Path .\* -Include *.png -Exclude *-stripped.png | ForEach-Object {
    Remove-Item -Path $_.FullName
}
