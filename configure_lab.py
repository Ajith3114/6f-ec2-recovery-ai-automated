import json
import os
import re
import subprocess
from pathlib import Path

repo = os.environ["LAB_REPO"]

details = json.loads(
    subprocess.check_output(
        ["gh", "api", f"repos/{repo}"],
        text=True,
    )
)

subject = (
    f"repo:{details['owner']['login']}@{details['owner']['id']}/"
    f"{details['name']}@{details['id']}:ref:refs/heads/main"
)

updated = 0

for item in Path(".").rglob("*.tf"):
    if ".terraform" in item.parts:
        continue

    content, count = re.subn(
        r'repo:[^"\r\n]+:ref:refs/heads/main',
        lambda match: subject,
        item.read_text(),
    )

    if count:
        item.write_text(content)
        updated += count

if updated < 2:
    raise SystemExit(
        "Expected two OIDC trust subjects. Check the project folder."
    )

names = {
    "infrastructure.yml": "Cloud Infra Pipeline (Mum)",
    "deploy-agent.yml": "Monitoring AI Agent (Hyd)",
    "recover-ec2.yml": "AI Infra Recovery",
}

for filename, display_name in names.items():
    workflow = Path(".github/workflows") / filename

    content, count = re.subn(
        r"^name:.*$",
        lambda match: f'name: "{display_name}"',
        workflow.read_text(),
        count=1,
        flags=re.MULTILINE,
    )

    if count != 1:
        raise SystemExit(f"Could not update workflow name: {filename}")

    workflow.write_text(content)
    print("Pipeline name:", display_name)

print("OIDC subject:", subject)
print("Configured trust subjects:", updated)
