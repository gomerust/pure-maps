# -*- coding: utf-8 -*-

# Copyright (C) 2014 Osmo Salomaa, 2018 Rinigus
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

"""An application to display maps and stuff."""

import poor
import pyotherside
import sys

__all__ = ("Application",)


class Application:

    """An application to display maps and stuff."""

    def __init__(self):
        """Initialize an :class:`Application` instance."""
        self.basemap = None
        self.geocoder = None
        self.guide = None
        self.history = poor.HistoryManager()
        self.icon = poor.IconFinder()
        self.narrative = poor.Narrative()
        self.router = None
        self.voice_tester = None
        self.set_basemap(poor.conf.basemap)
        self.set_geocoder(poor.conf.geocoder)
        self.set_guide(poor.conf.guide)
        self.set_router(poor.conf.router)

    def get_attribution(self, type, providers):
        """Return attribution entries for given providers."""
        items = []
        cls = poor.util.get_provider_class(type)
        for provider in providers:
            with poor.util.silent(Exception):
                for item in cls(provider).attribution:
                    if item["text"] not in (x["text"] for x in items):
                        items.append(item)
        return items

    def has_mapmatching(self):
        """Return True if map matching requirements are met"""
        return (poor.util.requirement_found("harbour-osmscout-server") or poor.util.requirement_found("osmscout-server"))

    def quit(self):
        """Quit the application."""
        print("Quitting")
        print("Calling http.pool.terminate")
        poor.http.pool.terminate()
        print("Calling poor.conf.write")
        poor.conf.write()
        print("Calling self.history.write")
        self.history.write()
        print("Calling self.narrative.quit")
        self.narrative.quit()
        print("All quit methods called")

    def set_basemap(self, basemap):
        """Set basemap from string `basemap`."""
        try:
            newmap = (self.basemap is None or basemap != self.basemap.id)
            self.basemap = poor.Map(basemap)
            poor.conf.set_basemap(basemap)
            if newmap: pyotherside.send('basemap.changed')
        except Exception as error:
            print("Failed to load basemap '{}': {}"
                  .format(basemap, str(error)),
                  file=sys.stderr)
            if self.basemap is None:
                default = poor.conf.get_default("basemap")
                if default != basemap:
                    self.set_basemap(default)

    def set_geocoder(self, geocoder):
        """Set geocoding provider from string `geocoder`."""
        try:
            self.geocoder = poor.Geocoder(geocoder)
            poor.conf.set_geocoder(geocoder)
        except Exception as error:
            print("Failed to load geocoder '{}': {}"
                  .format(geocoder, str(error)),
                  file=sys.stderr)
            if self.geocoder is None:
                default = poor.conf.get_default("geocoder")
                if default != geocoder:
                    self.set_geocoder(default)

    def set_guide(self, guide):
        """Set place guide provider from string `guide`."""
        try:
            self.guide = poor.Guide(guide)
            poor.conf.set_guide(guide)
        except Exception as error:
            print("Failed to load guide '{}': {}"
                  .format(guide, str(error)),
                  file=sys.stderr)
            if self.guide is None:
                default = poor.conf.get_default("guide")
                if default != guide:
                    self.set_guide(default)

    def set_profile(self, profile):
        """Set current profile."""
        if poor.conf.profile == profile: return
        poor.conf.set_profile(profile)
        self.set_basemap(poor.conf.basemap)
        self.set_geocoder(poor.conf.geocoder)
        self.set_guide(poor.conf.guide)
        self.set_router(poor.conf.router)

    def set_router(self, router):
        """Set routing provider from string `router`."""
        try:
            self.router = poor.Router(router)
            poor.conf.set_router(router)
        except Exception as error:
            print("Failed to load router '{}': {}"
                  .format(router, str(error)),
                  file=sys.stderr)
            if self.router is None:
                default = poor.conf.get_default("router")
                if default != router:
                    self.set_router(default)

    def voice_tester_start(self):
        if self.voice_tester is not None: return
        self.voice_tester = poor.VoiceGenerator()
        return True

    def voice_tester_stop(self):
        if self.voice_tester is not None:
            self.voice_tester.quit()
            self.voice_tester = None
