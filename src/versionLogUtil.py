
import re

basedir="/media/yy/DiscoExterno/appsSauce/"
app_dict={}
f = open("app_versions.log", "r")
last_app=""
for file in f.readlines():
	app_version = (file.replace(basedir,"").replace("\n",""))
	app = app_version.split("/")[0]
	version = re.sub('[aA-zZ]','', app_version.split("/")[1]).replace("-","")
	
	if app in app_dict:
		app_dict[app]['versions'].append(version)
	else:
		app_dict[app]={}
		app_dict[app]['majors']=set()
		app_dict[app]['minors']=set()
		app_dict[app]['versions']=[]
		app_dict[app]['versions'].append(version)
		##print("---")
	major_minor_patch=re.match("[0-9]+\.[0-9]\.[0-9]",version)
	if major_minor_patch:
		#print("%s matcha - %s"%(version, major_minor_patch.group(0)))
		app_dict[app]['majors'].add(major_minor_patch.group(0).split(".")[0])
		app_dict[app]['minors'].add((major_minor_patch.group(0).split(".")[1] ) )

majors=0
minors=0
for app in app_dict.values():
	if len(app['majors'])>2:
		majors=majors+1
	if len(app['minors'])>2:
		minors=minors+1
	#print(app['minors'])
print(majors)
print(minors)