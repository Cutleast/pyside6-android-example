"""
Copyright (c) Cutleast

Builds an Android APK with `pyside6-android-deploy` (python-for-android + buildozer).

This only works on Linux or macOS and requires the Android SDK, NDK r28c, a JDK (17+)
and rustup (for pydantic-core). It is meant to be run by the GitHub Actions workflow
but also works locally (e.g. in WSL). Run this from the project's root folder with a
Python environment that contains `pyside6`, `buildozer==1.6.0` and `cython==0.29.33`
(the Android build tooling is not part of the project's dependencies, see
`.github/workflows/build_android.yaml`):

    python scripts/build_android.py --sdk-path <sdk> --ndk-path <ndk>

The APK is written to `./dist`.
"""

import argparse
import configparser
import logging
import os
import re
import shutil
import subprocess
import sys
import tomllib
import urllib.request
from pathlib import Path

import PySide6

log: logging.Logger = logging.getLogger("AndroidBuilder")

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
"""The root folder of the project."""

BUILD_FOLDER: Path = PROJECT_ROOT / "build" / "android"
"""The folder for all intermediate build files."""

STAGING_FOLDER: Path = BUILD_FOLDER / "app"
"""The folder with the app sources that get packaged into the APK."""

WHEELS_FOLDER: Path = BUILD_FOLDER / "wheels"
"""The folder for the downloaded PySide6 and shiboken6 Android wheels."""

DIST_FOLDER: Path = PROJECT_ROOT / "dist"
"""The folder for the final APK."""

CORE_LIB_FOLDER: Path = PROJECT_ROOT / "core-lib" / "src" / "cutleast_core_lib"
"""The core lib package that gets bundled with the app sources."""

CORE_LIB_EXCLUDES: list[str] = ["builder", "scripts", "test", "res"]
"""Core lib subpackages that are only required for development or Windows."""

RESOURCE_MODULES: dict[Path, Path] = {
    PROJECT_ROOT / "res" / "resources.qrc": Path("resources_rc.py"),
    PROJECT_ROOT / "core-lib" / "res" / "resources.qrc": (
        Path(CORE_LIB_FOLDER.name) / "ui" / "resources_rc.py"
    ),
}
"""Qt resource collections and the staged modules they are compiled to."""

SHIMS_FOLDER: Path = PROJECT_ROOT / "android" / "shims"
"""Modules replacing dependencies that cannot be built for Android."""

WHEEL_URL: str = (
    "https://download.qt.io/official_releases/QtForPython/{package}/"
    "{package}-{version}-{version}-cp310-abi3-android_{arch}.whl"
)
"""Download URL of the official Qt for Python Android wheels."""

REQUIREMENTS: list[str] = [
    # pydantic must match the version of the pydantic-core recipe of python-for-android
    "pydantic==2.12.3",
    "pydantic-core",
    "annotated-types",
    "typing-extensions",
    "typing-inspection",
    "jstyleson",
    # replaces material-color-utilities, see android/shims/material_color_utilities.py
    "materialyoucolor",
    "qtawesome",
    "qtpy",
    "packaging",
    "requests",
    "urllib3",
    "idna",
    "certifi",
    "charset-normalizer",
    "semantic-version",
    "virtual-glob",
]
"""Python packages bundled additionally to PySide6 (python-for-android requirements)."""

EXTRA_QT_MODULES: list[str] = ["Svg"]
"""
Qt modules that are not imported directly but are required at runtime (e.g. for SVG
icons).
"""

REQUIRED_QT_PLUGINS: list[str] = ["imageformats_qsvg", "iconengines_qsvgicon"]
"""
Qt plugins (`<category>_<name>`) required for the SVG icons and stylesheet images. They
are added if `pyside6-android-deploy` does not detect them itself.
"""

APP_TITLE: str = "PySide6 Example"
"""The app name displayed in the Android launcher."""

PACKAGE_NAME: str = "pyside6example"
"""The Android package name (without domain)."""

PACKAGE_DOMAIN: str = "io.github.cutleast"
"""The Android package domain."""

VERSION_PATTERN: re.Pattern[str] = re.compile(r'(?<=APP_VERSION: str = ")[^"]+(?=")')
"""Pattern for injecting the version into the app module."""


