import os

# https://synaptics-astra.github.io/doc/v/1.3.0/subject/gpios.html
# GPIO[36] is located on the 40 pin connectors on SL1640 and SL1680. GPIO[36] maps to GPIO number 484 based on the table below GPIO Mappings.

# Once the GPIO has been exported, the value and direction can be viewed and set:

# root@sl1680:~# cd /sys/class/gpio/
# root@sl1680:/sys/class/gpio/gpio484# cat direction
# in
# root@sl1680:/sys/class/gpio/gpio484# cat value
# 0
# By default, GPIO[36] is set to input with the value 0. To changes these value, write to the corresponding sysfs file:

# root@sl1680:/sys/class/gpio/gpio484# echo "out" > direction
# root@sl1680:/sys/class/gpio/gpio484# cat direction
# out
# root@sl1680:/sys/class/gpio/gpio484# echo 1 > value
# root@sl1680:/sys/class/gpio/gpio484# cat value

import os
import argparse


def gpio_write(gpio_number, direction, value):
    gpio_path = f"/sys/class/gpio/gpio{gpio_number}"

    # Check if GPIO is already exported
    if not os.path.exists(gpio_path):
        # Export the GPIO
        with open("/sys/class/gpio/export", "w") as f:
            f.write(str(gpio_number))

    # Set the GPIO direction
    with open(os.path.join(gpio_path, "direction"), "w") as f:
        f.write(direction)

    # Write the value to the GPIO
    with open(os.path.join(gpio_path, "value"), "w") as f:
        f.write(str(value))


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Control GPIO pin")

    # Add arguments for GPIO number, direction, and value
    parser.add_argument("gpio_number", type=int, help="GPIO pin number")
    parser.add_argument(
        "direction", choices=["in", "out"], help="GPIO direction (in or out)"
    )
    parser.add_argument("value", type=int, choices=[0, 1], help="GPIO value (0 or 1)")

    # Parse arguments
    args = parser.parse_args()

    # Call the gpio_write function with parsed arguments
    gpio_write(args.gpio_number, args.direction, args.value)


if __name__ == "__main__":
    main()
