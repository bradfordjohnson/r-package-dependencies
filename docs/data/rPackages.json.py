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

    nodes = []
    links = []

    for package in r_packages:
        nodes.append(
            {
                "package": package["package"],
                "group": "group 1",
            }
        )

        if "imports" in package:
            for dependency in package["imports"]:
                links.append(
                    {"source": package["package"], "target": dependency, "value": 1}
                )

    unique_packages = set(link["target"] for link in links)

    nodes.extend(
        {
            "package": package,
            "group": "group 2",
        }
        for package in unique_packages
    )

    r_packages_wrangled = {"nodes": nodes, "links": links}

    with open("docs/data/rPackages.json", "w") as f:
        json.dump(r_packages_wrangled, f, indent=2)


if __name__ == "__main__":
    main()
