from python_experiments.utils import merge_dicts


def test_merge_dicts_basic() -> None:
    """Test basic dictionary merging functionality."""
    # Test simple dict merge
    into_dict = {"a": 1, "b": 2}
    from_dict = {"c": 3, "d": 4}

    merge_dicts(from_this=from_dict, into_this=into_dict)

    assert into_dict == {"a": 1, "b": 2, "c": 3, "d": 4}


def test_merge_dicts_overwrite() -> None:
    """Test that merge_dicts overwrites existing keys."""
    into_dict = {"a": 1, "b": 2}
    from_dict = {"b": 20, "c": 3}

    merge_dicts(from_this=from_dict, into_this=into_dict)

    assert into_dict == {"a": 1, "b": 20, "c": 3}


def test_merge_dicts_nested() -> None:
    """Test recursive merging of nested dictionaries."""
    into_dict = {"a": 1, "nested": {"x": 10, "y": 20}}
    from_dict = {"b": 2, "nested": {"y": 200, "z": 30}}

    merge_dicts(from_this=from_dict, into_this=into_dict)

    assert into_dict == {"a": 1, "b": 2, "nested": {"x": 10, "y": 200, "z": 30}}


def test_merge_dicts_complex_nested() -> None:
    """Test complex nested dictionary merging."""
    into_dict = {"level1": {"level2": {"a": 1, "b": 2}, "c": 3}, "d": 4}

    from_dict = {"level1": {"level2": {"b": 20, "e": 5}, "f": 6}, "g": 7}

    merge_dicts(from_this=from_dict, into_this=into_dict)

    assert into_dict == {"level1": {"level2": {"a": 1, "b": 20, "e": 5}, "c": 3, "f": 6}, "d": 4, "g": 7}


def test_merge_dicts_empty() -> None:
    """Test merging with empty dictionaries."""
    into_dict = {"a": 1, "b": 2}
    from_dict: dict[str, int] = {}

    merge_dicts(from_this=from_dict, into_this=into_dict)

    assert into_dict == {"a": 1, "b": 2}


def test_merge_dicts_both_empty() -> None:
    """Test merging two empty dictionaries."""
    into_dict: dict[str, str] = {}
    from_dict: dict[str, str] = {}

    merge_dicts(from_this=from_dict, into_this=into_dict)

    assert into_dict == {}
