# Configuration for Git Projects
import os

# Base paths for repositories
PATH_CPP = r'C:\Users\vitorjna\Desktop\branches\stable'
PATH_JAVA = r'C:\Users\vitorjna\Desktop\Java-gerrit\gitrepos'

# Paths to external tools
PATH_WINMERGE = r'C:\Program Files\WinMerge\WinMergeU.exe'
PATH_TORTOISE = r'c:\Program Files\TortoiseGit\bin\TortoiseGitProc.exe'

# Use TortoiseGit (True) or Git CLI (False)
USE_TORTOISE = True

# Project definitions: { "PROJECT_NAME": (base_path, {"repo1", "repo2", ...}) }
PROJECTS = {
    "VF": (PATH_CPP, {"IntegraTEC_CppDK", "IntegraTEC_Core", "IntegraTEC_Verifone"}),
    "PAX": (PATH_JAVA, {"te-common-pax", "te-common-utils", "te-payment-core", "te-payment-controller-pax"}),
    "ING": (PATH_CPP, {"IntegraTEC_CppDK", "IntegraTEC_Core", "IntegraTEC_Ingenico"}),
    "SDK": (PATH_CPP, {"IntegraTEC_CppDK", "IntegraTE_ClientSDK_Cpp", "IntegraTE_ClientSDK_Java"}),
}