import pefile

def GetFileVersion(filename: str) -> str:
    pe = pefile.PE(filename)

    if not hasattr(pe, "VS_FIXEDFILEINFO"):
        return None

    ms = pe.VS_FIXEDFILEINFO[0].FileVersionMS
    ls = pe.VS_FIXEDFILEINFO[0].FileVersionLS

    major = ms >> 16
    minor = ms & 0xFFFF
    build = ls >> 16
    revision = ls & 0xFFFF

    return f"{major}.{minor}.{build}.{revision}"
