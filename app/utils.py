from difflib import SequenceMatcher


def highlight_partial_matches(string1: str, string2: str, start_marker="<mark>", end_marker="</mark>"):
    """
    Highlights partial matches of string2 within string1.
    """
    # Use SequenceMatcher to find matching blocks
    matcher = SequenceMatcher(None, string1.lower(), string2.lower())
    highlighted = ""
    last_end = 0

    for match in matcher.get_matching_blocks():
        # Extract matching section's start and end
        start, end = match.a, match.a + match.size
        # Add non-matching text before the match
        highlighted += string1[last_end:start]
        # Add the matching text with markers
        highlighted += f"{start_marker}{string1[start:end]}{end_marker}"
        # Update last_end to the end of the current match
        last_end = end

    # Append any remaining non-matching text
    highlighted += string1[last_end:]
    return highlighted
