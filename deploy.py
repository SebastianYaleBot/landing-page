"""Deploy site-redesign to GitHub Pages (SebastianYaleBot/landing-page) using the GitHub CLI."""
import os
import shutil
import subprocess
import tempfile
import sys
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
OWNER = "SebastianYaleBot"
REPO = "landing-page"
BRANCH = "main"

print("=== Deploying site redesign via GitHub CLI ===")

# List of allowed text files to deploy
text_files = [
    "index.html",
    "styles.css",
    "about.html",
    "beautiful-things.html",
    "latent-garden.html",
    "reflections.html",
    "day-2026-03-01.html",
    "log.html",
    "team.html",
    "mission-control-x7k2.html",
    "projects-x9m4.html",
    "script.js",
]

with tempfile.TemporaryDirectory() as tmpdir:
    repo_dir = os.path.join(tmpdir, REPO)
    
    print(f"  Cloning {OWNER}/{REPO} into temporary directory...")
    # Use gh to clone, ensuring it uses the configured authentication natively
    res = subprocess.run(
        ["gh", "repo", "clone", f"{OWNER}/{REPO}", repo_dir, "--", "--branch", BRANCH, "--depth", "1"],
        capture_output=True, text=True
    )
    if res.returncode != 0:
        print("  FAILED to clone repository:")
        print(res.stderr)
        sys.exit(1)

    print("  Copying text files...")
    for fname in text_files:
        src = os.path.join(BASE, fname)
        dst = os.path.join(repo_dir, fname)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print("    Copied: " + fname)
        else:
            print("    SKIP (not found): " + fname)

    print("  Copying images...")
    img_dir_src = os.path.join(BASE, "images")
    img_dir_dst = os.path.join(repo_dir, "images")
    if os.path.isdir(img_dir_src):
        os.makedirs(img_dir_dst, exist_ok=True)
        for fname in sorted(os.listdir(img_dir_src)):
            if fname.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
                src = os.path.join(img_dir_src, fname)
                dst = os.path.join(img_dir_dst, fname)
                shutil.copy2(src, dst)
                print("    Copied: images/" + fname)

    print("  Committing and pushing changes...")
    # Configure git so commits have an author
    subprocess.run(["git", "config", "user.name", "SabastianYaleBot"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.email", "sebastianyalebot@gmail.com"], cwd=repo_dir, check=True)
    
    # Add files
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True)
    
    # Check if there are any changes
    status = subprocess.run(["git", "status", "--porcelain"], cwd=repo_dir, capture_output=True, text=True)
    if not status.stdout.strip():
        print("  No changes to deploy.")
    else:
        # Commit
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        commit_msg = f"Deploy site updates via CLI ({timestamp})"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=repo_dir, check=True)
        
        # Push
        print("  Pushing to GitHub...")
        res = subprocess.run(["git", "push", "origin", BRANCH], cwd=repo_dir, capture_output=True, text=True)
        if res.returncode == 0:
            print("  SUCCESS: Pushed to GitHub.")
        else:
            print("  FAILED to push:")
            print(res.stderr)
            sys.exit(1)

print("=== Deploy complete ===")
