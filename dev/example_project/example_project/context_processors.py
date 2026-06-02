class ProcessorCallCounter:
    """Counts how many times `example_processor` has been invoked.

    Used by tests to verify that context processors fire only once per
    request even when many isolated cotton components are rendered
    (regression guard for issue #269).
    """
    count = 0


def example_processor(request):
    ProcessorCallCounter.count += 1
    return {"from_context_processor": "logo.png"}
