import json, csv, os
from utils import execute_shell_command, is_number

CONFIG_FILE="config.json"

def get_config(config_file=CONFIG_FILE):
    js = {}
    with open(config_file, 'r') as jj:
        js = json.load(jj)
    return js


def downloadGithubReleases(app_pkg, app_releases, output_dir, max_releases=100):
    for i,release in enumerate(app_releases):
        if i > max_releases:
            return
        #print(json.dumps(release, indent=1))
        zip_url = release['zipball_url']
        version = "unknown" if "tag_name" not in release else release['tag_name']
        out_dir = os.path.join(output_dir, version)
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        output_file =  os.path.join( out_dir, f"{app_pkg}-{version}.zip")
        cmd = f"wget -O {output_file} {zip_url}"
        r,o,e = execute_shell_command(cmd)
        if r!=0:
            raise Exception(f"error in command {cmd}")

def get_app_releases(app_repo_id):
    #cmd = f"curl -H "Authorization: token ${OAUTH_TOKEN}" --silent "https://api.github.com/repos/${repo_id}/releases""
    cmd = f"curl https://api.github.com/repos/{app_repo_id}/releases"
    r,o,e = execute_shell_command(cmd)
    return {} if r != 0 else json.loads(o)

def get_play_store_category(app_package):
    cmd = f"scrapy runspider src/play_category_crawler.py  -a url=https://play.google.com/store/apps/details?id={app_package} -s LOG_ENABLED=False"
    r,o,e = execute_shell_command(cmd)
    return None if r != 0 else o.strip()

def row_passes_filter(row, filters):
    for filter, constraints in filters.items():
        matching_field = row[filter]
        for const, v in constraints.items():
            if const == "value" and str(v) != str(matching_field):
                if is_number(v) and is_number(matching_field) and float(v) == float(matching_field):
                    continue
                return False
            elif const == "min"  and is_number(v) and is_number(matching_field) and float(matching_field) < float(v) :
                return False
            elif const == "max"  and is_number(v) and is_number(matching_field) and float(matching_field) > float(v) :
                return False
            elif const not in ['value', 'max', 'min']:
                raise Exception(f"invalid constraint in filters of config file (filter: {filter} | constraint: {const} )")
    return True

# assuming 1 app per row
def process_app_line(row, config_obj, stats):
    if row_passes_filter(row, config_obj['filters']):
        app_pkg = row['package_name']
        app_category = get_play_store_category(app_pkg)
        stats['categories'][app_category] = [app_pkg] if app_category not in stats['categories'] else stats['categories'][app_category] + [app_pkg]
        app_github_releases = get_app_releases(row['entry'])
        out_dir =  os.path.join("out/downloads", app_pkg)
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        print(f'Downloading app {app_pkg}')
        #print(json.dumps(app_github_releases, indent=2))
        max_releases_to_download= 1 #TODO 
        downloadGithubReleases(app_pkg, app_github_releases, out_dir, max_releases=max_releases_to_download)
    #print(stats)

def process_input_file(config_obj,stats):
    with open(config_obj['input_file']) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            process_app_line(row,config_obj,stats)

def main(config_obj):
    stats = {'categories':{}}
    process_input_file(config_obj,stats)
    print(stats)

if __name__ == '__main__':
    x = get_config()
    main(x)