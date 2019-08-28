# utils.py
#
# Authors:
#   - Coumes Quentin <coumes.quentin@gmail.com>
import os
import subprocess



def command(cmd):
    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True
    )
    out, err = p.communicate()
    if p.returncode:
        raise RuntimeError(
            "Return code : " + str(p.returncode) + " - " + err.decode() + out.decode())
    return p.returncode, out.decode().strip(), err.decode()



def untar_archive():
    archive = os.path.join(os.path.dirname(__file__), "resources/6948902.tgz")
    command("docker cp %s wims:/home/wims/log/classes/" % archive)
    command('docker exec wims bash -c '
            '"tar -xzf /home/wims/log/classes/6948902.tgz -C /home/wims/log/classes/"')
    command('docker exec wims bash -c "chmod 644 /home/wims/log/classes/6948902/.def"')
    command('docker exec wims bash -c "chown wims:wims /home/wims/log/classes/6948902 -R"')
    command('docker exec wims bash -c "rm /home/wims/log/classes/6948902.tgz"')
    command("docker exec wims bash -c "
            "\"echo ':6948902,20200626,Institution,test,en,0,H4,dmi,S S,+myself/myclass+,' "
            '>> /home/wims/log/classes/.index"')
    return 6948902
