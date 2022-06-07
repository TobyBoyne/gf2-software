"""
import sys, os
import gettext
import wx
_ = gettext.gettext
# Hack to get the locale directory


basepath = os.path.abspath(os.path.dirname(sys.argv[0]))
localedir = os.path.join(basepath, "locale")
langid = wx.LANGUAGE_DEFAULT    # use OS default; or use LANGUAGE_JAPANESE, etc.
domain = "messages"             # the translation file is messages.mo
# Set locale for wxWidgets

mylocale = wx.Locale(langid)
mylocale.AddCatalogLookupPathPrefix(localedir)
mylocale.AddCatalog(domain)

# Set up Python's gettext
mytranslation = gettext.translation(domain, localedir,
[mylocale.GetCanonicalName()], fallback = True)
mytranslation.install()

if __name__ == '__main__':
     # use Python's gettext
     print(_("Hello, World!"))
     # use wxWidgets' translation services
     print(wx.GetTranslation("Hello, World!"))

# if getting unicode errors try something like this:
# #print wx.GetTranslation("Hello, World!").encode("utf-8")"""
import uuid
import gettext
import wx
import os
import sys
import builtins
#import Locale
languages = [wx.LANGUAGE_ENGLISH, wx.LANGUAGE_GREEK]
print(languages)
language = wx.Locale.GetSystemLanguage()
print(language)

builtins.__dict__["_"] = wx.GetTranslation

if language in languages:
    wx_lang = language
else:
    wx_lang = wx.LANGUAGE_GREEK

print(wx_lang)

# create locale
locale = wx.Locale(wx_lang)
if locale.IsOk():
    basepath = os.path.abspath(os.path.dirname(sys.argv[0]))
    # sys.path.append(base_path)
    localedir = os.path.join(basepath, "locale")
    print(localedir)
    domain = "messages"
    locale.AddCatalogLookupPathPrefix(localedir)
    locale.AddCatalog(domain)
else:
    locale = None

#mylocale = wx.Locale(langid)
#mylocale.AddCatalogLookupPathPrefix(localedir)
#mylocale.AddCatalog(domain)

"""domain = "messages"
el = gettext.translation(domain, localedir='locale', languages=['el:en'])
el.install()

_ = el.gettext
#_ = gettext.gettext # marker on strings to translate
"""
class BankAccount(object):

    def __init__(self, initial_balance=0):
        self.balance = initial_balance
        self.id = str(uuid.uuid4())
        print(_("Bank account '{id}' was created with initial Balance: {balance}").format(id=self.id, balance=self.balance))

    def deposit(self, amount):
        self.balance += amount
        print(_("Deposited {amount} to current balance").format(amount=amount))

    def withdraw(self, amount):
        self.balance -= amount
        print(_("&?   About"))
        print(_("&📁 Open File    Ctrl+O"))
        print(_("Withdrawned {amount} from current balance").format(amount=amount))

    def overdrawn(self):
        return self.balance < 0

    def print_balance(self):
        print(_("Balance for Account '{id}' is: {balance}").
              format(id=self.id, balance=self.balance))


class Bank(object):
    bank_accounts = []

    def create_account(self, initial_balance=0):
        new_account = BankAccount(initial_balance)
        self.bank_accounts.append(new_account)

        return new_account

    def list_accounts(self):
        return self.bank_accounts

    def transfer_balance(self, from_acccount_id, to_account_id, amount):
        from_account = self.get_account_by_id(from_acccount_id)
        to_account = self.get_account_by_id(to_account_id)

        if from_account is None or to_account is None:
            print(_("One of the Account numbers does not exist"))
            return

        from_account.withdraw(amount)
        to_account.deposit(amount)

        print(_("Successfully transfered {amount} from Account '{from_acccount_id}' to Account: {to_account_id}").
              format(amount=amount, from_acccount_id=from_acccount_id, to_account_id=to_account_id))

    def get_account_by_id(self, id_param):
        accounts = [acc for acc in self.bank_accounts if acc.id == id_param]

        if len(accounts) == 1:
            return accounts[0]
        else:
            return None


if __name__ == '__main__':
    bank = Bank()
    first = bank.create_account(100)
    second = bank.create_account(150)

    bank.transfer_balance(first.id, second.id, 50)

    first.print_balance()
    second.print_balance()