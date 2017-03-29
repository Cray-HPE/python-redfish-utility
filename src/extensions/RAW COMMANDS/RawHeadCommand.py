###
# Copyright 2017 Hewlett Packard Enterprise, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###

# -*- coding: utf-8 -*-
""" RawHead Command for rdmc """

import sys
import json

import redfish

from optparse import OptionParser
from rdmc_base_classes import RdmcCommandBase, RdmcOptionParser
from rdmc_helper import ReturnCodes, InvalidCommandLineError, \
                    InvalidCommandLineErrorOPTS, UI

class RawHeadCommand(RdmcCommandBase):
    """ Raw form of the head command """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='rawhead',\
            usage='rawhead [PATH]\n\n\tRun to to retrieve data from the ' \
                'passed in path\n\texample: rawhead "/redfish/v1/systems/'\
                '(system ID)"',\
            summary='This is the raw form of the HEAD command.',\
            aliases=['rawhead'],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.lobobj = rdmcObj.commandsDict["LoginCommand"](rdmcObj)

    def run(self, line):
        """ Main raw head worker function

        :param line: command line input
        :type line: string.
        """
        try:
            (options, args) = self._parse_arglist(line)
        except:
            if ("-h" in line) or ("--help" in line):
                return ReturnCodes.SUCCESS
            else:
                raise InvalidCommandLineErrorOPTS("")
        url = None

        if options.sessionid:
            url = self.sessionvalidation(options)
        else:
            self.headvalidation(options)

        if len(args) > 1:
            raise InvalidCommandLineError("Raw head only takes 1 argument.\n")
        elif len(args) == 0:
            raise InvalidCommandLineError("Missing raw head input path.\n")

        if args[0].startswith('"') and args[0].endswith('"'):
            args[0] = args[0][1:-1]

        results = self._rdmc.app.head_handler(args[0], \
                                              verbose=self._rdmc.opts.verbose, \
                                              sessionid=options.sessionid, \
                                              url=url, silent=options.silent, \
											  service=options.service)

        content = None
        tempdict = dict()

        if results and results.status == 200:
            if results._http_response:
                content = results._http_response.msg.headers
            else:
                content = results._headers

            for item in content:
                if isinstance(item, dict):
                    for key, value in item.iteritems():
                        tempdict[key] = value
                else:
                    item = item.replace(": ", ":").replace("\r\n", "").\
                                                                split(":", 1)
                    tempdict[item[0]] = item[1]

            if options.filename:
                output = json.dumps(tempdict, indent=2, \
                                                    cls=redfish.ris.JSONEncoder)
                filehndl = open(options.filename[0], "w")
                filehndl.write(output)
                filehndl.close()

                sys.stdout.write(u"Results written out to '%s'.\n" % \
                                                            options.filename[0])
            else:
                if options.service:
                    sys.stdout.write("%s\n" % tempdict)
                else:
                    UI().print_out_json(tempdict)
        else:
            return ReturnCodes.NO_CONTENTS_FOUND_FOR_OPERATION

        #Return code
        return ReturnCodes.SUCCESS

    def headvalidation(self, options):
        """ Raw head validation function

        :param options: command line options
        :type options: list.
        """
        inputline = list()

        try:
            self._rdmc.app.get_current_client()
        except:
            if options.user or options.password or options.url:
                if options.url:
                    inputline.extend([options.url])
                if options.user:
                    inputline.extend(["-u", options.user])
                if options.password:
                    inputline.extend(["-p", options.password])
            else:
                if self._rdmc.app.config.get_url():
                    inputline.extend([self._rdmc.app.config.get_url()])
                if self._rdmc.app.config.get_username():
                    inputline.extend(["-u", \
                                  self._rdmc.app.config.get_username()])
                if self._rdmc.app.config.get_password():
                    inputline.extend(["-p", \
                                  self._rdmc.app.config.get_password()])

            self.lobobj.loginfunction(inputline, skipbuild=True)

    def sessionvalidation(self, options):
        """ Raw head session validation function

        :param options: command line options
        :type options: list.
        """

        url = None
        if options.user or options.password or options.url:
            if options.url:
                url = options.url
        else:
            if self._rdmc.app.config.get_url():
                url = self._rdmc.app.config.get_url()
        if url and not "https://" in url:
            url = "https://" + url

        return url

    def definearguments(self, customparser):
        """ Wrapper function for new command main function

        :param customparser: command line input
        :type customparser: parser.
        """
        if not customparser:
            return

        customparser.add_option(
            '--url',
            dest='url',
            help="Use the provided iLO URL to login.",
            default=None,
        )
        customparser.add_option(
            '-u',
            '--user',
            dest='user',
            help="If you are not logged in yet, including this flag along"\
            " with the password and URL flags can be used to log into a"\
            " server in the same command.""",
            default=None,
        )
        customparser.add_option(
            '-p',
            '--password',
            dest='password',
            help="""Use the provided iLO password to log in.""",
            default=None,
        )
        customparser.add_option(
            '--silent',
            dest='silent',
            action="store_true",
            help="""Use this flag to silence responses""",
            default=None,
        )
        customparser.add_option(
            '--sessionid',
            dest='sessionid',
            help="Optionally include this flag if you would prefer to "\
            "connect using a session id instead of a normal login.",
            default=None
        )
        customparser.add_option(
            '-f',
            '--filename',
            dest='filename',
            help="""Use the provided filename to perform operations.""",
            action="append",
            default=None,
        )
        customparser.add_option(
            '--service',
            dest='service',
            action="store_true",
            help="""Use this flag to enable service mode and increase """\
                                                """the function speed""",
            default=False,
        )
