$domains=get-content .\allowed.domains.txt
foreach ($domain in $domains){
    $list=$list+ ", " + $domain 
}
$list
$list|out-file -FilePath .\alllowedlist.csv