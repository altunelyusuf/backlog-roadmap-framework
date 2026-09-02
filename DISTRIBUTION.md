# About this copy

This is the **public distribution** of `backlog-roadmap-framework`, derived from a governed package
that lives in a private ontology-engineering ecosystem. It is complete as a framework: vocabulary,
constraints, rules, tooling, fixtures and the standard. Nothing that makes it work has been removed.

## What was removed, and why

| Removed | Reason |
|---|---|
| `05-lesson-deposits/`, `06-package-provenance/` | Correspondence with other sessions about *their* artifacts — governance records, not framework content |
| `backlog_alignment_productbacklog_v1_0_0.ttl` and its mapping document | An alignment to one adopting project's private deposit. Useless without that deposit |
| ORCP submission, registration-readiness, ceremony records | Process records naming other registrants and internal pack releases |
| `backlog_registration_readiness`, `backlog_package_check` | Tools that only do anything against the private pack |

The adopting project that the subject was generalised from is referred to throughout as **"an
adopting project"**. That the framework came from a real register is true and worth keeping; the
identification is not ours to publish.

## One thing to know when reading the changelog

The changelog is a **historical record** and has not been rewritten. Two of its entries discuss
`oe-prov:` attribution IRIs and say they were left untouched — in the governed package that is true;
in this copy those IRIs have been replaced with literal attribution, because they resolve to nothing
outside the ecosystem. The entry is not edited, because editing a record of a past release to match
a later artifact is exactly the failure this framework's own tooling exists to prevent. This note is
the correction.

## Regenerating this copy

It is derived by script, not by hand, so it can be re-derived and checked for drift. The script
(`make_public_distribution_v1_3_0.py`) lives with the **governed** package, not here — its
substitution patterns necessarily contain the very names it removes, so shipping it in the public
copy would reintroduce them. The final scan caught exactly that and the script was pulled.

Every removal and every substitution is declared in that script's header, and it is re-runnable
against the governed source at any time.

## Licence

CC BY 4.0. Copyright (c) 2025–2026 İstanbul Kültür Üniversitesi & Yusuf Altunel. Attribution is a
licence condition, which is why the author's name is present throughout and was not stripped.
