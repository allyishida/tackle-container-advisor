# *****************************************************************
# Copyright IBM Corporation 2021
# Licensed under the Eclipse Public License 2.0, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# *****************************************************************


import os
import re
import logging


class version_detector:
    @staticmethod
    def mask_entity(text):
        """
        Replace the text with 'Entity_MASK' if its subtring is present in the blacklist since the numbers in the blacklist
        elements shouldn't be considered as version
        """
        try:
            blacklist = (
            "db2", "as/400", "j2ee", "neo4j", "log4j", "neo4", "log4net", "log4", "64-bit", "32-bit", "64bit", "32bit",
            "os2")

            for each in blacklist:
                if text.strip().lower().find(each.strip().lower()) >= 0:
                    # print("mask text:",text)
                    text = text.strip().lower().replace(each, "ENTITY_MASK")
            return text
        except Exception as e:
            logging.error(str(e))
         
    @staticmethod
    def get_version_strings(text):

        """
        Mask the input text and apply the predefined pattern to extract version from the input text
        """

        try:

            patterns = (r'[a-zA-Z]*\d+(\.*\d+)*(\-*\s*/*[0-9a-zA-Z]*\d*[0-9a-zA-Z]*\.*\d*)*')
            pattern_number = (r'\d+(\.*\d*)*(\-*/*[0-9a-zA-Z]*\d*[0-9a-zA-Z]*\.*\d*)*')

            version = "NA_VERSION"

            text0 = version_detector.mask_entity(text)

            match = re.search(patterns, text0)
            if match != None:
                version = match.group(0)

                version = version.strip(' ')
                version = version.strip('-')
                if version.find("(") < 0:
                    version = version.strip(r'\)')

            # verify version
            version_list = version.split(" ")

            # if len(version_list)> max_len:
            version_final = ""

            keep_list = {"service", "pack", "standard", "edit"}

            for each in version_list:
                if each.isalpha() and each not in keep_list:
                    break

                version_final += each + " "

            version_final = version_final.strip()


            # single version java8, 10g  need to keep
            if version_final.find(" ") < 0:
                if version_final[0].isdigit() == False:
                    match_ver = re.search(pattern_number, version_final)
                    if match_ver != None:
                        version_final = match_ver.group(0)

            if len(version_final) == 0:
                version_final = "NA_VERSION"

            version_final = version_final.strip(" ")
            version_final = version_final.strip("-")
            version_final = version_final.strip(".")

            return version_final.strip()
        except Exception as e:
            logging.error(str(e))
    
  
