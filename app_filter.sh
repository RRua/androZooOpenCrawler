# !/bin/bash

user_name="RRua"
min_releases=3
OAUTH_TOKEN=$(head -1 oauth_token.txt )

function downloadGithubReleases(){
	jsonfile=$1
	simple_name=$(echo $jsonfile | cut -f2 -d'/' | sed 's/.json//g')
	versions=$(python releases_finder.py "$jsonfile" "$min_releases" )
	for version in $versions; do
		echo "$version"
		version_id=$(echo $version |  rev | cut -d'/' -f 1 | rev)
		extracted_zip_dir="appsSauce/$simple_name/"
		mkdir -p "$extracted_zip_dir"
		echo "wget --user=${user_name} --password=${OAUTH_TOKEN} -O \"$extracted_zip_dir/$version_id\" \"$version\"" >> to_download.log
	done
}



index=0
for i in $(cut -f1 -f2 -f6 -f12 -f13 -d,  androzooopen.csv ); do
	data_sauce=$(echo $i | cut -f1 -d,)
	repo_id=$(echo $i | cut -f2 -d,)
	n_releases=$(echo $i | cut -f3 -d,)
	package=$(echo $i | cut -f4 -d,)
	on_play=$(echo $i | cut -f5 -d,)
	#echo "$n_releases -- $on_play"
	if [ "$n_releases" -ge "$min_releases" ] && [ "$on_play" != "No" ]; then
		#echo "$repo_id"
		#  curl --silent "https://api.github.com/repos/01sadra/Detoxiom/releases"
		app_category=$( scrapy runspider play_category_crawler.py  -a url="https://play.google.com/store/apps/details?id=${package}" -s LOG_ENABLED=False  )
		if [[ -n "$app_category" ]]; then
			echo "${package}" >> "$app_category.log"
		else
			echo "${package}" >> "unknown.log"
		fi
		
		if [[ "$data_sauce" == "github" ]]; then
			index=$(($index + 1))
			out_file="appsInfo/$(echo $repo_id| sed 's#/#-#g').json"
			curl -H "Authorization: token ${OAUTH_TOKEN}" --silent "https://api.github.com/repos/${repo_id}/releases" > "$out_file"
			has_error=$(cat "$out_file" | grep "rate limit exceeded")
			if [ -n "$has_error" ]; then
				echo "error. rate limit exceeded. aborting"
				exit 1
			else
				downloadGithubReleases $out_file
			fi

			
		else
			echo "$repo_id" >> "unsupported_$data_sauce.log"
		fi
		
	else
		echo "$repo_id" >> "few_releases.log"
	fi
	
done

echo "total = $index"