def get_project_version() -> str:
    """
    Returns:
        str: The project version from pyproject.toml.
    """

    with (PROJECT_ROOT / "pyproject.toml").open("rb") as file:
        return tomllib.load(file)["project"]["version"]


def get_build_env() -> dict[str, str]:
    """
    Returns:
        dict[str, str]:
            The environment for the build tools with the current virtual environment
            activated, so that buildozer finds its tools (e.g. `cython`).
    """

    env: dict[str, str] = os.environ.copy()
    env["VIRTUAL_ENV"] = sys.prefix
    env["PATH"] = os.pathsep.join([str(Path(sys.executable).parent), env["PATH"]])

    return env


def stage_sources(version: str) -> None:
    """
    Copies the app sources, the core lib and the Android shims into the staging folder.
    The buildozer cache in the staging folder is kept to speed up subsequent builds.

    Args:
        version (str): The version to inject into the app module.
    """

    STAGING_FOLDER.mkdir(parents=True, exist_ok=True)
    for item in STAGING_FOLDER.iterdir():
        if item.name == ".buildozer":
            continue

        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
    shutil.copytree(
        PROJECT_ROOT / "src", STAGING_FOLDER, ignore=ignore, dirs_exist_ok=True
    )
    shutil.copytree(
        CORE_LIB_FOLDER,
        STAGING_FOLDER / CORE_LIB_FOLDER.name,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", *CORE_LIB_EXCLUDES),
    )
    for shim in SHIMS_FOLDER.glob("*.py"):
        shutil.copy2(shim, STAGING_FOLDER)

    app_module: Path = STAGING_FOLDER / "app.py"
    app_module.write_text(
        VERSION_PATTERN.sub(version, app_module.read_text(encoding="utf8")),
        encoding="utf8",
    )
    log.info(f"Staged sources in '{STAGING_FOLDER}' (version {version}).")


def compile_resources() -> None:
    """
    Compiles the Qt resources of the app and the core lib into the staging folder.

    The desktop builds of Qt compress resources with zstd by default, but Qt for Android
    is built without zstd support and fails to open such resources. So they are
    compiled without compression instead.
    """

    rcc: Path = Path(sys.executable).parent / "pyside6-rcc"
    for qrc_file, module in RESOURCE_MODULES.items():
        subprocess.run(
            [
                str(rcc),
                "--no-compress",
                str(qrc_file),
                "-o",
                str(STAGING_FOLDER / module),
            ],
            check=True,
        )
        log.info(f"Compiled '{qrc_file}' to '{module}'.")


def download_wheel(package: str, version: str, arch: str) -> Path:
    """
    Downloads an official Qt for Python Android wheel if it isn't already cached.

    Args:
        package (str): The package name (`pyside6` or `shiboken6`).
        version (str): The PySide6 version.
        arch (str): The Android architecture (`aarch64` or `x86_64`).

    Returns:
        Path: The path to the downloaded wheel.
    """

    url: str = WHEEL_URL.format(package=package, version=version, arch=arch)
    wheel_path: Path = WHEELS_FOLDER / url.rsplit("/", 1)[-1]

    if not wheel_path.is_file():
        WHEELS_FOLDER.mkdir(parents=True, exist_ok=True)
        log.info(f"Downloading '{url}'...")
        urllib.request.urlretrieve(url, wheel_path)

    return wheel_path


