# Copyright 2025 Red Hat
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from __future__ import absolute_import

import collections
import typing


TableDataType = typing.Iterable[typing.Dict[str, typing.Any]]
OptionalTableDataType = typing.Optional[TableDataType]
TableSetItemValueType = typing.Union[typing.Dict[str, typing.Any],
                                     TableDataType]


class TableData(collections.UserList):
    """
    A list-like class for managing tabular data where each item is a dictionary
    and all dictionaries are guaranteed to have the same set of keys (schema).

    This class enforces the schema upon initialization and when new items are
    added.
    """
    _schema: typing.List[str] = []  # Stores the ordered list of expected keys

    def __init__(self, initial_data: OptionalTableDataType = None):
        """
        Initializes the TableData object.

        Args:
            initial_data: An optional iterable of dictionaries to pre-populate
                          the table.
                          If provided, the schema will be inferred from the
                          first dictionary (if any), and all subsequent
                          dictionaries must conform to this schema.
        """
        super().__init__()
        if initial_data:
            # Convert to list to iterate multiple times if needed
            initial_data_list = list(initial_data)
            if initial_data_list:
                # Infer schema from the first item's keys (order matters)
                self._schema = list(initial_data_list[0].keys())
                for item in initial_data_list:
                    self._validate_item(item)
                    self.data.append(item)  # Add to the internal list
            else:
                self._schema = []  # No initial data, so no schema yet

    @property
    def schema(self) -> typing.List[str]:
        """Returns the ordered list of keys (headers) for the table."""
        return self._schema

    def _validate_item(self, item: typing.Dict[str, typing.Any]):
        """
        Internal method to validate if a dictionary conforms to the current
        schema.
        Raises ValueError if the item does not conform.
        """
        if not isinstance(item, dict):
            raise TypeError(
                f"Items must be dictionaries, but got {type(item)}")

        if not self._schema:
            # If schema is not yet set, infer it from the first item
            self._schema = list(item.keys())
            if not self._schema:  # Handle empty dictionary as first item
                raise ValueError("Cannot infer schema from an empty "
                                 "dictionary as the first item.")
        else:
            # Check if the keys match the schema
            if set(item.keys()) != set(self._schema):
                raise ValueError("Dictionary keys do not match schema. "
                                 f"Expected {set(self._schema)}, "
                                 f"got {set(item.keys())}")
            # Optionally, check order if strict order is needed:
            # if list(item.keys()) != self._schema:
            #     raise ValueError("Dictionary key order does not match "
            #                      f"schema. Expected {self._schema}, "
            #                      f"got {list(item.keys())}")

    def append(self, item: typing.Dict[str, typing.Any]):
        """Appends a dictionary to the table, enforcing schema."""
        self._validate_item(item)
        super().append(item)

    def insert(self, i: int, item: typing.Dict[str, typing.Any]):
        """Inserts a dictionary into the table, enforcing schema."""
        self._validate_item(item)
        super().insert(i, item)

    # The correct signature for __setitem__ to avoid MyPy errors
    @typing.overload
    def __setitem__(self,
                    key: typing.SupportsIndex,
                    value: typing.Dict[str, typing.Any]): ...

    @typing.overload
    def __setitem__(self,
                    key: slice,
                    value: TableDataType): ...

    def __setitem__(self,
                    key: typing.Union[typing.SupportsIndex, slice],
                    value: TableSetItemValueType):
        """Sets an item or slice, enforcing schema."""
        if isinstance(key, slice):
            if not isinstance(value, list):
                raise TypeError(
                    "Must assign a list of dictionaries to a slice")
            for item in value:
                self._validate_item(item)
        else:
            if not isinstance(value, dict):
                raise TypeError(
                    "Must assign a dictionaries to an index")
            self._validate_item(value)
        super().__setitem__(key, value)

    # You might also want to override __add__ and __iadd__ for concatenation
    def __add__(self, other: TableDataType):
        if not isinstance(other, list):
            other = list(other)
        new_data = self.data + other
        return type(self)(new_data)  # Create a new re-validated instance

    def __iadd__(self, other: TableDataType):
        for item in other:
            self.append(item)  # Use append to ensure validation
        return self

    def __str__(self):
        if not self.data:
            return "TableData(Empty)"
        # Simple string representation, could be improved for tabular display
        s = "TableData:\n"
        s += ", ".join(self.schema) + "\n"
        for row in self.data:
            s += ", ".join(
                [str(row.get(key, 'N/A')) for key in self.schema]) + "\n"
        return s

    def __repr__(self):
        return f"{type(self).__name__}({self.data!r})"
