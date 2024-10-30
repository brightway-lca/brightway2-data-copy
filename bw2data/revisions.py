import json
from typing import Any, Optional, Self, Sequence, TypeVar

import deepdiff
from snowflake import SnowflakeGenerator as sfg

from bw2data.backends import schema


SD = TypeVar("SD", bound=schema.SignaledDataset)


class RevisionGraph:
    """Graph of revisions, edges are based on `metadata.parent_revision`."""

    class Iterator(object):
        """Helper class implementing iteration from child to parent."""

        def __init__(self, g: "RevisionGraph"):
            self.head = g.head
            self.id_map = g.id_map

        def __next__(self) -> Optional[dict]:
            if self.head is None:
                raise StopIteration
            ret = self.id_map[self.head]
            self.head = ret["metadata"].get("parent_revision")
            return ret

    def __init__(self, head: str, revisions: Sequence[dict]):
        self.head = head
        self.revisions = revisions
        self.id_map = {r["metadata"]["revision"]: r for r in revisions}

    def __iter__(self):
        """Iterates the graph from head to root."""
        return self.Iterator(self)


class Delta:
    """
    The difference between two versions of an object.

    Can be serialized, transfered, and applied to the same previous version to
    change it to the new state.
    """
    def apply(self, obj):
        return obj + self.delta

    @classmethod
    def from_dict(cls: Self, d: dict) -> Self:
        ret = cls()
        ret.delta = deepdiff.Delta(
            JSONEncoder().encode(d), deserializer=deepdiff.serialization.json_loads
        )
        return ret

    @classmethod
    def from_difference(
        cls: Self,
        obj_type: str,
        obj_id: int,
        diff: deepdiff.DeepDiff,
    ) -> Self:
        ret = cls()
        ret.type = obj_type
        ret.id = obj_id
        ret.delta = deepdiff.Delta(diff)
        return ret


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Delta):
            return super().default(obj)
        # XXX
        obj.delta.serializer = deepdiff.serialization.json_dumps
        return json.loads(obj.delta.dumps())


def generate_metadata(
    parent_revision: Optional[str] = None,
    revision: Optional[str] = None,
) -> dict[str, Any]:
    ret = {}
    ret["parent_revision"] = parent_revision
    ret["revision"] = revision or next(sfg(0))
    ret["authors"] = ret.get("authors", "Anonymous")
    ret["title"] = ret.get("title", "Untitled revision")
    ret["description"] = ret.get("description", "No description")
    return ret


def generate_delta(old: Optional[SD], new: SD) -> Delta:
    """
    Generates a patch object from one version of an object to another.

    Both objects are assumeed to be of the same type, but `old` can be `None` to
    generate a creation event.
    """
    from bw2data.backends import utils

    obj_type = new.__class__
    assert old is None or old.__class__ == obj_type
    assert old is None or not old.id or old.id == new.id
    mapper = getattr(utils, f"dict_as_{obj_type.__name__.lower()}")
    return Delta.from_difference(
        obj_type.__name__.removesuffix("Dataset").lower(),
        new.id,
        deepdiff.DeepDiff(
            mapper(old.data) if old else None,
            mapper(new.data),
            verbose_level=2,
        ),
    )


def generate_revision(metadata: dict, delta: Sequence[Delta]) -> dict:
    return {
        "metadata": metadata,
        "data": [{"type": d.type, "id": d.id, "delta": d} for d in delta],
    }
