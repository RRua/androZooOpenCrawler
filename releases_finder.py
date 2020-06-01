import sys,json

def main(jsonfile):
	with open(jsonfile) as json_file:
		data = json.load(json_file)
	if len(data)>0:
		for version in data:
			if 'zipball_url' in version:
				if 'tag_name' in version:
					print( str(version['zipball_url']))




if __name__ == '__main__':
	if len(sys.argv)>1:
		main(sys.argv[1])
	else:
		print("bad arg len")