def init_deployment(
    pyside_wheel: Path, shiboken_wheel: Path, sdk_path: Path, ndk_path: Path
) -> None:
    """
    Runs `pyside6-android-deploy --init` to generate the p4a recipes for PySide6 and
    shiboken6 and the buildozer.spec file. If required Qt plugins were not detected,
    they are added to the generated pysidedeploy.spec and the deployment files are
    generated again from it.

    Args:
        pyside_wheel (Path): Path to the PySide6 Android wheel.
        shiboken_wheel (Path): Path to the shiboken6 Android wheel.
        sdk_path (Path): Path to the Android SDK.
        ndk_path (Path): Path to the Android NDK.
    """

    deploy_tool: Path = Path(sys.executable).parent / "pyside6-android-deploy"
    command: list[str] = [
        str(deploy_tool),
        "--init",
        "--force",
        "--verbose",
        "--keep-deployment-files",
        "--no-install",
        f"--name={PACKAGE_NAME}",
        f"--wheel-pyside={pyside_wheel}",
        f"--wheel-shiboken={shiboken_wheel}",
        f"--sdk-path={sdk_path}",
        f"--ndk-path={ndk_path}",
        f"--extra-modules={','.join(EXTRA_QT_MODULES)}",
    ]
    subprocess.run(command, cwd=STAGING_FOLDER, env=get_build_env(), check=True)

    config_file: Path = STAGING_FOLDER / "pysidedeploy.spec"
    config = configparser.ConfigParser(interpolation=None)
    config.read(config_file, encoding="utf8")
    plugins: list[str] = [
        plugin for plugin in config["android"].get("plugins", "").split(",") if plugin
    ]
    log.info(f"Detected Qt plugins: {plugins}")

    missing_plugins: list[str] = [p for p in REQUIRED_QT_PLUGINS if p not in plugins]
    if missing_plugins:
        log.info(f"Adding missing Qt plugins: {missing_plugins}")
        config["android"]["plugins"] = ",".join(plugins + missing_plugins)
        with config_file.open("w", encoding="utf8") as file:
            config.write(file)

        subprocess.run(
            command + [f"--config-file={config_file}"],
            cwd=STAGING_FOLDER,
            env=get_build_env(),
            check=True,
        )


def patch_buildozer_spec(version: str) -> None:
    """
    Adds the app's Python requirements and metadata to the generated buildozer.spec.

    Args:
        version (str): The app version.
    """

    spec_file: Path = STAGING_FOLDER / "buildozer.spec"
    spec = configparser.ConfigParser(interpolation=None)
    spec.optionxform = str  # type: ignore[assignment]
    spec.read(spec_file, encoding="utf8")

    app = spec["app"]
    requirements: list[str] = app["requirements"].split(",") + REQUIREMENTS
    app["requirements"] = ",".join(requirements)
    app["title"] = APP_TITLE
    app["package.name"] = PACKAGE_NAME
    app["package.domain"] = PACKAGE_DOMAIN
    app["version"] = version
    app.pop("version.regex", None)
    app.pop("version.filename", None)
    app["source.exclude_dirs"] = "deployment,bin,.buildozer"
    app["android.accept_sdk_license"] = "True"
    app["android.skip_update"] = "True"
    app["android.allow_backup"] = "False"
    app["orientation"] = "portrait"

    with spec_file.open("w", encoding="utf8") as file:
        spec.write(file)

    log.info(f"Requirements: {app['requirements']}")
    log.info(f"Qt modules: {app.get('p4a.extra_args')}")


def build_apk() -> Path:
    """
    Builds the debug APK with buildozer and copies it to the dist folder.

    Returns:
        Path: The path to the APK in the dist folder.
    """

    subprocess.run(
        [sys.executable, "-m", "buildozer", "android", "debug"],
        cwd=STAGING_FOLDER,
        env=get_build_env(),
        check=True,
    )

    apks: list[Path] = sorted(
        STAGING_FOLDER.rglob("*.apk"), key=lambda apk: apk.stat().st_mtime
    )
    if not apks:
        raise FileNotFoundError(f"No APK was built in '{STAGING_FOLDER}'!")

    DIST_FOLDER.mkdir(exist_ok=True)
    apk: Path = Path(shutil.copy2(apks[-1], DIST_FOLDER))
    log.info(f"APK built: '{apk}'.")

    return apk


def main() -> None:
    """
    Parses the commandline arguments and runs the build.
    """

    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[1])
    parser.add_argument("--sdk-path", type=Path, required=True)
    parser.add_argument("--ndk-path", type=Path, required=True)
    parser.add_argument("--arch", choices=["aarch64", "x86_64"], default="aarch64")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    version: str = get_project_version()
    pyside_version: str = PySide6.__version__

    stage_sources(version)
    compile_resources()
    pyside_wheel: Path = download_wheel("pyside6", pyside_version, args.arch)
    shiboken_wheel: Path = download_wheel("shiboken6", pyside_version, args.arch)
    init_deployment(
        pyside_wheel, shiboken_wheel, args.sdk_path.resolve(), args.ndk_path.resolve()
    )
    patch_buildozer_spec(version)
    build_apk()


if __name__ == "__main__":
    main()
