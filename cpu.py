"""CPU functionality."""

import sys

# branch table key values
HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.SP = 7
        self.running = False
        # branch table
        self.branchtable = {}
        self.branchtable[HLT] = self.handle_hlt
        self.branchtable[LDI] = self.handle_ldi
        self.branchtable[PRN] = self.handle_pri
        self.branchtable[MUL] = self.handle_mul
        self.branchtable[PUSH] = self.handle_push
        self.branchtable[POP] = self.handle_pop

    def load(self):
        """Load a program into memory."""
        # Needs 2 file names (comp.py & program file name)...if not, print error
        if len(sys.argv) != 2:
            print("usage: comp.py filename")
            sys.exit(1)

        try:
            address = 0

            with open(sys.argv[1]) as f:
                # sanitize data from file
                for line in f:
                    t = line.split('#')
                    n = t[0].strip()

                    if n == '':
                        continue

                    try:
                        n = int(n, 2)
                    except ValueError:
                        print(f"Invalid number: {n}")
                        sys.exit(1)

                    # commit program data to memory
                    self.ram[address] = n
                    address += 1

        # If program file name not found/valid, print error
        except FileNotFoundError:
            print(f"File not found: {sys.argv[1]}")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    # MAR = memory address register <-- address being read
    def ram_read(self, MAR):
        MDR = self.ram[MAR]
        return MDR

    # MAR <-- address being written tO; MDR = memory data register <-- data being written to address
    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    # HLT INSTRUCTION: Halt CPU & exit emulator
    def handle_hlt(self, a, b):
        self.running = False

    # LDI INSTRUCTION: Set value of register to an integer
    def handle_ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b

    # PRN INSTRUCTION: print numeric value stored in given register
    def handle_pri(self, operand_a, operand_b):
        print(f"Value at register {operand_a}: {self.reg[operand_a]}")

    # MUL INSTRUCITON: Multiply values in 2 registers together & store result in registerA
    def handle_mul(self, reg_a, reg_b):
        self.alu("MUL", reg_a, reg_b)

    # PUSH INSTRUCTION: Push the value in the given register on the stack
    def handle_push(self, operand_a, operand_b):
        # decrement SP
        self.reg[self.SP] -= 1

        # get value to push...operand_a is reg num to push
        value = self.reg[operand_a]

        # copy value to SP address
        self.ram[self.reg[self.SP]] = value

    # POP INSTRUCTION: Pop the value at the top of the stack into the given register
    def handle_pop(self, operand_a, operand_b):
        # get value at top of stack address
        value = self.ram[self.reg[self.SP]]

        # store value in the register (reg num to pop into is operand_a)
        self.reg[operand_a] = value

        # increment SP
        self.reg[self.SP] += 1

    def run(self):
        """Run the CPU."""
        # initialize stack pointer
        self.reg[self.SP] = 0xF4

        # set running to True
        self.running = True

        # Iterate thru
        while self.running:
            # set instruction register
            ir = self.ram_read(self.pc)

            # find num of operands (use to dynamically set pc incrementation)
            operand_count = (ir & 0b11000000) >> 6
            increment_num = operand_count + 1

            op_a = self.ram_read(self.pc+1)
            op_b = self.ram_read(self.pc+2)

            # use branchtable to complete corresponding instruction
            self.branchtable[ir](op_a, op_b)

            # increment pc
            self.pc += increment_num

# python ls8.py examples/and.ls8
# python ls8.py examples/call.ls8
# python ls8.py examples/interrupts.ls8
# python ls8.py examples/keyboard.ls8
# python ls8.py examples/mult.ls8 ✅
# python ls8.py examples/or.ls8
# python ls8.py examples/print8.ls8 ✅
# python ls8.py examples/printstr.ls8
# python ls8.py examples/sctest.ls8
# python ls8.py examples/stack.ls8 ✅
# python ls8.py examples/stackoverflow.ls8
# python ls8.py examples/xor.ls8
