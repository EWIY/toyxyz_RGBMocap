"""Update a clean branch without destroying local work or skipping dependency repair."""
import os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from session_lock import app_lock

def git(*args):
    return subprocess.run(['git','-C',str(ROOT),*args],capture_output=True,text=True,encoding='utf8',errors='replace',check=True).stdout.strip()

def main():
    with app_lock(ROOT):
        if git('status','--porcelain','--untracked-files=no'):raise RuntimeError('Tracked source files have local changes. Commit or back up changes before updating.')
        branch=git('branch','--show-current')
        if not branch:raise RuntimeError('Switch to a named branch before updating; detached HEAD is not supported.')
        try:tracking=git('rev-parse','--abbrev-ref','--symbolic-full-name','@{upstream}')
        except subprocess.CalledProcessError:raise RuntimeError('This branch has no tracking remote. Configure it for your fork before updating.') from None
        if tracking.startswith('upstream/') and branch!='main':
            raise RuntimeError('The custom branch must track your fork, not upstream/main. Configure origin/custom before updating.')
        before=git('rev-parse','HEAD');pending=ROOT/'.setup/git-sync.pending'
        pending.parent.mkdir(parents=True,exist_ok=True)
        previous_pending=pending.read_bytes() if pending.exists() else None
        pending.write_text('Update requires installation and validation.\n',encoding='utf8')
        try:
            print('Updating '+branch+' from '+tracking+'...',flush=True)
            subprocess.run(['git','-C',str(ROOT),'pull','--ff-only'],check=True)
        except BaseException:
            if git('rev-parse','HEAD')==before:
                if previous_pending is None:pending.unlink(missing_ok=True)
                else:pending.write_bytes(previous_pending)
            raise
    command=[str(Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe'),'-NoProfile','-ExecutionPolicy','Bypass','-File',str(ROOT/'tools/git_bootstrap.ps1'),*sys.argv[1:]]
    print('Checking the updated runtime configuration...',flush=True)
    subprocess.run(command,check=True,cwd=ROOT)

if __name__=='__main__':
    try:main()
    except Exception as exc:
        print('Update failed:',exc,file=sys.stderr);sys.exit(1)
