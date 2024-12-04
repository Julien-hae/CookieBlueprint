import dataclasses
import pathlib
import shutil
import subprocess
import tempfile
import unittest

import tomli
import yaml
from cookiecutter import generate, main, prompt

USER_CONFIG = """
cookiecutters_dir: "{cookiecutters_dir}"
replay_dir: "{replay_dir}"
"""


def _run_shell_command_in_dir(command: list[str], dir: str) -> tuple[bytes, bytes, int]:
    with subprocess.Popen(
        command, cwd=dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ) as proc:
        outs, errs = proc.communicate()
        returncode = proc.returncode
    return outs, errs, returncode


@dataclasses.dataclass
class Result:
    project_dir: str
    exception: BaseException | None = None
    exit_code: int | None = 0
    context: pathlib.Path | None = None

    def is_success(self):
        return self.exit_code == 0

    def __repr__(self):
        if self.exception:
            return "<Result {!r}>".format(self.exception)

        return "<Result {}>".format(self.project_dir)


class CookieOven:
    """By and large taken from pytest-cookies"""

    def __init__(self, template, config_file=USER_CONFIG) -> None:
        self._default_template = template
        self._config_file = config_file
        self._counter = 0
        self.exception: BaseException | None = None
        self.exit_code: int | None = 0
        self.project_dir: str = ""
        self.output_dir = tempfile.mkdtemp(prefix="cookies")
        self.context: pathlib.Path | None = None

    def bake(
        self, extra_context: dict[str, str] = {}, template: str | None = None
    ) -> Result:
        if template is None:
            template = self._default_template

        context_file = pathlib.Path(template) / "cookiecutter.json"

        try:
            # Render the context, so that we can store it on the Result
            self.context = prompt.prompt_for_config(
                generate.generate_context(
                    context_file=str(context_file), extra_context=extra_context
                ),
                no_input=True,
            )

            # Run cookiecutter to generate a new project
            self.project_dir = main.cookiecutter(
                template,
                no_input=True,
                extra_context=extra_context,
                output_dir=str(self.output_dir),
            )

        except SystemExit as e:
            if e.code != 0:
                self.exception = e
            try:
                self.exit_code = int(str(e.code))
            except ValueError:
                self.exit_code = None

        except Exception as e:
            self.exception = e
            self.exit_code = -1

        return Result(
            exception=self.exception,
            exit_code=self.exit_code,
            project_dir=self.project_dir,
            context=self.context,
        )


