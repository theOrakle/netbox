import os
import paramiko
from netbox_dns.models import *
from extras.scripts import Script

class nameserver(Script):

  class Meta:
    name = "Update"
    description = "Push A and CNAME records to nameservers"
    
  def write(self,path):
    output.append("Wrote Files :")
    recs = Record.objects.filter(type="A")
    f = open(f"{path}/hosts", "w")
    for rec in recs:
      f.write(f"{rec.value}\t\t{rec.name}.{rec.zone.name}\n")
    f.close()
    output.append(f'\t{len(recs)} A records')
    recs = Record.objects.filter(type="CNAME")
    f = open(f"{path}/cname.conf", "w")
    for rec in recs:
      zone=rec.zone.name
      f.write(f"cname={rec.name}.{zone},{rec.value}\n")
    f.close()
    output.append(f'\t{len(recs)} CNAME records')

  def push(self,path):
    ns = NameServer.objects.all()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for server in ns:
      output.append(f"Updating {server} :")
      ssh.connect(f"{server}", username="root")
      sftp = ssh.open_sftp()
      sftp.put(f"{path}/cname.conf", f"/opt/dnsmasq/cname.conf")
      output.append('\tcname.conf')
      sftp.put(f"{path}/hosts", f"/opt/dnsmasq/hosts")
      output.append('\thosts')
      sftp.close()
    ssh.close()

  def run(self, data, commit):
    global output
    #conf=self.load_yaml("config.yaml")
    output = []
    path = f"{os.path.dirname(os.path.abspath(__file__))}/output"
    if not os.path.exists(path):
      os.makedirs(path)
      output.append('Created output directory')
    self.write(path)
    self.push(path)
    return '\n'.join(output)