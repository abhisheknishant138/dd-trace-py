import base64
import threading
from typing import Any
from typing import Optional
from typing import TYPE_CHECKING
from typing import Text

from .constants import ORIGIN_KEY
from .constants import SAMPLING_PRIORITY_KEY
from .constants import SamplingMechanism
from .constants import UPSTREAM_SERVICES_KEY
from .internal.compat import NumericType
from .internal.compat import ensure_binary
from .internal.compat import ensure_text
from .internal.logger import get_logger
from .internal.utils.deprecation import deprecated


if TYPE_CHECKING:
    from .span import Span
    from .span import _MetaDictType
    from .span import _MetricDictType

log = get_logger(__name__)


class Context(object):
    """Represents the state required to propagate a trace across execution
    boundaries.
    """

    __slots__ = [
        "trace_id",
        "span_id",
        "_lock",
        "_meta",
        "_metrics",
        "_last_upstream_service_entry",
    ]

    def __init__(
        self,
        trace_id=None,  # type: Optional[int]
        span_id=None,  # type: Optional[int]
        dd_origin=None,  # type: Optional[str]
        sampling_priority=None,  # type: Optional[float]
        meta=None,  # type: Optional[_MetaDictType]
        metrics=None,  # type: Optional[_MetricDictType]
        lock=None,  # type: Optional[threading.RLock]
        upstream_service_entry=None,  # type: Optional[str]
    ):
        self._meta = meta if meta is not None else {}  # type: _MetaDictType
        self._metrics = metrics if metrics is not None else {}  # type: _MetricDictType

        self._last_upstream_service_entry = upstream_service_entry

        self.trace_id = trace_id  # type: Optional[int]
        self.span_id = span_id  # type: Optional[int]

        if dd_origin is not None:
            self._meta[ORIGIN_KEY] = dd_origin
        if sampling_priority is not None:
            self._metrics[SAMPLING_PRIORITY_KEY] = sampling_priority

        if lock is not None:
            self._lock = lock
        else:
            # DEV: A `forksafe.RLock` is not necessary here since Contexts
            # are recreated by the tracer after fork
            # https://github.com/DataDog/dd-trace-py/blob/a1932e8ddb704d259ea8a3188d30bf542f59fd8d/ddtrace/tracer.py#L489-L508
            self._lock = threading.RLock()

    def _with_span(self, span):
        # type: (Span) -> Context
        """Return a shallow copy of the context with the given span."""
        return self.__class__(
            trace_id=span.trace_id,
            span_id=span.span_id,
            meta=self._meta,
            metrics=self._metrics,
            lock=self._lock,
            upstream_service_entry=self._last_upstream_service_entry,
        )

    def _update_tags(self, span):
        # type: (Span) -> None
        with self._lock:
            span.meta.update(self._meta)
            span.metrics.update(self._metrics)

    def _update_upstream_services(
        self,
        span,  # type: Span
        sampling_priority,  # type: int
        sampling_mechanism,  # type: SamplingMechanism
        sample_rate=None,  # type: Optional[float]
    ):
        # type: (...) -> None
        """
        Update the ``_dd.p.upstream_services`` tag associated with this context.

        Calling with the same values multiple times will not change anything.

        Calling multiple times with new values will replace the previous entry with the new one.
        (We will only have 1 entry in the tag for this context)
        """

        entry = "|".join(
            [
                # base64 encode binary representation of the service name
                # DEV: remove padding
                ensure_text(base64.b64encode(ensure_binary(span.service or "unnamed-python-service"))).strip("="),
                str(sampling_priority),
                str(sampling_mechanism.value),
                # Float string rounded to 4 decimal places if set, otherwise an empty string
                "{:0.4f}".format(sample_rate) if sample_rate is not None else "",
            ]
        )

        # If the sampling decision hasn't changed, do not add an entry
        # For example, if someone does `span.set_tag(MANUAL_KEEP_KEY)` multiple times in one trace
        if self._last_upstream_service_entry == entry:
            return

        # Fetch any existing value (extracted from propagation headers, or we have already set ourselves)
        existing = self._meta.get(UPSTREAM_SERVICES_KEY)

        # We have an existing header value and a previously set upstream service entry by us
        # DEV: We can have an existing value from another upstream service, it doesn't mean it was set by us
        if existing and self._last_upstream_service_entry is not None:
            # Remove the last entry if one exists
            existing, _, old = existing.rpartition(";")
            # No `;` found, we only had the one entry / our last entry
            if not old:
                self._meta[UPSTREAM_SERVICES_KEY] = entry
            else:
                self._meta[UPSTREAM_SERVICES_KEY] = ";".join([existing, entry])

        # Existing upstream value, and none set by us yet
        elif existing:
            self._meta[UPSTREAM_SERVICES_KEY] = ";".join([existing, entry])
        else:
            self._meta[UPSTREAM_SERVICES_KEY] = entry

        # Keep track of the last entry that we created/added
        self._last_upstream_service_entry = entry

    @property
    def sampling_priority(self):
        # type: () -> Optional[NumericType]
        """Return the context sampling priority for the trace."""
        return self._metrics.get(SAMPLING_PRIORITY_KEY)

    @sampling_priority.setter
    def sampling_priority(self, value):
        # type: (Optional[NumericType]) -> None
        with self._lock:
            if value is None:
                if SAMPLING_PRIORITY_KEY in self._metrics:
                    del self._metrics[SAMPLING_PRIORITY_KEY]
                return
            self._metrics[SAMPLING_PRIORITY_KEY] = value

    @property
    def dd_origin(self):
        # type: () -> Optional[Text]
        """Get the origin of the trace."""
        return self._meta.get(ORIGIN_KEY)

    @dd_origin.setter
    def dd_origin(self, value):
        # type: (Optional[Text]) -> None
        """Set the origin of the trace."""
        with self._lock:
            if value is None:
                if ORIGIN_KEY in self._meta:
                    del self._meta[ORIGIN_KEY]
                return
            self._meta[ORIGIN_KEY] = value

    @deprecated("Cloning contexts will no longer be required in 0.50", version="0.50")
    def clone(self):
        # type: () -> Context
        """
        Partially clones the current context.
        It copies everything EXCEPT the registered and finished spans.
        """
        return self

    def __eq__(self, other):
        # type: (Any) -> bool
        if isinstance(other, Context):
            with self._lock:
                return (
                    self.trace_id == other.trace_id
                    and self.span_id == other.span_id
                    and self._meta == other._meta
                    and self._metrics == other._metrics
                )
        return False

    def __repr__(self):
        # type: () -> str
        return "Context(trace_id=%s, span_id=%s, _meta=%s, _metrics=%s)" % (
            self.trace_id,
            self.span_id,
            self._meta,
            self._metrics,
        )

    __str__ = __repr__
