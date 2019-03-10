import os
import subprocess


def convert_one(source):
    target = source.replace('.ui', '.py')

    subprocess.run(['pyuic5', source,
                    '-o', target])


def convert_all():
    ui_dir = 'qt\\UI\\'
    for file in os.listdir(ui_dir):
        if file.endswith('.ui'):
            convert_one(os.path.join(ui_dir, file))


if __name__ == '__main__':
    convert_all()