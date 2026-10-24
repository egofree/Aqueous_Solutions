# Security policy

## Scope

Aqueous Solutions is a design repository: a process flow graph, a parametric
sizing pipeline, generated engineering documents, and CAD builders. It ships no
running service. Security reports that matter here are:

- a secret, credential, or personal data committed to the repository;
- code in the repository (the regeneration pipeline, the design tool API in
  `design_tool/`, CAD builders) that can be made to read or write outside the
  repository, execute untrusted input, or otherwise harm the machine that runs it;
- a dependency with a known vulnerability that the tooling pulls in.

A design that is unsafe to build (for example, a relief case or a material
selection that is wrong) is an engineering defect, not a security report. Open a
normal issue for it with the "Design defect" template, and say what is unsafe.
Every design here is a study and is not stamped by a licensed engineer.

## Reporting

Report privately. Do not open a public issue for a vulnerability or a leaked
secret.

- Preferred: GitHub private vulnerability reporting, on the repository's
  **Security** tab, **Report a vulnerability**.
- Alternative: contact the maintainer, @egofree, on GitHub and ask for a
  private channel.

Include what you found, where (file, commit, or endpoint), and how to reproduce
it. Do not paste a live secret into the report; give its location and type.

## Response

The maintainer aims to acknowledge a report within 7 days and to agree a fix
and disclosure date with the reporter. Committed secrets are revoked first, then
removed from the tree; removal from history is decided case by case.
