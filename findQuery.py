import gitlab
import json
import time
import readline
import sys
import boto3
import argparse

# To check run time
start_time = time.time()

def get_api_token():
    param_name = "/tools-jenkins/gitlab-api-token"
    region_name = "us-east-1"

    client = boto3.client("ssm", region_name=region_name)

    try:
        return client.get_parameter(
            Name=param_name,
            WithDecryption=True
        )['Parameter']['Value']
    except Exception as e:
        print(f"ERROR: Could not retrieve GitLab token from SSM: {e}")
        sys.exit(1)

ACCESS_TOKEN = get_api_token()

parser = argparse.ArgumentParser(description="GitLab Query Search Script")
parser.add_argument("--SEARCH_WORDS", required=True, help="Search words for the GitLab query")
args = parser.parse_args()

MATCH_PERCENT = 70
TOP_5 = 5
STOPWORDS = {"to", "an", "the", "in", "is", "on", "a", "and", "via", "with", "by", "of", "for", "as", "from", "=", '+'}

SEARCH_WORDS = args.SEARCH_WORDS

#PRIVATE_TOKEN = os.environ['GITLAB_ACCESS_TOKEN']  # Set this in your environment
print(SEARCH_WORDS)

with open("SEARCH_WORDS.TXT", "w") as f:
    f.write(SEARCH_WORDS)

# Parse and count words
words = SEARCH_WORDS.replace(","," ").split()
word_count = len(words)
print("Word count: ", word_count)
print("Original words:", words)

# Filter and sort meaningful words, gets the longest words , hepls filter out "as , in , and ,@ etc"
# As these small words are so common they will have many occurences 
meaningful_words = [w for w in words if w.lower() not in STOPWORDS]
meaningful_words = sorted(meaningful_words, key=len, reverse=True)
search_query = ' '.join(meaningful_words[:TOP_5])
print("GitLab Search Query:", search_query)

# Connect to GitLab
gl = gitlab.Gitlab('https://gitlab.com', private_token=ACCESS_TOKEN, api_version='4')
wh_group = gl.groups.get('workhuman')

# Get the files / data which will be used to match the users input against
try:
    search_blobs = wh_group.search(gitlab.const.SearchScope.BLOBS, search_query, get_all=True, group_id=wh_group.id)
except Exception as e:
    print(f"Search failed: {e}")
    search_blobs = []


print(f"SEARCH BLOBS: {len(search_blobs)} found")


# Function to fetch file content
def get_file_content(project_id, file_path, ref='master'):
    try:
        file = gl.projects.get(project_id).files.get(file_path=file_path, ref=ref)
        return file.decode().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching file {file_path} from project {project_id}: {e}")
        return ""

# Filtered matching results
filtered_results = []

# Group blobs together
unique_files = {}
for sb in search_blobs:
    file_key = f"{sb['project_id']}:{sb['path']}"
    if file_key not in unique_files:
        unique_files[file_key] = sb

print(f"UNIQUE FILES: {len(unique_files)} found (from {len(search_blobs)} search blobs)")

# Match logic for unique files
for file_key, sb in unique_files.items():
    file_path = sb["path"]
    file_content = get_file_content(sb["project_id"], file_path)
    file_content_lower = file_content.lower()

    matched_words = sum(1 for word in words if word.lower() in file_content_lower)
    match_ratio = (matched_words / word_count) * 100

    if match_ratio >= MATCH_PERCENT:
        print(f"{match_ratio:.2f}% match in file: {file_path}")
        filtered_results.append(sb)
    else:
        print(f"{match_ratio:.2f}% match (below threshold) in file: {file_path}")

# Save raw matching blobs
with open("test5-plain_search_blobs.json", 'w') as fp:
    json.dump(filtered_results, fp, indent=4, sort_keys=True)

# Organize by repo
repo_search = {
    "counts": {
        "repositories": 0,
        "string_match": 0
    },
    "repositories": {}
}
seen_repos = set()

for sb in filtered_results:
    project = gl.projects.get(sb["project_id"])
    r_url = project.http_url_to_repo # Chaged from ssh so link is clickable
    r_split_path = project.path_with_namespace.split('/')
    d = repo_search["repositories"]


    if r_url not in seen_repos:
        seen_repos.add(r_url)
        print("\nThe repo can be found here :",r_url)
        print("The file can be found here :",r_url.replace(".git", "/-/blob/master/") + sb['path'])

    for p in r_split_path:
        if p not in d:
            d[p] = {}
        d = d[p]

    if r_url not in d:
        d[r_url] = {}
    
    d[r_url][(sb["filename"])] = {sb["startline"]: sb["data"]}

repo_search["counts"]["repositories"] = len(seen_repos)
repo_search["counts"]["string_match"] = len(filtered_results)

# Save organized results
with open("test5-code_search.json", 'w') as fp:
    json.dump(repo_search, fp, indent=4, sort_keys=True)

# End time
print("%s seconds to complete" % (time.time() - start_time))