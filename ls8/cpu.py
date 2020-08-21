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
            "ADD": 0b10100000,
            "MUL": 0b10100010,  # MUL R0,R1
            "SUB": 0b10100001,  # SUB R0, R1
            "PUSH": 0b01000101,
            "POP": 0b01000110,
            "CALL": 0b01010000,
            "RET": 0b00010001,
            "CMP": 0b10100111,
            "JMP": 0b01010100,
            "JEQ": 0b01010101,
            "JNE": 0b01010110,
            "AND": 0b10101000,
            "OR": 0b10101010,
            "XOR": 0b10101011,
            "NOT": 0b01101001,
            "SHL": 0b10101100,
            "SHR": 0b10101101,
            "MOD": 0b10100100,
        }
        self.sp = 7  # from LS8 spec
        self.flags = 0

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
        elif op == "CMP":
            if self.registers[reg_a] < self.registers[reg_b]:
                self.flags = 0b00000100  # L in binary (less than)
            elif self.registers[reg_a] > self.registers[reg_b]:
                self.flags = 0b00000010  # G in binary (greater than)
            else:
                self.flags = 0b00000001  # E in binary (equal)
        elif op == "AND":
            self.registers[reg_a] &= self.registers[reg_b]
        elif op == "OR":
            self.registers[reg_a] |= self.registers[reg_b]
        elif op == "XOR":
            self.registers[reg_a] ^= self.registers[reg_b]
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
            elif ir == self.machine_codes["ADD"]:
                reg_slot_1 = self.memory[self.pc + 1]
                reg_slot_2 = self.memory[self.pc + 2]
                self.alu("ADD", reg_slot_1, reg_slot_2)
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
            elif ir == self.machine_codes["PUSH"]:
                # decrement sp
                self.registers[self.sp] -= 1

                # get val from register
                reg_num = self.memory[self.pc + 1]
                value = self.registers[reg_num]

                # store it on the stack
                top_of_stack_address = self.registers[self.sp]
                self.memory[top_of_stack_address] = value

                self.pc += 2

            elif ir == self.machine_codes["POP"]:
                value_addr = self.registers[self.sp]
                value = self.memory[value_addr]
                reg_num = self.memory[self.pc + 1]
                self.registers[reg_num] = value
                self.registers[self.sp] += 1
                self.pc += 2

            elif ir == self.machine_codes["CALL"]:
                self.registers[self.sp] -= 1
                return_address = self.pc + 2
                value_address = self.registers[self.sp]
                self.memory[value_address] = return_address
                reg_num = self.memory[self.pc + 1]
                subroutine_address = self.registers[reg_num]
                self.pc = subroutine_address

            elif ir == self.machine_codes["RET"]:
                value_address = self.registers[self.sp]
                return_address = self.memory[value_address]
                self.registers[self.sp] += 1
                self.pc = return_address

            elif ir == self.machine_codes["CMP"]:
                reg_num1 = self.memory[self.pc + 1]
                reg_num2 = self.memory[self.pc + 2]
                self.alu("CMP", reg_num1, reg_num2)
                self.pc += 3

            elif ir == self.machine_codes["JMP"]:
                reg_num = self.memory[self.pc + 1]
                self.pc = self.registers[reg_num]

            elif ir == self.machine_codes["JEQ"]:
                reg_num = self.memory[self.pc + 1]
                if self.flags == 0b00000001:  # E in binary (equal)
                    self.pc = self.registers[reg_num]
                else:
                    self.pc += 2
            elif ir == self.machine_codes["JNE"]:
                reg_num = self.memory[self.pc + 1]
                if self.flags != 0b00000001:  # E in binary this shows they are unequal!
                    self.pc = self.registers[reg_num]
                else:
                    self.pc += 2
            elif ir == self.machine_codes["AND"]:
                reg_num1 = self.memory[self.pc + 1]
                reg_num2 = self.memory[self.pc + 2]
                self.alu("AND", reg_num1, reg_num2)
                self.pc += 3
            elif ir == self.machine_codes["OR"]:
                reg_num1 = self.memory[self.pc + 1]
                reg_num2 = self.memory[self.pc + 2]
                self.alu("OR", reg_num1, reg_num2)
                self.pc += 3
            elif ir == self.machine_codes["XOR"]:
                reg_num1 = self.memory[self.pc + 1]
                reg_num2 = self.memory[self.pc + 2]
                self.alu("XOR", reg_num1, reg_num2)
                self.pc += 3

        self.trace()
