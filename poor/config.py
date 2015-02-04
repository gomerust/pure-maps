# -*- coding: utf-8 -*-

# Copyright (C) 2014 Osmo Salomaa
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Attribute dictionary of configuration values."""

import copy
import os
import poor
import sys

__all__ = ("ConfigurationStore",)

DEFAULTS = {
    "allow_tile_download": True,
    "auto_center": False,
    "basemap": "mapquest_open",
    "cache_max_age": 36500, # days
    "center": [0.0, 0.0],
    "download_timeout": 10, # seconds
    "geocoder": "mapquest_nominatim",
    "gps_update_interval": 1, # seconds
    "guide": "foursquare",
    # 'always', 'navigating' or 'never'.
    "keep_alive": "navigating",
    "overlays": [],
    "router": "mapquest_open",
    "show_routing_narrative": True,
    "zoom": 15,
}


class AttrDict(dict):

    """Dictionary with attribute access to keys."""

    def __init__(self, *args, **kwargs):
        """Initialize an :class:`AttrDict` instance."""
        dict.__init__(self, *args, **kwargs)
        self.__dict__ = self


class ConfigurationStore(AttrDict):

    """
    Attribute dictionary of configuration values.

    Options to most methods can be given as a dotted string,
    e.g. 'routers.mycoolrouter.type'.
    """

    def __init__(self):
        """Initialize a :class:`Configuration` instance."""
        AttrDict.__init__(self, copy.deepcopy(DEFAULTS))

    def _coerce(self, value, ref):
        """Coerce type of `value` to match `ref`."""
        # XXX: No coercion done if ref is an empty list!
        if isinstance(value, list) and ref:
            return [self._coerce(x, ref[0]) for x in value]
        return type(ref)(value)

    def get(self, option):
        """Return the value of `option`."""
        root = self
        for section in option.split(".")[:-1]:
            root = root[section]
        name = option.split(".")[-1]
        return copy.deepcopy(root[name])

    def get_default(self, option):
        """Return the default value of `option`."""
        defaults = DEFAULTS
        for section in option.split(".")[:-1]:
            defaults = defaults[section]
        name = option.split(".")[-1]
        return copy.deepcopy(defaults[name])

    def _migrate(self, values):
        """Migrate configuration values from earlier versions."""
        # 'tilesource' renamed to 'basemap' in 0.18.
        if not "basemap" in values and "tilesource" in values:
            values["basemap"] = values.pop("tilesource")
        return values

    def read(self, path=None):
        """Read values of options from JSON file at `path`."""
        if path is None:
            path = os.path.join(poor.CONFIG_HOME_DIR, "poor-maps.json")
        if os.path.isfile(path):
            with poor.util.silent(Exception):
                values = poor.util.read_json(path)
                values = self._migrate(values)
                self._update(values)

    def _register(self, values, root=None, defaults=None):
        """Add entries for `values` if missing."""
        root = (self if root is None else root)
        defaults = (DEFAULTS if defaults is None else defaults)
        for name, value in values.items():
            if isinstance(value, dict):
                self._register(values[name],
                               root.setdefault(name, AttrDict()),
                               defaults.setdefault(name, {}))

            else:
                root.setdefault(name, copy.deepcopy(value))
                defaults.setdefault(name, copy.deepcopy(value))

    def register_guide(self, name, values):
        """
        Add configuration `values` for guide `name` if missing.

        e.g. calling ``register_guide("foo", {"type": 1})`` will make type
        available as ``poor.conf.guides.foo.type``.
        """
        self._register({"guides": {name: values}})

    def register_router(self, name, values):
        """
        Add configuration `values` for router `name` if missing.

        e.g. calling ``register_router("foo", {"type": 1})`` will make type
        available as ``poor.conf.routers.foo.type``.
        """
        self._register({"routers": {name: values}})

    def set(self, option, value):
        """Set the value of `option`."""
        root, name = self._split_option(option, create=True)
        root[name] = copy.deepcopy(value)

    def set_add(self, option, item):
        """Add `item` to `option` of type set."""
        root, name = self._split_option(option)
        if not item in root[name]:
            root[name].append(copy.deepcopy(item))

    def set_contains(self, option, item):
        """Return ``True`` if `option` of type set contains `item`."""
        root, name = self._split_option(option)
        return item in root[name]

    def set_remove(self, option, item):
        """Remove `item` from `option` of type set."""
        root, name = self._split_option(option)
        if item in root[name]:
            root[name].remove(item)

    def _split_option(self, option, create=False):
        """Split dotted option to dictionary and option name."""
        root = self
        for section in option.split(".")[:-1]:
            if create and not section in root:
                # Create missing hierarchies.
                root[section] = AttrDict()
            root = root[section]
        name = option.split(".")[-1]
        return root, name

    def _update(self, values, root=None, defaults=None, path=()):
        """Load values of options after validation."""
        root = (self if root is None else root)
        defaults = (DEFAULTS if defaults is None else defaults)
        for name, value in values.items():
            # Ignore options commented out (used prior to 0.18).
            if name.startswith("#"): continue
            if isinstance(value, dict):
                self._update(value,
                             root.setdefault(name, AttrDict()),
                             defaults.setdefault(name, {}),
                             (path + (name,)))

            else:
                try:
                    if name in defaults:
                        # Be liberal, but careful in what to accept.
                        value = self._coerce(value, defaults[name])
                    root[name] = copy.deepcopy(value)
                except Exception as error:
                    full_name = ".".join(path + (name,))
                    print("Discarding bad option-value pair ({}, {}): {}"
                          .format(repr(full_name), repr(value), str(error)),
                          file=sys.stderr)

    def write(self, path=None):
        """Write values of options to JSON file at `path`."""
        if path is None:
            path = os.path.join(poor.CONFIG_HOME_DIR, "poor-maps.json")
        out = copy.deepcopy(self)
        out["version"] = poor.__version__
        with poor.util.silent(Exception):
            poor.util.write_json(out, path)
