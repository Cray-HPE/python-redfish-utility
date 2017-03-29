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
""" RawPost Command for rdmc """

import sys
import json

from optparse import OptionParser
from rdmc_base_classes import RdmcCommandBase, RdmcOptionParser
from rdmc_helper import ReturnCodes, InvalidCommandLineError, \
                    InvalidCommandLineErrorOPTS, UI, InvalidFileInputError, \
                    InvalidFileFormattingError

class RawPostCommand(RdmcCommandBase):
    """ Raw form of the post command """
    def __init__(self, rdmcObj):
        RdmcCommandBase.__init__(self,\
            name='rawpost',\
            usage='rawpost [FILENAME] [OPTIONS]\n\n\tRun to send a post from ' \
                    'the data in the input file.\n\texample: rawpost rawpost.' \
                    'txt\n\n\tExample input file:\n\t{\n\t    "path": "/' \
                    'redfish/v1/systems/(system ID)/Actions/ComputerSystem.'
                    'Reset",\n\t    "body": {\n\t        "ResetType": '\
                    '"ForceRestart"\n\t    }\n\t}',\
            summary='This is the raw form of the POST command.',\
            aliases=['rawpost'],\
            optparser=OptionParser())
        self.definearguments(self.parser)
        self._rdmc = rdmcObj
        self.lobobj = rdmcObj.commandsDict["LoginCommand"](rdmcObj)

    def run(self, line):
        """ Main raw patch worker function

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
        headers = {}
        results = None

        if options.sessionid:
            url = self.sessionvalidation(options)
        else:
            self.postvalidation(options)

        contentsholder = None

        if len(args) == 1:
            try:
                inputfile = open(args[0], 'r')
                contentsholder = json.loads(inputfile.read())
            except Exception, excp:
                raise InvalidFileInputError("%s" % excp)
        elif len(args) > 1:
            raise InvalidCommandLineError("Raw post only takes 1 argument.\n")
        else:
            raise InvalidCommandLineError("Missing raw post file input "\
                                                                "argument.\n")

        if options.headers:
            extraheaders = options.headers.split(',')
            for item in extraheaders:
                header = item.split(':')
                try:
                    headers[header[0]] = header[1]
                except:
                    raise InvalidCommandLineError("Invalid format for " \
                                                            "--headers option.")

        if "path" in contentsholder and "body" in contentsholder:
            returnresponse = False

            if options.response or options.getheaders:
                returnresponse = True

            results = self._rdmc.app.post_handler(contentsholder["path"], \
                  contentsholder["body"], verbose=self._rdmc.opts.verbose, \
                  sessionid=options.sessionid, url=url, headers=headers, \
                  response=returnresponse, silent=options.silent, \
                  providerheader=options.providerid, service=options.service)
        else:
            raise InvalidFileFormattingError("Input file '%s' was not "\
                                             "formatted properly." % args[0])

        if results and returnresponse:
            if options.getheaders:
                sys.stdout.write(json.dumps(dict(\
                                results._http_response.getheaders())) + "\n")

            if options.response:
                sys.stdout.write(results.text)

        #Return code
        return ReturnCodes.SUCCESS

    def postvalidation(self, options):
        """ Raw post validation function

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
        """ Raw post session validation function

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
            '--response',
            dest='response',
            action="store_true",
            help="Use this flag to return the iLO response body.",
            default=False
        )
        customparser.add_option(
            '--getheaders',
            dest='getheaders',
            action="store_true",
            help="Use this flag to return the iLO response headers.",
            default=False
        )
        customparser.add_option(
            '--headers',
            dest='headers',
            help="Use this flag to add extra headers to the request."\
            "\t\t\t\t\t Usage: --headers=HEADER:VALUE,HEADER:VALUE",
            default=None,
        )
        customparser.add_option(
            '--silent',
            dest='silent',
            action="store_true",
            help="""Use this flag to silence responses""",
            default=False,
        )
        customparser.add_option(
            '--sessionid',
            dest='sessionid',
            help="Optionally include this flag if you would prefer to "\
            "connect using a session id instead of a normal login.",
            default=None
        )
        customparser.add_option(
            '--providerid',
            dest='providerid',
            help="""Use this flag to pass in the provider id header""",
            default=None,
        )
        customparser.add_option(
            '--service',
            dest='service',
            action="store_true",
            help="""Use this flag to enable service mode and increase """\
                                                """the function speed""",
            default=False
        )
