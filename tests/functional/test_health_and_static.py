"""FT-STATIC-xx — unauthenticated health check and static asset serving.

See tests/functional/TEST_PLAN.md for the full test case list with steps.
"""


def test_ft_static_01_health_check_reports_ok(api):
    """FT-STATIC-01: /health responds without needing authentication."""
    response = api.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ft_static_02_root_page_is_served(api):
    """FT-STATIC-02: the main UI page loads."""
    response = api.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_ft_static_03_login_page_is_served(api):
    """FT-STATIC-03: the login UI page loads."""
    response = api.get("/login")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_ft_static_04_static_css_asset_is_served(api):
    """FT-STATIC-04: a static asset under /static is served with the right type."""
    response = api.get("/static/css/theme.css")

    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]
