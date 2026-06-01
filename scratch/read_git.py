import subprocess
import os

repo_dir = r"c:\My Study\NMCNPM\Code\branch2\Mall_Management_Project"
file_path = "frontend/src/pages/premises/PremiseListPage.jsx"

# Run git show
result = subprocess.run(
    ["git", "show", f"9b777cbf:{file_path}"],
    cwd=repo_dir,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=False
)

if result.returncode == 0:
    content = result.stdout.decode('utf-8', errors='replace')
    out_path = os.path.join(repo_dir, "frontend", "src", "pages", "premises", "PremiseListPage.jsx.utf8")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("SUCCESS")
else:
    print("ERROR:", result.stderr.decode('utf-8'))
