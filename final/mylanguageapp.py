import wx
import os
import sys
import builtins
from wx.lib.mixins.inspection import InspectionMixin

builtins.__dict__["_"] = wx.GetTranslation
languages = [wx.LANGUAGE_ENGLISH, wx.LANGUAGE_GREEK]


class MyLanguageApp(wx.App, InspectionMixin):
    """
    Gets the user's locale to set the GUI language.

    This class is called within logsim.py and launches the appropriate GUI version based on the user's local.
    Currently only Greek and English are supported.
    If the user's system locale is not one of the translated languages then it is set to English (default).
    """

    def OnInit(self):

        self.Init()
        language = wx.Locale.GetSystemLanguage()

        if language in languages:
            wx_lang = language
        else:
            wx_lang = wx.LANGUAGE_DEFAULT  # English

        # wx_lang = 94  # Uncomment this line to launch the Greek GUI manually

        # Create locale
        self.locale = wx.Locale(wx_lang)
        if self.locale.IsOk():
            basepath = os.path.abspath(os.path.dirname(sys.argv[0]))
            localedir = os.path.join(basepath, "locale")
            domain = "messages_gr"  # .mo and .po files containing the translations
            self.locale.AddCatalogLookupPathPrefix(localedir)
            self.locale.AddCatalog(domain)
        else:
            self.locale = None

        return True
