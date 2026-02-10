from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

APP_NAME = "IshKundaligi"
ENTRYPOINT = Path("kundalik_gui.py")
DIST_DIR = Path("dist")
BUILD_DIR = Path("build")
ICON_PATH = Path("app.ico")


def run(command: list[str]) -> None:
    print("[RUN]", " ".join(command))
    subprocess.run(command, check=True)


def ensure_pyinstaller() -> str:
    pyinstaller = shutil.which("pyinstaller")
    if pyinstaller:
        return pyinstaller

    print("PyInstaller topilmadi. Quyidagilarni bajaring:")
    print("  python -m pip install -r requirements.txt")
    raise SystemExit(1)


def build_exe(pyinstaller_path: str) -> Path:
    if not ENTRYPOINT.exists():
        print(f"Xato: {ENTRYPOINT} topilmadi")
        raise SystemExit(1)

    command = [
        pyinstaller_path,
        "--noconfirm",
        "--clean",
        "--name",
        APP_NAME,
        "--windowed",
        str(ENTRYPOINT),
    ]

    if ICON_PATH.exists():
        command.extend(["--icon", str(ICON_PATH)])

    run(command)

    exe_path = DIST_DIR / APP_NAME / f"{APP_NAME}.exe"
    if not exe_path.exists():
        print(f"Xato: EXE yaratilmagan ({exe_path})")
        raise SystemExit(1)

    return exe_path


def write_inno_setup_script(exe_path: Path) -> Path:
    installer_dir = Path("installer")
    installer_dir.mkdir(exist_ok=True)
    iss_path = installer_dir / "kundalik_installer.iss"

    app_dir = exe_path.parent.resolve()

    iss_content = f'''#define MyAppName "Ish Kundaligi"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Local"
#define MyAppExeName "{APP_NAME}.exe"

[Setup]
AppId={{{{D6BBAF03-DC3D-4A57-B68D-E458A3C32E17}}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
DefaultDirName={{autopf}}\\{{#MyAppName}}
DefaultGroupName={{#MyAppName}}
DisableProgramGroupPage=yes
OutputDir=..\\dist
OutputBaseFilename=IshKundaligiSetup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Files]
Source: "{app_dir}\\*"; DestDir: "{{app}}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{{autoprograms}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"
Name: "{{autodesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\{{#MyAppExeName}}"; Description: "Launch {{#MyAppName}}"; Flags: nowait postinstall skipifsilent
'''

    iss_path.write_text(iss_content, encoding="utf-8")
    return iss_path


def main() -> None:
    pyinstaller_path = ensure_pyinstaller()
    exe_path = build_exe(pyinstaller_path)
    iss_path = write_inno_setup_script(exe_path)

    print("\n✅ Tayyor:")
    print(f"- EXE: {exe_path}")
    print(f"- Inno Setup script: {iss_path}")
    print("\nInstaller yaratish uchun:")
    print("1) Inno Setup o'rnating: https://jrsoftware.org/isinfo.php")
    print(f"2) {iss_path} faylini Inno Setup bilan ochib Compile qiling")


if __name__ == "__main__":
    main()
