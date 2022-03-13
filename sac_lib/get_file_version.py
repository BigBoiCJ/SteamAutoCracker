import win32api

def GetFileVersion(filename: str) -> str:
    fileInfos = win32api.GetFileVersionInfo(filename, "\\")
    return "%d.%d.%d.%d" % (fileInfos['FileVersionMS'] / 65536, fileInfos['FileVersionMS'] % 65536, fileInfos['FileVersionLS'] / 65536, fileInfos['FileVersionLS'] % 65536)