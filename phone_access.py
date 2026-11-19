import subprocess
from pathlib import Path

# PHONE DATA ANALYZER
# Works with an Android phone using Android Debug Bridge (ADB).
# Only accesses files that Android makes available to this computer.

OUTPUT = Path.home() / "Phone_Data_Export"
OUTPUT.mkdir(exist_ok=True)


def adb(command):
    result = subprocess.run(
        ["adb"] + command,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print("ADB error:", result.stderr.strip())
        return None
    return result.stdout


def check_connection():
    print("\nChecking phone connection...")
    devices = adb(["devices"])
    if devices and "\tdevice" in devices:
        print(devices)
        print("Phone connected and authorised.")
        return True
    print(devices or "Could not run ADB.")
    print("No authorised phone detected.")
    return False


def phone_information():
    print("\nPHONE INFORMATION")
    for label, prop in [
        ("Manufacturer", "ro.product.manufacturer"),
        ("Model", "ro.product.model"),
        ("Android version", "ro.build.version.release"),
    ]:
        value = adb(["shell", "getprop", prop])
        print(f"{label}: {value.strip() if value else 'Unavailable'}")


def list_storage():
    print("\nACCESSIBLE PHONE STORAGE")
    result = adb(["shell", "ls", "/sdcard/"])
    print(result if result else "Storage listing unavailable.")


def list_whatsapp_media():
    print("\nWHATSAPP MEDIA FOLDERS")
    locations = [
        "/sdcard/Android/media/com.whatsapp/WhatsApp/Media",
        "/sdcard/WhatsApp/Media",
    ]
    found = False
    for location in locations:
        result = adb(["shell", "ls", location])
        if result and "No such file" not in result and "Permission denied" not in result:
            print(f"\n{location}\n{result}")
            found = True
    if not found:
        print("No accessible WhatsApp media folder found.")


def export_whatsapp_media():
    print("\nEXPORTING ACCESSIBLE WHATSAPP MEDIA")
    locations = [
        "/sdcard/Android/media/com.whatsapp/WhatsApp/Media",
        "/sdcard/WhatsApp/Media",
    ]
    for location in locations:
        result = adb(["shell", "ls", location])
        if result and "No such file" not in result and "Permission denied" not in result:
            destination = OUTPUT / "WhatsApp_Media"
            pull = subprocess.run(
                ["adb", "pull", location, str(destination)],
                text=True
            )
            if pull.returncode == 0:
                print(f"Export saved to: {destination}")
            else:
                print("Export did not complete. Check the phone permissions.")
            return
    print("No accessible WhatsApp media folder found.")


def main():
    while True:
        print("\n================================")
        print("        PHONE DATA ANALYZER")
        print("================================")
        print("1. Check phone connection")
        print("2. Show phone information")
        print("3. List accessible storage")
        print("4. List WhatsApp media folders")
        print("5. Export accessible WhatsApp media")
        print("6. Exit")

        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            check_connection()
        elif choice == "2":
            if check_connection():
                phone_information()
        elif choice == "3":
            if check_connection():
                list_storage()
        elif choice == "4":
            if check_connection():
                list_whatsapp_media()
        elif choice == "5":
            if check_connection():
                export_whatsapp_media()
        elif choice == "6":
            print("Closing program.")
            break
        else:
            print("Invalid selection. Choose 1 to 6.")


if __name__ == "__main__":
    main()
