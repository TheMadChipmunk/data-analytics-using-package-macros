"""
Test Using Package Macros

Validates that student has:
- Created packages.yml declaring dbt_utils
- Installed dbt_utils with dbt deps
- Refactored int_marketing_campaigns.sql to use dbt_utils.safe_divide()
"""

import pytest
from pathlib import Path
import yaml


@pytest.fixture
def greenweez_dbt_dir():
    """Get greenweez_dbt/ directory within challenge repo."""
    project_dir = Path(__file__).parent.parent / "greenweez_dbt"
    assert project_dir.exists(), (
        f"❌ greenweez_dbt/ directory not found in {Path(__file__).parent.parent}\n"
        f"   Did you copy your dbt project from the previous challenge? (Section 0)\n"
        f"   First check which challenge directory to copy from: ls ..\n"
        f"   Then run: cp -r ../PREVIOUS-CHALLENGE/greenweez_dbt ."
    )
    return project_dir


class TestPackagesConfig:
    """Checkpoint: packages.yml is defined and contains dbt_utils."""

    @pytest.fixture
    def packages_file(self, greenweez_dbt_dir):
        """Get packages.yml."""
        f = greenweez_dbt_dir / "packages.yml"
        return f if f.exists() else None

    def test_packages_yml_exists(self, packages_file):
        """greenweez_dbt/packages.yml must exist."""
        assert packages_file is not None, (
            "❌ packages.yml not found in greenweez_dbt/\n"
            "   Create it to declare the dbt_utils dependency:\n"
            "   packages:\n"
            "     - package: dbt-labs/dbt_utils\n"
            "       version: 1.1.1"
        )

    def test_packages_yml_is_valid_yaml(self, packages_file):
        """packages.yml must contain valid YAML."""
        if packages_file is None:
            pytest.skip("packages.yml not found")
        try:
            with open(packages_file, 'r') as f:
                yaml.safe_load(f)
        except yaml.YAMLError as e:
            pytest.fail(
                f"❌ packages.yml has invalid YAML syntax\n"
                f"   Error: {str(e)}"
            )

    def test_packages_yml_has_packages_key(self, packages_file):
        """packages.yml must have a 'packages' key."""
        if packages_file is None:
            pytest.skip("packages.yml not found")
        with open(packages_file, 'r') as f:
            content = yaml.safe_load(f)
        assert content and 'packages' in content, (
            "❌ packages.yml is missing the 'packages' key\n"
            "   Add:\n"
            "   packages:\n"
            "     - package: dbt-labs/dbt_utils\n"
            "       version: 1.1.1"
        )

    def test_packages_yml_includes_dbt_utils(self, packages_file):
        """packages.yml must declare dbt-labs/dbt_utils."""
        if packages_file is None:
            pytest.skip("packages.yml not found")
        with open(packages_file, 'r') as f:
            content = yaml.safe_load(f)
        if not content or 'packages' not in content:
            pytest.skip("No packages key")

        packages = content['packages']
        # Accept either 'package: dbt-labs/dbt_utils' or 'git:' style
        has_dbt_utils = any(
            'dbt_utils' in str(pkg.get('package', '')) or
            'dbt_utils' in str(pkg.get('git', ''))
            for pkg in packages
        )
        assert has_dbt_utils, (
            "❌ packages.yml does not include dbt_utils\n"
            "   Add the dbt_utils package:\n"
            "   packages:\n"
            "     - package: dbt-labs/dbt_utils\n"
            "       version: 1.1.1"
        )
