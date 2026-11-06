"""Fork updates keep upstream's pending-marker and fast-forward protections."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools import git_update as update


class UpdateTests(unittest.TestCase):
    def run_fixture(self, branch='custom', tracking='origin/custom', dirty='', fail_pull=False, pending=None):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            marker=root/'.setup/git-sync.pending'
            if pending is not None:
                marker.parent.mkdir(parents=True)
                marker.write_bytes(pending)
            def git(*args):
                if args[0]=='status':return dirty
                if args[0]=='branch':return branch
                if args==('rev-parse','--abbrev-ref','--symbolic-full-name','@{upstream}'):
                    if tracking is None:raise subprocess.CalledProcessError(1,['git'])
                    return tracking
                return 'unchanged-head'
            calls=[]
            def run(command,**kwargs):
                calls.append(command)
                if fail_pull and 'pull' in command:raise subprocess.CalledProcessError(1,command)
            error=None
            with patch.object(update,'ROOT',root),patch.object(update,'git',side_effect=git),patch.object(update.subprocess,'run',side_effect=run),patch.object(sys,'argv',['git_update.py','--verify-all']):
                try:update.main()
                except Exception as exc:error=exc
            return error,calls,marker.read_bytes() if marker.exists() else None

    def test_custom_branch_updates_its_own_remote_and_forwards_verify_all(self):
        error,calls,marker=self.run_fixture()
        self.assertIsNone(error)
        self.assertEqual(calls[0][-2:],['pull','--ff-only'])
        self.assertIn('--verify-all',calls[1])
        self.assertIsNotNone(marker) # Cleared by actual successful bootstrap, not the Git pull.

    def test_tracked_edits_detached_and_wrong_remote_are_rejected_before_install(self):
        for options in [dict(dirty=' M app.py'),dict(branch=''),dict(tracking=None),dict(tracking='upstream/main')]:
            with self.subTest(options=options):
                error,calls,marker=self.run_fixture(**options)
                self.assertIsInstance(error,RuntimeError)
                self.assertFalse(calls)
                self.assertIsNone(marker)

    def test_failed_pull_preserves_previous_pending_marker(self):
        original=b'previous incomplete install\n'
        error,calls,marker=self.run_fixture(fail_pull=True,pending=original)
        self.assertIsInstance(error,subprocess.CalledProcessError)
        self.assertEqual(marker,original)
        self.assertEqual(len(calls),1)

    def test_failed_pull_does_not_create_false_new_pending_state(self):
        error,calls,marker=self.run_fixture(fail_pull=True)
        self.assertIsInstance(error,subprocess.CalledProcessError)
        self.assertIsNone(marker)


if __name__ == '__main__':
    unittest.main()
