"""Review service (alias for case_review_service)."""

from app.services.case_review_service import (
    create_case_review,
    get_case_review_by_id,
    get_all_case_reviews,
    update_case_review,
)

# Friendly aliases matching prompt conventions
create_review = create_case_review
get_review = get_case_review_by_id
list_reviews = get_all_case_reviews
update_review = update_case_review

__all__ = [
    "create_case_review",
    "get_case_review_by_id",
    "get_all_case_reviews",
    "update_case_review",
    "create_review",
    "get_review",
    "list_reviews",
    "update_review",
]

