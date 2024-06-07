import requests
import re
import json


def parse_r_packages_info(url):
    response = requests.get(url)
    packages_text = response.text.split("\n\n")
    packages = []

    for package_text in packages_text:
        package_info = {}
        last_key = None
        for line in package_text.splitlines():
            if ":" in line:
                key, _, value = line.partition(": ")
                key = key.lower().replace(" ", "")
                if key in ["depends", "imports", "suggests"] and "," in value:
                    package_info[key] = [
                        v.strip()
                        for v in re.split(r",(?![^\(]*\))", value)
                        if v.strip()
                    ]
                else:
                    package_info[key] = [value.strip()] if value.strip() else []
                last_key = key
            elif last_key:
                continued_values = [
                    v.strip() for v in re.split(r",(?![^\(]*\))", line) if v.strip()
                ]
                package_info[last_key].extend(continued_values)

        packages.append(package_info)

    return packages


def main():
    url = "https://cloud.r-project.org/src/contrib/PACKAGES"
    r_packages = parse_r_packages_info(url)

    with open("docs/rPackages.json", "w") as f:
        json.dump(r_packages, f, indent=2)


if __name__ == "__main__":
    main()
