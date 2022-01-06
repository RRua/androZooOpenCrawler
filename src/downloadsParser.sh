# !/bin/sh

for f in $(find appsInfo -name "*_play_info.json"); do
	app_title=$(  grep -Po  -o  "title': '.*?'" "$f" | cut -f3 -d\' )
	app_installs=$(grep -o -E "installs': '[0-9]+(,[0-9]+)?*" "$f" | grep -o -E "[0-9]+(,[0-9]+)?*" | sed 's/,//g' )
	if [[ -z "$app_installs" ]]; then
		continue
	fi

	#echo "$app_title -+- $app_installs"
	if [[ "$app_installs" -ge "1000000" ]]; then
	#	echo "$app_title - $(echo "$app_installs" | sed 's/000000/M/g' )"
		echo "$app_title - ${app_installs%000000}M"
	
	fi
	
done

