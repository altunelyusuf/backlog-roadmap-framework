#!/usr/bin/env python3
"""backlog_sparql_memo v1.0.0 -- parse each SPARQL query text once per process, not once per focus node (G99, cold-run analysis 2026-10-08).

MEASURED. pyshacl runs every SPARQL constraint once per focus node, and rdflib parses and translates the query text again on every call (about 20 ms each). On one
validation of the live register (355 shapes, 783 query executions): 21.6 s in total, 16.1 s of it in rdflib's parser and 3.0 s in its translator; evaluating the queries
took about 0.2 s. With the parsed query kept and reused, the same validation takes 3.8 s. The negative fixture went from 333 s to 22 s. The results were compared
result for result (focus node, constraint component, message, severity, value) on three fixtures and are identical.

WHAT THIS DOES. It wraps rdflib.Graph.query: a query given as TEXT is prepared once (rdflib.plugins.sparql.prepareQuery, with the same prefixes) and the prepared query
is run with the same initial bindings every time. A parsed query holds no data and no bindings, so nothing leaks between focus nodes or graphs; the probe shows it.
It changes no verdict and no result. BACKLOG_SPARQL_MEMO=0 turns it off (that is how the probe proves equality).
Importers: call install() once; it is idempotent. The tools that import it name this file in their cache keys (OE rule R9).
"""
import os

_state = {"on": False, "orig": None, "cache": {}, "prepared": 0, "calls": 0}


def install():
    if os.environ.get("BACKLOG_SPARQL_MEMO") == "0":
        return False
    if _state["on"]:
        return True
    import rdflib
    from rdflib.plugins.sparql import prepareQuery
    orig = rdflib.Graph.query
    cache = _state["cache"]

    def query(self, query_object, processor="sparql", result="sparql", initNs=None, initBindings=None, use_store_provided=True, **kwargs):
        if isinstance(query_object, str) and processor == "sparql":
            _state["calls"] += 1
            key = (query_object, tuple(sorted((str(a), str(b)) for a, b in initNs.items())) if initNs else None)
            prepared = cache.get(key)
            if prepared is None:
                prepared = cache[key] = prepareQuery(query_object, initNs=initNs)
                _state["prepared"] += 1
            query_object, initNs = prepared, None
        return orig(self, query_object, processor, result, initNs, initBindings, use_store_provided, **kwargs)

    _state["orig"] = orig
    rdflib.Graph.query = query
    _state["on"] = True
    return True


def uninstall():
    if _state["on"]:
        import rdflib
        rdflib.Graph.query = _state["orig"]
        _state.update(on=False, orig=None)
        _state["cache"].clear()


def stats():
    return {"queries_run": _state["calls"], "texts_prepared": _state["prepared"]}
