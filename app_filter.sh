# !/bin/bash

user_name=$(head -1 github_id.txt ) # place here your github id #"RRua"
min_releases=1

test -z "$user_name" && echo "please specify your github id "
test  ! -f oauth_token.txt && echo "github oauth token not found. please generate oauth token (https://help.github.com/pt/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line) and place it in oauth_token.txt file" && exit 2
auth_len=$(echo "oauth_token.txt" | wc -l )
test  "$auth_len" -eq "0"  && echo "github oauth token not found. please generate oauth token (https://help.github.com/pt/github/authenticating-to-github/creating-a-personal-access-token-for-the-command-line) and place it in oauth_token.txt file" && exit 2


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
		wget --user=${user_name} --password=${OAUTH_TOKEN} -O "$extracted_zip_dir/$version_id" "$version" #>> to_download.log
	done
}



index=0
for i in $( tail -n +2  androzooopen.csv | cut -f1,2,6,12,13 -d, ); do
	package=$(echo $i | cut -f4 -d,)

	nm=$(grep "$package" security_packages.log | wc -l )
	test "$nm" -eq "0" && echo "skipping --------- "&& continue
	
	data_sauce=$(echo $i | cut -f1 -d,)
	repo_id=$(echo $i | cut -f2 -d,)
	n_releases=$(echo $i | cut -f3 -d,)
	on_play=$(echo $i | cut -f5 -d,)
	#echo "$n_releases -- $on_play"
	
	 
	#if [ "$n_releases" -ge "$min_releases" ] && [ "$on_play" != "No" ]; then
		#echo  "${package}" 
		#continue
		#echo "$repo_id"
		#  curl --silent "https://api.github.com/repos/01sadra/Detoxiom/releases"
		#app_category=$( scrapy runspider play_category_crawler.py  -a url="https://play.google.com/store/apps/details?id=${package}" -s LOG_ENABLED=False  )
		#if [[ -n "$app_category" ]]; then
		#	echo "${package}" >> "categories/$app_category.log"
		#else
		#	echo "${package}" >> "categories/unknown.log"
		#fi


	if [[ "$data_sauce" == "github" ]]; then
		echo "$repo_id"
		index=$(($index + 1))
		out_file="appsInfo/$(echo $repo_id| sed 's#/#-#g').json"
		curl -H "Authorization: token ${OAUTH_TOKEN}" --silent "https://api.github.com/repos/${repo_id}/releases" > "$out_file"
		has_error=$(cat "$out_file" | grep "rate limit exceeded")
		if [ -n "$has_error" ]; then
			echo "error. rate limit exceeded. aborting"
			exit 1
		else
			echo "downloading $package"
			downloadGithubReleases $out_file
			#python3 playscraper.py "${package}" > "appsInfo/$(echo $repo_id| sed 's#/#-#g')_play_info.json"
		fi

		
	else
		echo "$repo_id" >> "unsupported_$data_sauce.log"
	fi
		
	#else
	#	echo "$repo_id" >> "few_releases.log"
	#fi
	
	
done

echo "total = $index"



