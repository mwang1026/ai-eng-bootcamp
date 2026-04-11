"""Shared test helpers — importable from any test module."""

from langchain_core.documents import Document


def make_long_opinion(
    paragraphs: int = 20, case_name: str = "Long v. Opinion"
) -> Document:
    """Create a realistic-length opinion with multiple paragraphs."""
    para = (
        "The Court finds that the petitioner's argument regarding the "
        "constitutional implications of the statute in question raises "
        "substantial concerns about due process and equal protection. "
        "We must therefore examine the legislative history and the "
        "framework established by prior precedent in this area of law."
    )
    return Document(
        page_content="\n\n".join([para] * paragraphs),
        metadata={"case_name": case_name, "date_filed": "2005-01-01"},
    )
