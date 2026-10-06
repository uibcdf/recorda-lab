"""Adapt a trial-owned receipt index to Recorda's explicit local byte checker."""

import recorda


def local_files(root, entries):
    locations = {}
    for entry in entries:
        value = entry["reference"]
        reference = recorda.Reference(
            **{key: value.get(key) for key in ("owner", "identifier", "revision", "digest")}
        )
        if reference in locations and locations[reference] != entry["path"]:
            raise ValueError("duplicate native reference")
        locations[reference] = entry["path"]
    resolver = recorda.LocalFileResolver(root, locations, digest_algorithm="sha256")
    for reference in resolver.references:
        checked = recorda.check_reference(reference, resolver=resolver)
        if checked["status"] in {"missing", "outside_root", "not_a_file"}:
            raise ValueError("native artifact missing or outside the trial")
        if checked["status"] != "matched":
            raise ValueError("native artifact no longer matches its receipt")
    return resolver
