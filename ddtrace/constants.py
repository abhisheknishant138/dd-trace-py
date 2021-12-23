import enum


FILTERS_KEY = "FILTERS"
SAMPLE_RATE_METRIC_KEY = "_sample_rate"
SAMPLING_PRIORITY_KEY = "_sampling_priority_v1"
ANALYTICS_SAMPLE_RATE_KEY = "_dd1.sr.eausr"
SAMPLING_AGENT_DECISION = "_dd.agent_psr"
SAMPLING_RULE_DECISION = "_dd.rule_psr"
SAMPLING_LIMIT_DECISION = "_dd.limit_psr"
ORIGIN_KEY = "_dd.origin"
HOSTNAME_KEY = "_dd.hostname"
ENV_KEY = "env"
VERSION_KEY = "version"
SERVICE_KEY = "service.name"
SERVICE_VERSION_KEY = "service.version"
SPAN_KIND = "span.kind"
SPAN_MEASURED_KEY = "_dd.measured"
KEEP_SPANS_RATE_KEY = "_dd.tracer_kr"

NUMERIC_TAGS = (ANALYTICS_SAMPLE_RATE_KEY,)

MANUAL_DROP_KEY = "manual.drop"
MANUAL_KEEP_KEY = "manual.keep"

# Horizontally propagated tags
UPSTREAM_SERVICES_KEY = "_dd.p.upstream_services"

LOG_SPAN_KEY = "__datadog_log_span"

ERROR_MSG = "error.msg"  # a string representing the error message
ERROR_TYPE = "error.type"  # a string representing the type of the error
ERROR_STACK = "error.stack"  # a human readable version of the stack.

PID = "system.pid"

# Use this to explicitly inform the backend that a trace should be rejected and not stored.
USER_REJECT = -1
# Used by the builtin sampler to inform the backend that a trace should be rejected and not stored.
AUTO_REJECT = 0
# Used by the builtin sampler to inform the backend that a trace should be kept and stored.
AUTO_KEEP = 1
# Use this to explicitly inform the backend that a trace should be kept and stored.
USER_KEEP = 2


class SamplingMechanism(enum.Enum):
    """The mechanism responsible for making a sampling decision."""

    DEFAULT = 0  # RateByServiceSampler used before receiving rates from the agent
    AGENT = 1  # RateByServiceSampler used rates from the agent
    REMOTE = 2  # Not currently used
    USER_RULE = 3  # Manual rule / rate provided in tracer configuration
    MANUAL = 4  # Manually set via `set_tag(MANUAL_DROP/KEEP_KEY)`
    APP_SEC = 5  # Not currently used
    USER_REMOTE = 6  # Not currently used
