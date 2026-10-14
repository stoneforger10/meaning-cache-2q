param([int]$Start=0,[string]$PreviousHash='',[string]$Account='studio-proof-deployer')
$ErrorActionPreference='Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$d=Get-Content deployment.json -Raw | ConvertFrom-Json
$env:CACHE_TEST_ACCOUNT=$Account
$names=@('first','second','reuse','third','bad-source','first')
$files=@('a','b','a-paraphrase','c','c','a')
function Check-Receipt([string]$Hash,[switch]$ExpectedError){
    if($ExpectedError){& node scripts/check.mjs --error $Hash 'replay'}
    else{& node scripts/check.mjs --success $Hash}
    if($LASTEXITCODE -ne 0){throw "Receipt failed for $Hash. No blind rebroadcast."}
}
function Inspect-State{
    $output=& node scripts/inspect.mjs $d.contract
    if($LASTEXITCODE -ne 0){throw 'State/root verification failed. No more writes.'}
    return ($output | ConvertFrom-Json)
}
if($Start -lt 0 -or $Start -gt 5){throw 'Start must be 0..5'}
if($Start -gt 0 -and $PreviousHash -notmatch '^0x[0-9a-fA-F]{64}$'){throw 'PreviousHash required for resuming'}
if($PreviousHash){Check-Receipt $PreviousHash}else{Check-Receipt $d.verified_receipts.deployment}
& node scripts/check.mjs --source $d.contract
if($LASTEXITCODE -ne 0){throw 'Source verification failed'}
for($i=$Start;$i -lt 6;$i++){
    $before=Inspect-State
    $expectedSequence=[Math]::Min($i,5)
    if($before.sequence -ne $expectedSequence){throw 'Unexpected sequence. Inspect history before resuming.'}
    $file='examples/'+$files[$i]+'.txt'
    $sha=(Get-FileHash $file -Algorithm SHA256).Hash.ToLowerInvariant()
    # CLI auto-parses digit-only arguments; keep the deliberately wrong hash a string.
    if($i -eq 4){$sha='f'*64}
    $deadline=[DateTimeOffset]::UtcNow.ToUnixTimeSeconds()+518400
    $output=& node scripts/run-cli.cjs write $d.contract access --args $names[$i] stoneforger10 meaning-cache-2q $d.commit $file $sha $deadline
    $output
    $hashes=@($output | ForEach-Object{if($_ -match '^BROADCAST_HASH (0x[0-9a-fA-F]{64})$'){$Matches[1]}} | Select-Object -Unique)
    if($hashes.Count -ne 1){throw 'No unique broadcast hash. Outcome may be unknown; inspect wallet history.'}
    $hash=$hashes[0]
    Check-Receipt $hash -ExpectedError:($i -eq 5)
    $after=Inspect-State
    if($i -eq 5){
        if($after.sequence -ne 5 -or $after.head -ne $before.head){throw 'Replay changed cache history'}
        @{step=$i;hash=$hash;expected_error=$true;sequence=$after.sequence;head=$after.head;roots_verified=$after.roots_verified} | ConvertTo-Json -Compress
        break
    }
    $last=$after.events[-1]
    if($after.sequence -ne ($i+1)){throw 'Access did not append exactly one event'}
    if($i -eq 2 -and ($last.outcome -ne 'HIT' -or $last.representative -ne $after.events[0].representative)){throw 'Paraphrase did not reuse A'}
    if($i -eq 3 -and ($last.outcome -ne 'MISS' -or $last.evicted -ne $after.events[1].representative)){throw 'Protected policy did not evict B'}
    if($i -eq 4 -and ($last.outcome -ne 'BYPASS' -or ($after.probation -join ',') -ne ($before.probation -join ',') -or ($after.protected -join ',') -ne ($before.protected -join ','))){throw 'Bad evidence changed residency'}
    @{step=$i;hash=$hash;nonce=$names[$i];event=$last;probation=$after.probation;protected=$after.protected;head=$after.head;roots_verified=$after.roots_verified} | ConvertTo-Json -Depth 8 -Compress
}
