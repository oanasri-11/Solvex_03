"""Follow-up service (alias for follow_up_action_service)."""

from app.services.follow_up_action_service import (
    create_follow_up_action,
    get_follow_up_action_by_id,
    get_all_follow_up_actions,
    update_follow_up_action,
    delete_follow_up_action,
)

# Friendly aliases matching prompt conventions
create_follow_up = create_follow_up_action
get_follow_up = get_follow_up_action_by_id
list_follow_ups = get_all_follow_up_actions
update_follow_up = update_follow_up_action
delete_follow_up = delete_follow_up_action

__all__ = [
    "create_follow_up_action",
    "get_follow_up_action_by_id",
    "get_all_follow_up_actions",
    "update_follow_up_action",
    "delete_follow_up_action",
    "create_follow_up",
    "get_follow_up",
    "list_follow_ups",
    "update_follow_up",
    "delete_follow_up",
]

