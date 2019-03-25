from typing import Optional, Tuple

import replies
import settings


def clamp(t: int, min_value: int, max_value: int) -> int:
    return max(min(t, max_value), min_value)


def merge_message(additions: int, deletions: int, additions_left: int, deletions_left: int) -> Tuple[str, bool]:
    """
    :return: Tuple containing message for the PR, and if can merge
    """
    can_add = additions_left - additions >= 0
    can_delete = deletions_left - deletions >= 0

    message: str
    can_merge: bool = False

    if can_add and can_delete:
        message = replies.merge_success
        can_merge = True
    elif can_add and not can_delete:
        message = replies.delete_limit_exceeded
    elif not can_add and can_delete:
        message = replies.add_limit_exceeded
    else:
        message = replies.both_limits_exceeded

    if can_merge:
        additions_left -= additions
        deletions_left -= deletions

    message += "\n" + replies.lines_left(additions_left, deletions_left)

    return message, can_merge


def updated_lines(additions_left: int, deletions_left: int, last_updated: float) -> Tuple[int, int]:
    """
    Calculates the number of lines that a user would be allowed given that their last update was `last_updated` seconds ago.

    :return: Tuple of the new number of lines allowed for additions and deletions
    """
    updates_last_commit: int = last_updated // settings.update_seconds
    new_additions: int = clamp(settings.additions_per_update * updates_last_commit + additions_left,
                               0, settings.max_addition_lines)
    new_deletions: int = clamp(settings.deletions_per_update * updates_last_commit + deletions_left,
                               0, settings.max_deletion_lines)

    return new_additions, new_deletions


def update_users_table(connection, user_id: int, additions: int, deletions: int, last_updated: Optional[int] = None) -> None:
    """
    Updates the users table in the database using `connection`.
    """
    with connection.cursor() as cur:
        if last_updated is not None:
            cur.execute("UPDATE users SET additions_left = %s, deletions_left = %s, last_commit = %s WHERE user_id = %s",
                        (additions, deletions, last_updated, user_id))
        else:
            cur.execute("UPDATE users SET additions_left = %s, deletions_left = %s WHERE user_id = %s",
                        (additions, deletions, user_id))
        connection.commit()


def most_recent_update(t: int) -> int:
    """
    Calculates the last time there would've been a line allowance update for `t`.

    :return: Last time there would've been an update.
    """
    return t // settings.update_seconds * settings.update_seconds