"""Filter-contract gates — parse_filter_state is the single JSON-store reader every
view depends on; a regression here mis-scopes every chart at once."""

import json

from app import panel_data
from app.filters import DEFAULT_FILTER_STATE, parse_filter_state


def test_parses_defaults_when_json_is_none():
    scope, window, line, retailer = parse_filter_state(None)
    assert scope == panel_data.SCOPE_BRAND
    assert window == panel_data.DEFAULT_REPEAT_WINDOW_WEEKS
    assert line == "__all__" and retailer == "__all__"


def test_parses_defaults_when_json_is_empty():
    assert parse_filter_state("{}") == (
        panel_data.SCOPE_BRAND, panel_data.DEFAULT_REPEAT_WINDOW_WEEKS, "__all__", "__all__")


def test_falls_back_per_field_when_partial():
    scope, window, line, retailer = parse_filter_state(json.dumps({"scope": "CHP-SB-010"}))
    assert scope == "CHP-SB-010"
    assert window == panel_data.DEFAULT_REPEAT_WINDOW_WEEKS  # missing → default
    assert line == "__all__" and retailer == "__all__"


def test_coerces_string_window_to_int():
    window = parse_filter_state(json.dumps({"repeat_window": "26"}))[1]
    assert window == 26 and isinstance(window, int)


def test_default_filter_state_roundtrips():
    assert parse_filter_state(json.dumps(DEFAULT_FILTER_STATE)) == (
        panel_data.SCOPE_BRAND, panel_data.DEFAULT_REPEAT_WINDOW_WEEKS, "__all__", "__all__")


def test_scope_sku_maps_brand_to_none_and_passes_sku():
    assert panel_data.scope_sku(panel_data.SCOPE_BRAND) is None
    assert panel_data.scope_sku("CHP-SB-010") == "CHP-SB-010"
    assert panel_data.scope_sku(None) is None
