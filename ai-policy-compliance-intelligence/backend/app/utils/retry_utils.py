from tenacity import retry, stop_after_attempt, wait_exponential


def transient_retry():
    return retry(wait=wait_exponential(multiplier=0.5, min=0.5, max=4), stop=stop_after_attempt(3), reraise=True)
