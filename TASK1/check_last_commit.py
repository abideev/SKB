import gitlab
import re, os
from TASK1.email_sender import send_email
from TASK1.helper import get_in_redis, sent_in_redis
from datetime import timedelta, datetime


def check_last_date_commit():
    current_page=1
    projects=gl.projects.list(as_list=False)
    total_pages=projects.total_pages
    while (current_page <= total_pages):
        projects=gl.projects.list(as_list=False, per_page=100, page=current_page)
        for project in projects:
            branches=project.branches.list()
            branch_list=[b.name for b in branches]

            for element in branch_list:
                if re.match("^(?!master|develop)", element) is not None:

                    all_commits=project.commits.list(ref_name=element)
                    commits_list=[b.committed_date for b in all_commits]

                    commit_date=datetime.strptime(commits_list[0], '%Y-%m-%dT%H:%M:%S.%fZ')
                    date_days=datetime.now() - timedelta(days=14)

                    if date_days > commit_date:
                        check_redis=get_in_redis(element, 1)

                        if check_redis is None:
                            subject=rf"Update or remove branch: {element} in project: {project.name}"
                            send_email(all_commits[0].author_email, subject, project.name, all_commits[0].author_name,
                                       all_commits[0].created_at, all_commits[0].title, all_commits[0].id)
                            sent_in_redis(element, rf"sent email notification to {all_commits[0].author_email}", 1)


gl=gitlab.Gitlab(os.getenv("GITLAB_SCHEME") + os.getenv("GITLAB_URL"), os.getenv("ACCESS_TOKEN"))
gl.auth()

check_last_date_commit()
