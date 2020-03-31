# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import os
import sys

import sgtk
from sgtk.platform import SoftwareLauncher, SoftwareVersion, LaunchInformation




class MariLauncher(SoftwareLauncher):

    @property
    def minimum_supported_version(self):
        """
        The minimum software version that is supported by the launcher.
        """
        return "2.6v4"
    def prepare_launch(self, exec_path, args, file_to_open=None):
        """
        Prepares an environment to launch Natron in that will automatically
        load Toolkit and the tk-natron engine when Natron starts.

        :param str exec_path: Path to Natron executable to launch.
        :param str args: Command line arguments as strings.
        :param str file_to_open: (optional) Full path name of a file to open on
                                            launch.
        :returns: :class:`LaunchInformation` instance
        """
        required_env = {}

        # Run the engine's init.py file when Natron starts up
        startup_path = os.path.join(self.disk_location, "startup")

        # Prepare the launch environment with variables required by the
        # classic bootstrap approach.
        self.logger.debug(
            "Preparing Natron Launch via Toolkit Classic methodology ...")
        required_env["TANK_ENGINE"] = self.engine_name
        required_env["TANK_CONTEXT"] = sgtk.context.serialize(self.context)
        required_env["MARI_SCRIPT_PATH"] = startup_path


        if file_to_open:
            # Add the file name to open to the launch environment
            required_env["SGTK_FILE_TO_OPEN"] = file_to_open

        return LaunchInformation(exec_path, args, required_env)


    def _icon_from_engine(self):
        """
        Use the default engine icon as natron does not supply
        an icon in their software directory structure.

        :returns: Full path to application icon as a string or None.
        """

        # the engine icon
        engine_icon = os.path.join(self.disk_location, "icon_256.png")
        return engine_icon

    def scan_software(self):

        try:
            import rez as _
        except ImportError:
            rez_path = self.get_rez_module_root()
            if not rez_path:
                raise EnvironmentError('rez is not installed and could not be automatically found. Cannot continue.')

            sys.path.append(rez_path)
        from rez.package_search import ResourceSearcher , ResourceSearchResultFormatter


        searcher = ResourceSearcher()
        formatter = ResourceSearchResultFormatter()
        _ ,packages = searcher.search("mari")

        supported_sw_versions = []
        self.logger.debug("Scanning for Mari executables...")
        infos = formatter.format_search_results(packages)

        for info in infos:
            name,version = info[0].split("-")
            

            software = SoftwareVersion(version,name,"rez_init",self._icon_from_engine())
            
            (supported, reason) = self._is_supported(software)
            if supported:
                supported_sw_versions.append(software)

        return supported_sw_versions


    def get_rez_module_root(self):
        
        
        command = self.get_rez_root_command()
        module_path, stderr = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()

        module_path = module_path.strip()

        if not stderr and module_path:
            return module_path



        return ''

    def get_rez_root_command(self):

        return 'rez-env rez -- printenv REZ_REZ_ROOT'
