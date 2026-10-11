import serial
import time

PORT = "COM9"
BAUD_RATES = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
TIMEOUT = 1.0

def try_baud(port, baud):
    try:
        with serial.Serial(port=port, baudrate=baud, timeout=TIMEOUT) as ser:
            # Give device time after opening port
            time.sleep(2)

            # Clear buffers
            ser.reset_input_buffer()
            ser.reset_output_buffer()

            # Optional probe: send newline (common for CLI-style firmware)
            ser.write(b"\r\n")
            time.sleep(0.3)

            data = ser.read(200)
            if data:
                text = data.decode(errors="replace").strip()
                print(f"[+] Baud {baud}: RECEIVED -> {repr(text)}")
                return True
            else:
                print(f"[-] Baud {baud}: no data")
                return False

    except serial.SerialException as e:
        print(f"[!] Baud {baud}: serial error -> {e}")
        return False

def main():
    print(f"Testing {PORT} with common baud rates...\n")
    found = []

    for baud in BAUD_RATES:
        ok = try_baud(PORT, baud)
        if ok:
            found.append(baud)

    print("\nDone.")
    if found:
        print("Possible working baud rates:", found)
    else:
        print("No response detected. Check device mode, cable, driver, and COM port.")

if __name__ == "__main__":
    main()