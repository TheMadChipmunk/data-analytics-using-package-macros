"""
Test Using Package Macros — Model Refactoring

Validates that student has:
- Replaced manual CASE WHEN division guards with dbt_utils.safe_divide()
- int_marketing_campaigns.sql no longer contains the manual guard pattern
"""

import pytest
from pathlib import Path


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


@pytest.fixture
def int_campaigns_file(greenweez_dbt_dir):
    """Get int_marketing_campaigns.sql."""
    return greenweez_dbt_dir / "models" / "intermediate" / "int_marketing_campaigns.sql"


class TestModelRefactored:
    """Checkpoint: int_marketing_campaigns.sql uses dbt_utils.safe_divide."""

    def test_int_marketing_campaigns_exists(self, int_campaigns_file):
        """models/intermediate/int_marketing_campaigns.sql must exist."""
        assert int_campaigns_file.exists(), (
            "❌ models/intermediate/int_marketing_campaigns.sql not found\n"
            "   Did you copy your dbt project from the previous challenge? (Section 0)\n"
            "   First check which challenge directory to copy from: ls ..\n"
            "   Then run: cp -r ../PREVIOUS-CHALLENGE/greenweez_dbt ."
        )

    def test_uses_safe_divide(self, int_campaigns_file):
        """int_marketing_campaigns.sql must call dbt_utils.safe_divide()."""
        if not int_campaigns_file.exists():
            pytest.skip("int_marketing_campaigns.sql doesn't exist yet")
        content = int_campaigns_file.read_text()
        assert "safe_divide" in content, (
            "❌ int_marketing_campaigns.sql does not use dbt_utils.safe_divide()\n"
            "   Replace the manual CASE WHEN guards with:\n"
            "   {{ dbt_utils.safe_divide('ads_clicks * 1.0', 'ads_impressions') }} as click_through_rate,\n"
            "   {{ dbt_utils.safe_divide('ads_cost', 'ads_clicks') }} as cost_per_click"
        )

    def test_manual_guard_removed_ctr(self, int_campaigns_file):
        """int_marketing_campaigns.sql should not still have the manual CTR guard."""
        if not int_campaigns_file.exists():
            pytest.skip("int_marketing_campaigns.sql doesn't exist yet")
        content = int_campaigns_file.read_text().lower()
        # The old manual guard pattern checked ads_impressions > 0
        has_manual_guard = (
            "case when ads_impressions" in content or
            "case when ads_impressions > 0" in content
        )
        assert not has_manual_guard, (
            "❌ int_marketing_campaigns.sql still contains the manual CASE WHEN guard for CTR\n"
            "   Remove the old guard and replace with:\n"
            "   {{ dbt_utils.safe_divide('ads_clicks * 1.0', 'ads_impressions') }} as click_through_rate"
        )

    def test_manual_guard_removed_cpc(self, int_campaigns_file):
        """int_marketing_campaigns.sql should not still have the manual CPC guard."""
        if not int_campaigns_file.exists():
            pytest.skip("int_marketing_campaigns.sql doesn't exist yet")
        content = int_campaigns_file.read_text().lower()
        # The old manual guard pattern checked ads_clicks > 0
        has_manual_guard = (
            "case when ads_clicks" in content or
            "case when ads_clicks > 0" in content
        )
        assert not has_manual_guard, (
            "❌ int_marketing_campaigns.sql still contains the manual CASE WHEN guard for CPC\n"
            "   Remove the old guard and replace with:\n"
            "   {{ dbt_utils.safe_divide('ads_cost', 'ads_clicks') }} as cost_per_click"
        )
