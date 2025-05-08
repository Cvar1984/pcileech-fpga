import os

def read_config_space(device_path):
    try:
        with open(os.path.join(device_path, 'config'), 'rb') as f:
            return f.read(4096)
    except:
        return None

def extract_bytes(blob, offset, length):
    return blob[offset:offset+length]

def print_hex(label, data):
    if data:
        print(f"{label}: {' '.join(f'{b:02X}' for b in data)}")
    else:
        print(f"{label}: (not present)")

def main(vendor_id_hex, device_id_hex=None):
    base_paths = ["/sys/bus/pci/devices", "/sys/bus/pci_express/devices"]
    vendor_id = int(vendor_id_hex, 16)
    device_id = int(device_id_hex, 16) if device_id_hex else None

    seen = set()

    for base_path in base_paths:
        if not os.path.exists(base_path):
            continue
        for dev in os.listdir(base_path):
            if dev in seen:
                continue  # skip duplicates
            seen.add(dev)

            dev_path = os.path.join(base_path, dev)
            try:
                with open(os.path.join(dev_path, 'vendor')) as f:
                    v = int(f.read().strip(), 16)
                with open(os.path.join(dev_path, 'device')) as f:
                    d = int(f.read().strip(), 16)
            except:
                continue

            if v == vendor_id and (device_id is None or d == device_id):
                print(f"\n✅ Found matching device at: {dev}")
                blob = read_config_space(dev_path)
                if not blob:
                    print("Failed to read config space.")
                    return

                print_hex("Vendor ID", extract_bytes(blob, 0x00, 2))
                print_hex("Device ID", extract_bytes(blob, 0x02, 2))
                print_hex("RevID", extract_bytes(blob, 0x08, 1))
                print_hex("BAR0", extract_bytes(blob, 0x10, 4))
                print_hex("Subsystem ID", extract_bytes(blob, 0x2E, 2))
                print_hex("Serial Number Register (Lower DW)", extract_bytes(blob, 0x44, 4))
                print_hex("Serial Number Register (Upper DW)", extract_bytes(blob, 0x48, 4))
                return

    print("❌ No matching PCI(e) device found.")
    print("Try lspci -nn")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: sudo python3 pci_extractor.py <vendor_id_hex> [device_id_hex]")
        print("Example: sudo python3 pci_extractor.py 10EC 6816")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)

