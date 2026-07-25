class BountyClaimer:
    def __init__(self, github_username, repo_name, issue_number):
        self.github_username = github_username
        self.repo_name = repo_name
        self.issue_number = issue_number

    def star_repos(self):
        print(f"Starring https://github.com/mergeos-bounties/HIRI and https://github.com/mergeos-bounties/mergeos")

    def comment_on_issue(self):
        print(f"Commenting 'I claim this bounty' on issue {self.issue_number}")

    def create_mergeos_claim(self):
        print(f"Creating MergeOS claim with issue link {self.issue_number}")

    def create_pull_request(self):
        print(f"Creating pull request to HIRI with Fixes #{self.issue_number}")


def main():
    github_username = "your_github_username"
    repo_name = "HIRI"
    issue_number = 200

    claimer = BountyClaimer(github_username, repo_name, issue_number)
    claimer.star_repos()
    claimer.comment_on_issue()
    claimer.create_mergeos_claim()
    claimer.create_pull_request()


if __name__ == "__main__":
    main()