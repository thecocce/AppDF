import os
import zipfile
import lxml.etree
import lxml.objectify

import sys

# @silent_normalize
def silent_normalize(f):
    def decorate(self, local="default"):
        try:
            if local=="default":
                node = f(self)
            else:
                node = f(self, local)
            return node.text.encode("utf-8")
        except AttributeError:
            return None

    return decorate


class AppDF(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self.archive = None

    def parse(self):
        with zipfile.ZipFile(self.file_path, "r") as archive:
            if archive.testzip():
                raise RuntimeError("AppDF file `{}' is broken".format(file))

            if "description.xml" not in archive.namelist():
                raise RuntimeError("Invalid AppDF file `{}'".format(file))

            self.archive = archive
            self.xml = archive.read("description.xml")
            self.obj = lxml.objectify.fromstring(self.xml)
    
    def validate(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        xsd_file = os.path.join(current_dir, "..", "..", "..", "spec",
                                "appdf-description.xsd")
        schema = lxml.etree.XMLSchema(lxml.etree.parse(xsd_file))
        schema.assertValid(lxml.etree.fromstring(self.xml))

    @silent_normalize
    def title(self, local="default"):
        if local == "default":
            return self.obj.application.description.texts.title
        else:
            for desc in self.obj.application["description-localization"]:
                if desc.attrib["language"] == local:
                    return desc.texts.title
        return ""

    def video(self):
        url = None

        if self.obj.application.description.videos["youtube-video"]:
            video_id = self.obj.application.description.videos["youtube-video"]
            url = "http://www.youtube.com/watch?v={}".format(video_id)

        return url

    @silent_normalize
    def website(self):
        return self.obj.application["customer-support"].website

    @silent_normalize
    def email(self):
        return self.obj.application["customer-support"].email

    @silent_normalize
    def phone(self):
        return self.obj.application["customer-support"].phone

    @silent_normalize
    def privacy_policy(self):
        return self.obj.application.description.texts["privacy-policy"]

    @silent_normalize
    def full_description(self, local="default"):
        if local=="default":
            return self.obj.application.description.texts["full-description"]
        else:
            for desc in self.obj.application["description-localization"]:
                if desc.attrib["language"]==local:
                    return desc.texts["full-description"]
        return ""

    @silent_normalize
    def short_description(self, local="default"):
        if local=="default":
            return self.obj.application.description.texts["short-description"]
        else:
            for desc in self.obj.application["description-localization"]:
                if desc.attrib["language"]==local:
                    return desc.texts["short-description"]
        return ""

    @silent_normalize
    def recent_changes(self, local="default"):
        if local=="default":
            return self.obj.application.description.texts["recent-changes"]
        else:
            for desc in self.obj.application["description-localization"]:
                if desc.attrib["language"]==local:
                    return desc.texts["recent-changes"]
        return ""

    @silent_normalize
    def type(self):
        return self.obj.application.categorization.type

    @silent_normalize
    def category(self):
        return self.obj.application.categorization.category

    @silent_normalize
    def rating(self):
        return self.obj.application["content-description"]["content-rating"]
