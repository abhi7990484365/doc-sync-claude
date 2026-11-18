from doc_sync.markdown import (
    Heading,
    atx_heading,
    fence_flags,
    find_headings,
    setext_level,
)


def test_atx_levels_and_text() -> None:
    assert atx_heading("# Title") == (1, "Title")
    assert atx_heading("   ###### Deep") == (6, "Deep")


def test_atx_rejects_non_headings() -> None:
    assert atx_heading("#Title") is None
    assert atx_heading("####### seven") is None
    assert atx_heading("    # indented code") is None
    assert atx_heading("text") is None


def test_atx_closing_hash_run_removed() -> None:
    assert atx_heading("## Title ##") == (2, "Title")
    assert atx_heading("# Title #   ") == (1, "Title")
    assert atx_heading("# C#") == (1, "C#")
    assert atx_heading("#") == (1, "")
    assert atx_heading("# #") == (1, "")


def test_setext_level() -> None:
    assert setext_level("===") == 1
    assert setext_level("  ---  ") == 2
    assert setext_level("text") is None
    assert setext_level("") is None
    assert setext_level("=-=") is None


def test_fence_flags_backticks() -> None:
    flags, open_marker = fence_flags(["a", "```", "# x", "```", "b"])
    assert flags == [False, True, True, True, False]
    assert open_marker is None


def test_fence_flags_tildes() -> None:
    flags, open_marker = fence_flags(["~~~py", "# x", "~~~", "# y"])
    assert flags == [True, True, True, False]
    assert open_marker is None


def test_fence_needs_same_char_and_enough_length() -> None:
    lines = ["````", "```", "~~~~", "````  ", "after"]
    flags, open_marker = fence_flags(lines)
    assert flags == [True, True, True, True, False]
    assert open_marker is None


def test_fence_closing_line_with_text_does_not_close() -> None:
    flags, open_marker = fence_flags(["```", "``` text", "x"])
    assert flags == [True, True, True]
    assert open_marker == "```"


def test_unclosed_fence_marker_returned() -> None:
    flags, open_marker = fence_flags(["a", "~~~~", "b"])
    assert flags == [False, True, True]
    assert open_marker == "~~~~"


def test_empty_input() -> None:
    assert fence_flags([]) == ([], None)
    assert find_headings([]) == []


def test_find_atx_headings() -> None:
    assert find_headings(["# A", "", "## B ##"]) == [
        Heading(0, 0, 1, "A"),
        Heading(2, 2, 2, "B"),
    ]


def test_headings_inside_fences_ignored() -> None:
    lines = ["```", "# no", "```", "~~~", "Title", "===", "~~~", "# yes"]
    assert find_headings(lines) == [Heading(7, 7, 1, "yes")]


def test_headings_in_unclosed_fence_ignored() -> None:
    assert find_headings(["# a", "```", "# b"]) == [Heading(0, 0, 1, "a")]


def test_setext_headings() -> None:
    lines = ["Title", "=====", "", "Sub", "---"]
    assert find_headings(lines) == [
        Heading(0, 1, 1, "Title"),
        Heading(3, 4, 2, "Sub"),
    ]


def test_setext_multi_line_text_joined() -> None:
    assert find_headings(["one", "two", "==="]) == [Heading(0, 2, 1, "one two")]


def test_thematic_break_is_not_heading() -> None:
    assert find_headings(["---", "", "text", "", "---"]) == []


def test_heading_followed_directly_by_text() -> None:
    lines = ["# Title", "text line", "---"]
    assert find_headings(lines) == [
        Heading(0, 0, 1, "Title"),
        Heading(1, 2, 2, "text line"),
    ]


def test_setext_not_taken_from_heading_line() -> None:
    assert find_headings(["# A", "---"]) == [Heading(0, 0, 1, "A")]
