# Recovery cases and filesystem boundaries

Status: second-level execution design. No real filesystem executor has been implemented. These cases define the next experiment's expected behavior.

## What can be promised

The system can avoid knowingly replaying an uncertain operation, retain evidence, and expose uncertainty. It cannot make arbitrary application effects and its own journal a single atomic transaction. Distinguish “the requested state is now observed” from “we proved this particular process caused it.”

For the first file-move experiment, limit support to regular files within a declared local filesystem, a known source identity, and a nonexistent destination. Exclude overwrites, cross-filesystem copies, network filesystems, directory trees, and symlink sources until their semantics are designed.

Linux rename interfaces document replacement behavior and `RENAME_NOREPLACE`; the latter depends on filesystem support. A preflight existence check followed by ordinary overwrite-capable rename is not sufficient to enforce no-overwrite under concurrent changes. [rename(2)](https://man7.org/linux/man-pages/man2/rename.2.html).

Directory-relative resolution with `openat2` offers constraints such as staying beneath a root and restricting symlink resolution. It is a candidate mechanism to investigate, not a complete substitute for checking the actual source/destination used by a later operation. [openat2(2)](https://man7.org/linux/man-pages/man2/openat2.2.html).

An unresolved production issue is concurrent source-name replacement: validating an object and later renaming its pathname leaves a race unless the supported environment supplies stronger control. Directory descriptors and no-overwrite flags do not by themselves prove that the source still denotes the selected object. A post-effect check may detect a wrong-object move too late. The sandbox experiment can use exclusively controlled fixture directories; production `file.move` must remain unavailable until the supported race/concurrency semantics are established. Do not advertise complete target safety based only on preflight checks.

Durability is distinct from a successful syscall. `fsync` documentation notes that syncing a file does not necessarily persist the containing directory entry; a directory sync is separately needed. The executor's journal/effect ordering must be tested for the chosen filesystem. [fsync(2)](https://man7.org/linux/man-pages/man2/fsync.2.html).

## Journal ordering proposal

1. Resolve scope and intended objects; record immutable operation arguments and preconditions.
2. Durably record `prepared`. No external effect is allowed before this record succeeds.
3. Recheck current grant, cancellation, and immediate object state.
4. Durably record `executing` before issuing the effect.
5. Issue the bounded operation and gather verification evidence.
6. Make required effect/directory durability checks, then durably record the result.
7. Acknowledge completion to the UI.

There is still a window after step 4 and before or after step 5 in which a restart cannot infer completion from the journal alone. `prepared` proves no effect was issued only if every execution path obeys this ordering. Tests must inject faults at each boundary, not merely call the happy path twice.

## Move recovery decision table

“Original object” means strong enough identity evidence under the experiment's declared assumptions; a matching filename or content hash alone is not sufficient. Persistent identity after deletion/inode reuse requires additional care before production.

| Observed source | Observed destination | Result and next step |
| --- | --- | --- |
| Original object | Absent | Goal not observed. Recheck current grant, cancellation, and preconditions before any new attempt |
| Absent | Original object | Goal observed. Record recovered completion with evidence; do not repeat |
| Different object | Original object | Goal observed with source path reuse. Preserve the replacement source; do not move it |
| Original object | Different object | Conflict. Do not overwrite; ask for a new destination or explicit new operation |
| Original object | Original object | Ambiguous/hard-link case. Stop and classify as unsupported or uncertain |
| Absent | Absent | Outcome unknown. Stop dependent actions and report missing evidence |
| Different object | Absent or different object | Outcome unknown. Do not act on the replacement source |
| Unreadable or unverifiable | Any | Outcome unknown or access revoked. Do not substitute a guessed result |

If cancellation or permission revocation occurred during execution, observation of an existing effect can still be recorded when read access permits. Neither event authorizes additional effects. The UI reports what happened before cancellation, not an imaginary rollback.

## Directory creation and provenance

After a crash, a directory existing at the requested path can establish that the requested state exists; it does not by itself establish which actor created it. A recovered create should therefore avoid claiming exclusive ownership or offering automatic deletion as undo without stronger evidence. Never remove a now-populated directory as a generic compensation.

## Compound request example

“Create Garden and move this note there” becomes two steps. If create succeeds and move fails, report “Garden exists; the note was not moved” with the failure reason. Do not delete Garden to hide the partial result. A later retry can reuse the existing destination after checking type, scope, and identity.

The first contract fixture checker intentionally does not implement references to outputs of previous steps. Before implementing compound workflows, define result references and dependencies explicitly; do not ask the model to guess generated paths or IDs.

## Concrete fault-injection exercise

Create disposable fixtures in a temporary directory. Use a fake journal or controlled flush boundaries to simulate failure at each numbered point. Recreate the coordinator from the recorded state and fresh observations, then assert the decision table. Repeat with source replacement, destination collision, revocation, cancellation, and disk/journal failure.

Tests must check both contents and untouched neighboring files. Simulated process crashes do not establish power-loss durability; that needs a separate filesystem/VM experiment. Never point this exercise at the user's working files.
