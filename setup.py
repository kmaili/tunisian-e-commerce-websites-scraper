import pathlib
import setuptools

if __name__ == "__main__":
    name = "e_commerce_scraper"
    license = ("MIT",)
    description = "A bot which scrapes products from tunisian e-commerce websites"

    pkg_name = name.replace("-", "_")
    pkg_path = pathlib.Path(__file__).parent

    with open(pkg_path / "requirements" / "prod") as fp:
        install_requires = fp.readlines()

    with open(pkg_path / "requirements" / "dev") as fd:
        extra_requires_dev = fd.readlines()

    setuptools.setup(
        name=name,
        description=description,
        packages=setuptools.find_packages(exclude=["tests"]),
        install_requires=install_requires,
        setup_requires=["setuptools_scm"],
        extras_require={"dev": extra_requires_dev},
        package_data={"": ["*.exe", "*.txt"]},
        include_package_data=True,
        zip_safe=False,
        python_requires=">=3.6",
    )
