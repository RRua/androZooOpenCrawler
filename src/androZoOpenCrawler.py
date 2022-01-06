import json, csv, os
from utils import execute_shell_command, is_number

def get_config(config_file):
        js = {}
        with open(config_file, 'r') as jj:
            js = json.load(jj)
        return js

class AndroZooOpenCrawler(object):
    def __init__(self,config_file):
        self.config_obj = get_config(config_file)
        self.stats = {'categories': {}}

    def save_release_info(self, app_release_info, target_file):
        with open(target_file,'w') as ww:
            json.dump(app_release_info, ww, indent=1)

    def downloadGithubReleases(self, app_pkg, app_releases, output_dir):
        max_releases = int(self.config_obj['releases_per_app_to_download']) if 'releases_per_app_to_download' in self.config_obj else 10000
        for i,release in enumerate(app_releases):
            if i >= max_releases:
                return
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
            self.save_release_info( release, output_file.replace(".zip", ".json")  )

    def get_app_releases(self, app_repo_id):
        #cmd = f"curl -H "Authorization: token ${OAUTH_TOKEN}" --silent "https://api.github.com/repos/${repo_id}/releases""
        cmd = f"curl https://api.github.com/repos/{app_repo_id}/releases"
        r,o,e = execute_shell_command(cmd)
        return {} if r != 0 else json.loads(o)

    def get_play_store_category(self, app_package):
        cmd = f"scrapy runspider src/play_category_crawler.py  -a url=https://play.google.com/store/apps/details?id={app_package} -s LOG_ENABLED=False"
        r,o,e = execute_shell_command(cmd)
        return None if r != 0 else o.strip()

    def row_passes_filter(self, row):
        for filter, constraints in self.config_obj['filters'].items():
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
    def process_app_line(self, row):
        if not self.row_passes_filter(row):
            return
        app_pkg = row['package_name']
        if row['data_source'].lower() == 'github':
            app_category = self.get_play_store_category(app_pkg)
            self.stats['categories'][app_category] = [app_pkg] if app_category not in self.stats['categories'] else self.stats['categories'][app_category] + [app_pkg]
            app_github_releases = self.get_app_releases(row['entry'])
            out_dir =  os.path.join(self.config_obj['output_dir'], "downloads", app_category , app_pkg)
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)
            print(f'Downloading app {app_pkg}')
            #print(json.dumps(app_github_releases, indent=2))
            self.downloadGithubReleases(app_pkg, app_github_releases, out_dir)
        else:
            raise Exception("Unsupported data source")

    def process_input_file(self):
        with open(self.config_obj['input_file']) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                self.process_app_line(row)

