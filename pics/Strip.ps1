echo "Stripping"
Get-ChildItem -Path .\* -Include *.png -Exclude *-stripped.png | ForEach-Object {
    pngstuff -i $_.FullName -o $(-join($_.BaseName, "-stripped", $_.Extension)) -a strip
}

echo "Dumping"
Get-ChildItem -Path .\* -Include *-stripped.png | ForEach-Object {
    pngstuff -i $_.FullName -a dump
}

echo "Removing"
Get-ChildItem -Path .\* -Include *.png -Exclude *-stripped.png | ForEach-Object {
    Remove-Item -Path $_.FullName
}
