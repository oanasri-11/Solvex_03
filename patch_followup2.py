# Patch follow_up_action_service.py - rename delete_follow_up_action to complete_follow_up_action
p = "Backend/app/services/follow_up_action_service.py"
s = open(p, encoding="utf-8").read()

old_func = '''def delete_follow_up_action(db: Session, action_id: int) -> Optional[FollowUpAction]:
    """Soft delete a follow-up action only if it is not completed.
    
    The model carries no is_active field, so the soft delete is expressed by moving
    the action to a terminal (completed) state with a completed_at timestamp when it
    is not already completed. Completed actions cannot be removed.
    """
    try:
        db_action = get_follow_up_action_by_id(db, action_id)
        if not db_action:
            return None
        if db_action.status == "completed":  # type: ignore
            return None
        db_action.status = "completed"  # type: ignore
        db_action.completed_at = datetime.utcnow()  # type: ignore
        db.add(db_action)
        db.commit()
        db.refresh(db_action)
        return db_action
    except SQLAlchemyError:
        db.rollback()
        raise
'''

new_func = old_func.replace(
    "def delete_follow_up_action",
    "def complete_follow_up_action",
    1
)

if old_func in s:
    s = s.replace(old_func, new_func)
    print("Renamed in follow_up_action_service.py")
else:
    print("ERROR: old_func not found")
    # Show a snippet to debug
    idx = s.find("def delete_follow_up_action")
    if idx >= 0:
        print("Snippet:", repr(s[idx:idx+300]))

open(p, "w", encoding="utf-8").write(s)
