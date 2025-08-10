function View-Proj-Struct {
    param(
        [string] $Path   = ".",
        [string] $Indent = ""
    )

    # Directories to exclude in the proj struct tree
    [string[]] $excludeDirs = @('.venv', '.idea', '__pycache__', 'Lib')
    $children = Get-ChildItem -LiteralPath $Path | Where-Object {
        if ($_.PSIsContainer -and ($excludeDirs -contains $_.Name)) {
            $false
        } else {
            $true
        }
    }

    for ($i = 0; $i -lt $children.Count; $i++) {
        $child  = $children[$i]
        $isLast = ($i -eq $children.Count - 1)

        # Branch glyphs
        if ($isLast) {
            $branch          = '└─'
            $childIndentUnit = '   '
        } else {
            $branch          = '├─'
            $childIndentUnit = '│  '
        }

        # Print file or folder name
        Write-Host "$Indent$branch $($child.Name)"

        # Recurse into every other folder
        if ($child.PSIsContainer) {
            View-Proj-Struct -Path $child.FullName -Indent ($Indent + $childIndentUnit)
        }
    }
}

View-Proj-Struct
