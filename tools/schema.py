"""Shared schema definitions for the Control Centre state layer.

Every contribution an agent files must declare one of these kinds. The validator
rejects anything else, which is what stops the state layer drifting into a pile
of unstructured notes.
"""

# A contribution declares "kind" plus the fields required for that kind.
KINDS = {
    "project": {
        "required": ["id", "name", "path", "status", "live_edge"],
        "optional": ["active", "verification", "notes", "authority"],
        "collection": "projects",
    },
    "firewall": {
        "required": ["who", "state", "topic", "earliest_change", "rule"],
        "optional": ["project", "belief", "notes"],
        "collection": "firewalls",
    },
    "anchor": {
        "required": ["anchor", "year"],
        "optional": ["project", "note", "chapter"],
        "collection": "anchors",
    },
    "canon": {
        "required": ["claim", "confidence"],
        "optional": ["sources", "note", "project"],
        "collection": "canon",
    },
    "lock": {
        "required": ["lock", "value"],
        "optional": ["project", "note"],
        "collection": "locks",
    },
    "decision": {
        "required": ["decision", "reason"],
        "optional": ["project", "authorized_by", "date", "supersedes"],
        "collection": "decisions",
    },
    "correction": {
        "required": ["was", "now", "reason"],
        "optional": ["project", "file", "line", "found_by"],
        "collection": "corrections",
    },
    "note": {
        "required": ["text"],
        "optional": ["project", "tag"],
        "collection": "notes",
    },
}

# Firewall state must be one of these. Anything else is a new state, which is a
# law change and needs the user, not an agent.
FIREWALL_STATES = [
    "KNOWN", "KNOWN PARTLY", "SUSPICION", "DISBELIEF",
    "UNKNOWN", "FALSE BELIEF", "HIDDEN",
]

# Confidence tags. A contribution claiming canon strength must say where it came from.
CONFIDENCE_LEVELS = ["canon", "fan", "design", "user ruling", "on page", "reported"]

PROJECT_STATUSES = [
    "live", "active", "gate-pass", "portable", "reference",
    "template", "external", "paused", "superseded",
]

# Fields an agent may never set by contribution. These change the shape of the
# system and belong to the user.
RESERVED_FIELDS = ["_comment", "authority_order", "seven_gates", "gate_scope_warning"]
