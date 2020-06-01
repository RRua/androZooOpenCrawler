# !/bin/bash

function downloadGithubReleases(){
	jsonfile=$1
	simple_name=$(echo $jsonfile | cut -f2 -d'/' | sed 's/.json//g')
	versions=$(python releases_finder.py "$jsonfile" )
	for version in $versions; do
		version_id=$(echo $version |  rev | cut -d'/' -f 1 | rev)
		extracted_zip_dir="appsSauce/$simple_name/"
		mkdir -p "$extracted_zip_dir"
		wget -O "$extracted_zip_dir/$version_id" "$version"
	done
}



index=0
for i in $(cut -f1 -f2 -f6 -d,  androzooopen.csv ); do
	data_sauce=$(echo $i | cut -f1 -d,)
	repo_id=$(echo $i | cut -f2 -d,)
	n_releases=$(echo $i | cut -f3 -d,)
	if [[ "$n_releases" -ge "3" ]]; then
		echo "$repo_id"
		#  curl --silent "https://api.github.com/repos/01sadra/Detoxiom/releases"
		if [[ "$data_sauce" == "github" ]]; then
			out_file="appsInfo/$(echo $repo_id| sed 's#/#-#g').json"
			curl --silent "https://api.github.com/repos/${repo_id}/releases" > "$out_file"
			downloadGithubReleases $out_file
		else
			echo "$repo_id" >> "unsupported_$data_sauce.log"
		fi
		exit 0
		
	else
		echo "$repo_id" >> "few_releases.log"
	fi
	index=$(($index + 1))
done




