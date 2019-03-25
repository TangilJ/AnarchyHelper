import settings

add_limit_exceeded: str = f"This pull request cannot be merged as you have exceeded your limit of " \
    f"{settings.max_addition_lines} lines of additions."
delete_limit_exceeded: str = f"This pull request cannot be merged as you have exceeded your limit of " \
    f"{settings.max_deletion_lines} lines of deletions."
both_limits_exceeded: str = f"This pull request cannot be merged as you have exceeded your " \
    f"limits of {settings.max_addition_lines} lines of additions and {settings.max_deletion_lines} lines of deletions."
merge_success: str = "This pull request has been successfully merged."
non_bot_file_changed: str = "This pull request has not been merged as you have edited a file not in the `anarchy` folder."


def lines_left(additions_left: int, deletions_left: int) -> str:
    return f"You currently have {additions_left} addition(s) left and {deletions_left} deletion(s) left."