class TestCookiecutter(unittest.TestCase):
    def setUp(self) -> None:
        self.oven = CookieOven(template=str(pathlib.Path(__file__).parents[2]))

    def tearDown(self) -> None:
        shutil.rmtree(self.oven.output_dir)

    def test_dot_python_version(self) -> None:
        # Prepare / Run
        cookies = self.oven.bake()

        self.assertTrue(cookies.is_success(), msg=cookies.exception)

        self.assertEqual(
            "3.11\n",
            (pathlib.Path(cookies.project_dir) / ".python-version").read_text(),
        )

    def test_pyproject_toml(self) -> None:
        # Prepare / Run
        cookies = self.oven.bake(
            extra_context={
                "bitbucket_organization": "bitbucket",
                "author_email": "first-name.last-name@sbb.ch",
            }
        )

        self.assertTrue(cookies.is_success(), msg=cookies.exception)

        with open(pathlib.Path(cookies.project_dir) / "pyproject.toml", "rb") as fh:
            pyproject = tomli.load(fh)

        # Check
        self.assertEqual(pyproject["tool"]["poetry"]["name"], "sbb-esta-python")
        self.assertEqual(
            pyproject["tool"]["poetry"]["description"],
            "Blueprint for a basic Python codebase",
        )
        self.assertEqual(
            pyproject["tool"]["poetry"]["authors"],
            ["your-last-name your-first-name <first-name.last-name@sbb.ch>"],
        )
        self.assertEqual(
            pyproject["tool"]["poetry"]["repository"],
            "https://code.sbb.ch/projects/bitbucket/repos/esta-python",
        )
        self.assertEqual(
            pyproject["tool"]["poetry"]["documentation"],
            "https://code.sbb.ch/projects/bitbucket/repos/esta-python/browse/README.md",
        )
        self.assertEqual(
            pyproject["tool"]["poetry"]["packages"],
            [{"include": "esta_python", "from": "src"}],
        )
        self.assertEqual(pyproject["tool"]["poetry"]["dependencies"]["python"], "~3.11")

    def test_with_docker(self) -> None:
        # Prepare / Run
        cookies = self.oven.bake(
            extra_context={"docker_repository": "esta.docker", "python_version": "3.9"}
        )

        self.assertTrue(cookies.is_success(), msg=cookies.exception)

        # Check
        # Dockerfile exists
        self.assertTrue(
            pathlib.Path(cookies.project_dir).joinpath("Dockerfile").is_file()
        )

        # Dockerignore exists
        self.assertTrue(
            pathlib.Path(cookies.project_dir).joinpath(".dockerignore").is_file()
        )

        with open(f"{cookies.project_dir}/Dockerfile", "r") as fh:
            from_instruction = fh.readline()

        self.assertEqual(
            from_instruction,
            "FROM registry-redhat.docker.bin.sbb.ch/rhel9/python-39 AS base\n",
        )

        # Tekton-Pipeline
        with open(f"{cookies.project_dir}/estaTektonPipeline.yaml", "r") as fh:
            tekton_pipeline = yaml.safe_load(fh)

        # Tekton-Docker section
        self.assertEqual(
            tekton_pipeline["docker"], {"artifactoryDockerRepo": "esta.docker"}
        )
        continuous_build = tekton_pipeline["pipelines"][0]["build"]
        snapshot_build = tekton_pipeline["pipelines"][1]["build"]
        release_build = tekton_pipeline["pipelines"][2]["build"]

        # Check build sections
        self.assertEqual(
            continuous_build,
            {
                "sonarScan": {"enabled": True},
                "owaspDependencyCheck": {
                    "enabled": True,
                    "additionalParams": "--suppression dependency-check-suppressions.xml --disablePyDist --disablePyPkg --failOnCVSS 11",
                },
                "failOnQualityGateFailure": False,
                "buildDockerImage": True,
                "deployDockerImage": False,
            },
        )
        self.assertEqual(
            snapshot_build,
            {
                "sonarScan": {"enabled": True},
                "owaspDependencyCheck": {
                    "enabled": True,
                    "additionalParams": "--suppression dependency-check-suppressions.xml --disablePyDist --disablePyPkg --failOnCVSS 11",
                },
                "failOnQualityGateFailure": False,
                "buildDockerImage": True,
                "deployDockerImage": True,
                "deployArtifacts": False,
            },
        )
        self.assertEqual(
            release_build,
            {
                "sonarScan": {"enabled": True},
                "owaspDependencyCheck": {
                    "enabled": True,
                    "additionalParams": "--suppression dependency-check-suppressions.xml --disablePyDist --disablePyPkg --failOnCVSS 11",
                },
                "failOnQualityGateFailure": False,
                "buildDockerImage": True,
                "deployArtifacts": True,
                "additionalDockerImageTags": ["latest"],
            },
        )

    def test_without_docker(self) -> None:
        # Prepare / Run
        cookies = self.oven.bake(
            extra_context={"docker_repository": "", "python_version": "3.11"}
        )

        self.assertTrue(cookies.is_success(), msg=cookies.exception)

        # Check
        # Dockerfile does not exist
        self.assertFalse(
            pathlib.Path(cookies.project_dir).joinpath("Dockerfile").exists()
        )

        # Dockerignore does not exist
        self.assertFalse(
            pathlib.Path(cookies.project_dir).joinpath(".dockerignore").exists()
        )

        # Tekton-Pipeline
        with open(f"{cookies.project_dir}/estaTektonPipeline.yaml", "r") as fh:
            tekton_pipeline = yaml.safe_load(fh)

        # Tekton-Docker section
        self.assertNotIn("docker", tekton_pipeline)

        # Check build sections
        for i, pipeline in enumerate(["continuous", "snapshot", "release"]):
            with self.subTest(msg=f"Checking pipeline: '{pipeline}'."):
                self.assertEqual(
                    tekton_pipeline["pipelines"][i]["build"],
                    {
                        "sonarScan": {"enabled": True},
                        "owaspDependencyCheck": {
                            "enabled": True,
                            "additionalParams": "--suppression dependency-check-suppressions.xml --disablePyDist --disablePyPkg --failOnCVSS 11",
                        },
                        "failOnQualityGateFailure": False,
                    },
                )

    def test_with_pypi(self) -> None:
        # Prepare / Run
        cookies = self.oven.bake(extra_context={"pypi_repository": "esta.pypi"})

        self.assertTrue(cookies.is_success(), msg=cookies.exception)

        # Check Tekton-Pipeline
        with open(f"{cookies.project_dir}/estaTektonPipeline.yaml", "r") as fh:
            tekton_pipeline = yaml.safe_load(fh)
        self.assertEqual(tekton_pipeline["python"], {"targetRepo": "esta.pypi"})

    def test_without_pypi(self) -> None:
        # Prepare / Run
        cookies = self.oven.bake(extra_context={"pypi_repository": ""})

        self.assertTrue(cookies.is_success(), msg=cookies.exception)

        # Check Tekton-Pipeline
        with open(f"{cookies.project_dir}/estaTektonPipeline.yaml", "r") as fh:
            tekton_pipeline = yaml.safe_load(fh)
        self.assertEqual(tekton_pipeline["python"], {})

    def test_pre_commit_hooks_in_template(self) -> None:
        # Prepare
        cookies = self.oven.bake(
            extra_context={"author_email": "first-name.last-name@sbb.ch"}
        )

        self.assertTrue(cookies.is_success(), msg=cookies.exception)

        outs, errs, _ = _run_shell_command_in_dir(
            ["git", "init"], dir=cookies.project_dir
        )
        outs, errs, _ = _run_shell_command_in_dir(
            ["git", "add", "--all"], dir=cookies.project_dir
        )

        # Run
        commands = [
            ["make"],
            ["poetry", "run", "pre-commit", "run", "--all-files"],
        ]

        # Check
        for command in commands:
            with self.subTest(msg=f"Running {command=}."):
                stdout, stderr, returncode = _run_shell_command_in_dir(
                    command=command, dir=cookies.project_dir
                )
                self.assertEqual(
                    returncode,
                    0,
                    msg=f"\nstdout:\n{stdout.decode()}\nstderr:\n{stderr.decode()}.",
                )

    def test_directory_names(self) -> None:
        # Prepare / Run
        cookies = self.oven.bake(extra_context={"project_name": "Funky Grogu"})

        self.assertTrue(cookies.is_success(), msg=cookies.exception)

        # Check
        self.assertTrue(pathlib.Path(cookies.project_dir).is_dir())
        self.assertTrue(
            pathlib.Path(cookies.project_dir).joinpath("src", "funky_grogu").is_dir()
        )
        self.assertTrue(
            pathlib.Path(cookies.project_dir).joinpath("tests", "funky_grogu").is_dir()
        )

    def test_poetry_tompl(self) -> None:
        # Prepare / Run
        cookies = self.oven.bake(extra_context={"pypi_repository": "esta-python.pypi"})

        self.assertTrue(cookies.is_success(), msg=cookies.exception)

        with open(pathlib.Path(cookies.project_dir) / "poetry.toml", "rb") as fh:
            poetry = tomli.load(fh)

        # Check
        self.assertEqual(
            poetry["repositories"]["artifactory"]["url"],
            "https://bin.sbb.ch/artifactory/api/pypi/esta-python.pypi",
        )
