"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.registers = [0] * 8
        self.memory = [0] * 256
        self.pc = 0
        self.machine_codes = {
            "HLT": 0b00000001,
            "LDI": 0b10000010,
            "PRN": 0b01000111,
            "MUL": 0b10100010,  # MUL R0,R1
            "SUB": 0b10100001,  # SUB R0, R1
        }

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]
        # for instruction in program:
        #     self.memory[address] = instruction
        #     address += 1

        if len(sys.argv) != 2:
            print("usage: cPU.py progname")
            sys.exit(1)
        try:
            with open(sys.argv[1], "r") as program:
                for instruction in program:
                    # print(instruction)
                    if "#" in instruction:
                        instruction = instruction.split()[0]
                        if instruction == "#":
                            continue
                    else:
                        instruction = instruction.replace("\n", "")
                    self.memory[address] = int(instruction, 2)
                    address += 1
        except FileNotFoundError:
            print(f"Couldn't open {sys.argv[1]}")
            sys.exit(2)

            if address == 0:
                print("Program was empty")
                sys.exit(3)

    def ram_read(self, idx):
        return self.memory[idx]

    def ram_write(self, idx, user_input):
        self.memory[idx] = user_input

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.registers[reg_a] += self.registers[reg_b]
        elif op == "SUB":
            self.registers[reg_a] -= self.registers[reg_b]
        elif op == "MUL":
            self.registers[reg_a] *= self.registers[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(
            f"TRACE: %02X | %02X %02X %02X |"
            % (
                self.pc,
                # self.fl,
                # self.ie,
                self.ram_read(self.pc),
                self.ram_read(self.pc + 1),
                self.ram_read(self.pc + 2),
            ),
            end="",
        )

        for i in range(8):
            print(" %02X" % self.registers[i], end="")

        print()

    def run(self):
        """Run the CPU."""
        running = True
        while running:
            ir = self.ram_read(self.pc)

            if ir == self.machine_codes["HLT"]:  # HLT
                # shuts off program
                running = False
                self.pc += 1

            elif ir == self.machine_codes["PRN"]:  # PRINT_REG
                reg_num = self.memory[self.pc + 1]
                print(self.registers[reg_num])
                self.pc += 2

            elif ir == self.machine_codes["LDI"]:
                reg_num = self.memory[self.pc + 1]
                val = self.memory[self.pc + 2]
                self.registers[reg_num] = val
                self.pc += 3
            elif ir == self.machine_codes["MUL"]:
                reg_num1 = self.memory[self.pc + 1]
                reg_num2 = self.memory[self.pc + 2]
                self.alu("MUL", reg_num1, reg_num2)
                self.pc += 3
            elif ir == self.machine_codes["SUB"]:
                reg_num1 = self.memory[self.pc + 1]
                reg_num2 = self.memory[self.pc + 2]
                self.alu("SUB", reg_num1, reg_num2)
                self.pc += 3
        # self.trace()
