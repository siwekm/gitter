## Gitter
A Python app to monitor activity on GitHub repositories using the GitHub Events API.  
<br>

#### GitHub Authentication
Set `GITHUB_TOKEN` environment variable to avoid 60 requests/hour GitHub limit.
<br><br>

#### Install:
Requires `Python >= 3.11`<br><br>
To install, run:
`poetry install`
<br><br>

#### Run:
Edit `config_repos.json` with desired repos in the format `user/repo_name`

`poetry run python main.py`
<br><br>

#### Access:
`http://localhost:8000/stats`
<br><br>
The app has a single endpoint `/stats`, which provides the average time between events for the configured repositories.
Time values are in seconds.
<br><br>

Response will look something like this:
```json
{
    "ohmyzsh/ohmyzsh": {
        "WatchEvent": 2240.7356828193833,
        "IssueCommentEvent": 40134.916666666664,
        "ForkEvent": 27098.5625,
        "PushEvent": 82223.0,
        "PullRequestEvent": 83459.4,
        "PullRequestReviewEvent": 82208.0,
        "DeleteEvent": 0.0,
        "CreateEvent": 0.0,
        "IssuesEvent": 75858.0,
        "GollumEvent": 0.0
    },
    "tensorflow/tensorflow": {
        "PushEvent": 313.73553719008265,
        "PullRequestEvent": 632.5833333333334,
        "DeleteEvent": 1465.9565217391305,
        "IssueCommentEvent": 1487.6538461538462,
        "CreateEvent": 1388.962962962963,
        "WatchEvent": 2217.4,
        "IssuesEvent": 5046.0,
        "ForkEvent": 13639.0
    }
}
```
