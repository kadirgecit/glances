#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Glances - An eye on your system
#
# Copyright (C) 2014 Nicolargo <nicolas@nicolargo.com>
#
# Glances is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Glances is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# Import Glances lib
from glances.plugins.glances_plugin import GlancesPlugin
from glances.core.glances_monitor_list import monitorList as glancesMonitorList


class Plugin(GlancesPlugin):
    """
    Glances's monitor Plugin
    """

    def __init__(self):
        GlancesPlugin.__init__(self)

        # We want to display the stat in the curse interface
        self.display_curse = True
        # Set the message position
        # It is NOT the curse position but the Glances column/line
        # Enter -1 to right align
        self.column_curse = 1
        # Enter -1 to diplay bottom
        self.line_curse = 3

        # Init stats
        self.glances_monitors = None
        self.stats = []

    def load_limits(self, config):
        """
        Load the monitored list from the conf file
        """
        # print "DEBUG: Monitor plugin load config file %s" % config
        self.glances_monitors = glancesMonitorList(config)

    def update(self):
        """
        Nothing to do here
        Just return the global glances_log
        """
        # Check if the glances_monitor instance is init
        if (self.glances_monitors == None):
            return self.stats

        # Update the monitored list (result of command)
        self.glances_monitors.update()

        # Put it on the stats var
        self.stats = self.glances_monitors.get()

        return self.stats

    def get_alert(self, nbprocess=0, countmin=None, countmax=None, header="", log=False):
        # Return the alert status relative to the process number
        if (nbprocess is None):
            return 'OK'
        if (countmin is None):
            countmin = nbprocess
        if (countmax is None):
            countmax = nbprocess
        if (nbprocess > 0):
            if (int(countmin) <= int(nbprocess) <= int(countmax)):
                return 'OK'
            else:
                return 'WARNING'
        else:
            if (int(countmin) == 0):
                return 'OK'
            else:
                return 'CRITICAL'

    def msg_curse(self, args=None):
        """
        Return the dict to display in the curse interface
        """
        # Init the return message
        ret = []

        # Only process if stats exist and display plugin enable...
        if ((self.stats == []) or (args.disable_process)):
            return ret

        # Build the string message
        for m in self.stats:
            msg = "{0:<16} ".format(str(m['description']))
            ret.append(self.curse_add_line(
                msg, self.get_alert(m['count'], m['countmin'], m['countmax'])))
            msg = "{0:<3} ".format(m['count'] if (m['count'] > 1) else "")
            ret.append(self.curse_add_line(msg))
            msg = "{0:13} ".format(_("RUNNING") if (m['count'] >= 1) else _("NOT RUNNING"))
            ret.append(self.curse_add_line(msg))
            msg = "{0}".format(m['result'] if (m['count'] >= 1) else "")
            ret.append(self.curse_add_line(msg))
            ret.append(self.curse_new_line())

        # Delete the last empty line
        try:
            ret.pop()
        except IndexError:
            pass

        return ret