"""Opt-in experimental consumers; the underlying dummy library stays independent."""

import hashlib
import json
import os

import recorda

from recorda_lab import Result, summarize


@recorda.record("lab.summarize_samples", profile="scientific_analysis")
def summarize_samples(samples):
    return summarize(samples)


@recorda.record("lab.sample_count", profile="inspection")
def sample_count(samples):
    return len(samples)


@recorda.record("lab.analyze", profile="scientific_workflow")
def analyze(samples):
    return summarize_samples(samples)


@recorda.record("lab.interrupt", profile="scientific_analysis")
def interrupt():
    os._exit(23)


@recorda.record("lab.echo")
def echo(value, api_key=None):
    return value


def samples_reference(samples):
    digest = hashlib.sha256(json.dumps(samples).encode()).hexdigest()
    return recorda.Reference(owner="recorda-lab", identifier=f"sha256:{digest}", digest=digest)


def result_reference(result):
    return recorda.Reference(owner="recorda-lab", identifier=result.identifier)


REFERENCE_ADAPTERS = {list: samples_reference, Result: result_reference}
