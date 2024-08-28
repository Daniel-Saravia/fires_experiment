import requests
import subprocess

def get_latest_version(package_name):
    # Query the PyPI API for package information
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        latest_version = data['info']['version']
        return latest_version
    else:
        print(f"Could not retrieve version information for {package_name}")
        return None

def update_requirements_file(input_file='requirements.txt', output_file='updated_requirements.txt'):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            if '==' in line:
                package = line.strip().split('==')[0]
                latest_version = get_latest_version(package)
                if latest_version:
                    outfile.write(f"{package}=={latest_version}\n")
                    print(f"Updated {package} to {latest_version}")
                else:
                    outfile.write(line)
                    print(f"Kept {package} at its current version")
            else:
                # Write lines that don't specify a version as is
                outfile.write(line)

if __name__ == "__main__":
    update_requirements_file()