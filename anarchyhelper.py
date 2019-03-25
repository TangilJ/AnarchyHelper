from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.view import view_config, view_defaults
from pyramid.response import Response
from pyramid.request import Request
from github import Github
from github.Repository import Repository
from github.PullRequest import PullRequest
from github.IssueComment import IssueComment
import psycopg2

import os
import utils
import logging
from typing import Optional, Tuple, List

import settings
import replies
import time

ENDPOINT = "webhook"
PORT = int(os.environ["PORT"])
USERNAME = "AnarchyHelper"
PASSWORD = os.environ["GITHUB_PASSWORD"]
REPOSITORY = "TheBlocks/Anarchy"
DATABASE_URL = os.environ["DATABASE_URL"]
logging.basicConfig(level=logging.INFO, format="%(levelname)s|%(lineno)d|%(message)s")


@view_defaults(
    route_name=ENDPOINT, renderer="json", request_method="POST"
)
class Webhook:
    def __init__(self, request: Request):
        self.request: Request = request
        self.payload: dict = self.request.json

    @view_config(header="X-Github-Event:pull_request")
    def pull_request(self) -> Response:
        """
        Called when a pull request is opened/closed/updated.\n
        This method squash merges a PR if the user does not exceed their line limits.\n
        It comments on the PR if the user exceeds limits. The previous comment is edited if the user updates their PR.

        :return: 200 OK
        """
        if self.payload["action"] == "closed":
            return Response()

        pr: PullRequest = repo.get_pull(self.payload["pull_request"]["number"])
        changed_files: List[str] = [i.filename for i in pr.get_files()]

        if False in [i.startswith("anarchy") for i in changed_files]:
            pr.create_issue_comment(replies.non_bot_file_changed)
            return Response()

        # Determine if the PR can be merged, and the message in the reply comment
        user_id: int = self.payload["pull_request"]["user"]["id"]
        with connection.cursor() as cur:
            cur.execute("SELECT additions_left, deletions_left, last_commit FROM users WHERE user_id = %s", (user_id,))
            query_return: Optional[Tuple[int, int, int]] = cur.fetchone()
        if query_return is not None:
            additions_left, deletions_left, last_commit = query_return
        else:
            # Add user to users table since they don't exist in the table already
            additions_left, deletions_left, last_commit = settings.max_addition_lines, settings.max_deletion_lines, 0
            with connection.cursor() as cur:
                cur.execute("INSERT INTO users (user_id, additions_left, deletions_left, last_commit) VALUES (%s, %s, %s, %s)",
                            (user_id, additions_left, deletions_left, last_commit))
                connection.commit()

        # Get the new line allowances for the user
        updated_additions_left, updated_deletions_left = utils.updated_lines(additions_left, deletions_left,
                                                                             int(time.time()) - last_commit)
        if (additions_left != updated_additions_left) and (deletions_left != updated_deletions_left):
            most_recent_update: int = utils.most_recent_update(int(time.time()))
            utils.update_users_table(connection, user_id, updated_additions_left, updated_deletions_left, most_recent_update)

        additions, deletions = self.payload["pull_request"]["additions"], self.payload["pull_request"]["deletions"]
        message, can_merge = utils.merge_message(additions, deletions, updated_additions_left, updated_deletions_left)

        if can_merge:
            # Merge if allowed and update the table
            pr.merge(merge_method="squash")
            logging.info(f"Merged PR #{self.payload['number']} with ID {self.payload['pull_request']['id']}.")
            utils.update_users_table(connection, user_id, updated_additions_left - additions, updated_deletions_left - deletions)

        # Comment on the PR
        if self.payload["action"] == "opened":
            pr.create_issue_comment(message)
            logging.info(f"Created comment on PR #{self.payload['number']} "
                         f"with PR ID {self.payload['pull_request']['id']}.")

        elif self.payload["action"] == "synchronize":
            with connection.cursor() as cur:
                cur.execute("SELECT comment_id FROM bot_comments WHERE issue_id = %s",
                            (self.payload['number'],))
                prev_comment_id: int = cur.fetchone()[0]
                comment: IssueComment = pr.get_issue_comment(prev_comment_id)
                comment.edit(message)
                logging.info(f"Edited comment on PR #{self.payload['number']}. Edited comment ID: {prev_comment_id}")

        else:
            logging.error("X-Github-Event:pull_request 'action' was not: opened, closed, or synchronize."
                          f"Was: {self.payload['action']}")

        return Response()

    @view_config(header="X-Github-Event:issue_comment")
    def issue_comment(self) -> Response:
        """
        Called when a comment is created/deleted/edited in an issue.\n
        This method adds its own comment ID to the database to keep track of.
        This way its previous comments can be edited instead of creating new ones.

        :return: 200 OK
        """
        if self.payload["issue"]["user"]["login"] == "AnarchyHelper":
            with connection.cursor() as cur:
                cur.execute("INSERT INTO bot_comments (comment_id, issue_id) VALUES (%s, %s)"
                            "ON CONFLICT (comment_id) DO UPDATE SET comment_id = %s, issue_id = %s",
                            (self.payload["comment"]["id"], self.payload["issue"]["number"],
                             self.payload["comment"]["id"], self.payload["issue"]["number"]))
                connection.commit()

                logging.info(f"Updated bot_comments table with own comment ID ({self.payload['comment']['id']})"
                             f"and issue #{self.payload['issue']['number']}.")

        return Response()

    @view_config(header="X-Github-Event:ping")
    def ping(self) -> Response:
        """
        Called when the server is pinged.

        :return: 200 OK
        """
        logging.info(f"Pinged! Webhook created with id {self.payload['hook']['id']}.")
        return Response()


if __name__ == "__main__":
    gh: Github = Github(USERNAME, PASSWORD)
    repo: Repository = gh.get_repo(REPOSITORY)
    logging.info(f"Accessed account {USERNAME} and repository {REPOSITORY} successfully.")

    connection = psycopg2.connect(DATABASE_URL)
    config: Configurator = Configurator()

    config.add_route(ENDPOINT, "/{}".format(ENDPOINT))
    config.scan()

    app = config.make_wsgi_app()
    server = make_server("0.0.0.0", PORT, app)
    logging.info("Starting server.")
    server.serve_forever()
