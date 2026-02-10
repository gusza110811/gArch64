import sys
from collections import deque

class Converter:
    def __init__(self):
        self.running = False
    
    def main(self, source:str=None):
        self.running = True

        output = ""

        do_stdio = source == None

        if source:
            source = deque(source.splitlines(keepends=True))

        while self.running:
            if do_stdio:
                try:
                    liner = input()+"\n"
                except EOFError:
                    self.running = False
                    break
            else:
                try:
                    liner = source.popleft()
                except IndexError:
                    self.running = False
                    break

            line, *comments = liner.split(";")

            whitesp = len(line) - len(line.lstrip())
            line = line.strip()

            if len(line) == 0:
                output += liner
                continue # skip blank lines

            if line.endswith(":"):
                output += liner
                continue # skip label def
            if line.startswith("const"):
                output += liner
                continue # skip constants def
            if line.startswith("."):
                output += liner
                continue # skip dot directives

            command, *argsp = line.split()

            args = " ".join(argsp).split(",")
            nargs = []

            if argsp:
                for arg in args:
                    arg = arg.strip()

                    if arg.startswith("$") or arg.startswith("%"):
                        nargs.append(arg[1:])
                    else:
                        nargs.append("["+arg+"]")
            
            new = " "*whitesp+command+" "+ ", ".join(nargs) + (f" ;{";".join(comments)}" if comments else "") + "\n"

            output += new
        if do_stdio:
            sys.stdout.write(output)
        else:
            return output

if __name__ == "__main__":
    converter = Converter()

    if len(sys.argv) > 1:
        for target in sys.argv[1:]:
            print(target,file=sys.stderr,end=": ")
            try:
                with open(target,"r+") as file:
                    out = converter.main(file.read())
                    file.truncate(0)
                    file.seek(0)
                    file.write(out)
                print("Done",file=sys.stderr)
            except FileNotFoundError:
                print("Not found",file=sys.stderr)
            except UnicodeDecodeError:
                print("Not a valid UTF-8 file",file=sys.stderr)
    else:
        converter.main()