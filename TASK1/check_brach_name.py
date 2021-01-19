import gitlab
import re, os
from TASK1.email_sender import send_email
from TASK1.helper import get_in_redis, sent_in_redis


def check_branch_name():
    current_page=1
    projects=gl.projects.list(as_list=False)
    total_pages=projects.total_pages
    while (current_page <= total_pages):
        projects=gl.projects.list(as_list=False, per_page=100, page=current_page)

        for project in projects:
            branches=project.branches.list()
            branch_list=[b.name for b in branches]

            for element in branch_list:
                invalid_branch_name = re.match("^(?!^(master|develop|feature|bugfix)/task-\d+)", element)
                if invalid_branch_name is not None:
                    try:
                        check_redis=get_in_redis(invalid_branch_name.string, 0)
                        if check_redis is None:
                            author=project.commits.list(ref_name=invalid_branch_name.string)
                            # print(author[0].author_email, author[0].author_name, author[0].title, author[0].created_at, author[0].id, project.name, invalid_branch_name.string )
                            subject=rf"Renaming or remove branch: {invalid_branch_name.string} in project: {project.name}"
                            send_email(author[0].author_email, subject, project.name, author[0].author_name,
                                       author[0].created_at, author[0].title, author[0].id)
                            sent_in_redis(invalid_branch_name.string,
                                          rf"sent email notification to {author[0].author_email}", 0)
                    except Exception as e:
                        print(e)
                current_page+=1



gl=gitlab.Gitlab(os.getenv("GITLAB_SCHEME") + os.getenv("GITLAB_URL"), os.getenv("ACCESS_TOKEN"))
gl.auth()

check_branch_name()
