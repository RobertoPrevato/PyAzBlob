import io


class Scribe:

    @staticmethod
    def read(path):
        with io.open(path, mode="rt", encoding="utf-8") as f:
            s = f.read()
            # go to beginning
            f.seek(0)
        return s

    @staticmethod
    def read_beginning(path, lines):
        with io.open(path, mode="rt", encoding="utf-8") as f:
            s = f.read(lines)
            # go to beginning
            f.seek(0)
        return s

    @staticmethod
    def read_lines(path):
        with io.open(path, mode="rt", encoding="utf-8") as f:
            content = f.readlines()
        return [x[:-1] for x in content]

    @staticmethod
    def write(contents, path):
        with open(path, mode="wt", encoding="utf-8") as f:
            f.truncate()
            f.write(contents)

    @staticmethod
    def write_lines(lines, path):
        with open(path, mode="wt", encoding="utf-8") as f:
            f.writelines([l + "\n" for l in lines])

    @staticmethod
    def add_lines(lines, path):
        with open(path, mode="a+", encoding="utf-8") as f:
            f.writelines([l + "\n" for l in lines])

    @staticmethod
    def add_content(contents, path):
        with open(path, mode="a+", encoding="utf-8") as f:
            f.writelines(contents)
