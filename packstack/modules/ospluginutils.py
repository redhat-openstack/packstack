# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import os
import yaml

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography import x509
from cryptography.x509 import oid

from packstack.installer import basedefs
from packstack.installer import utils
from packstack.installer.setup_controller import Controller

controller = Controller()

PUPPET_DIR = os.path.join(basedefs.DIR_PROJECT_DIR, "puppet")
PUPPET_TEMPLATE_DIR = os.path.join(PUPPET_DIR, "templates")
HIERA_COMMON_YAML = os.path.join(basedefs.HIERADATA_DIR, "common.yaml")
# For compatibility with hiera < 3.0
HIERA_DEFAULTS_YAML = os.path.join(basedefs.HIERADATA_DIR, "defaults.yaml")


class ManifestFiles(object):
    def __init__(self):
        self.filelist = []
        self.data = {}

    # continuous manifest file that have the same marker can be
    # installed in parallel, if on different servers
    def addFile(self, filename, marker, data=''):
        self.data[filename] = self.data.get(filename, '') + '\n' + data
        for f, p in self.filelist:
            if f == filename:
                return

        self.filelist.append((filename, marker))

    def prependFile(self, filename, marker, data=''):
        self.data[filename] = data + '\n' + self.data.get(filename, '')
        for f, p in self.filelist:
            if f == filename:
                return

        self.filelist.append((filename, marker))

    def getFiles(self):
        return [f for f in self.filelist]

    def writeManifests(self):
        """
        Write out the manifest data to disk, this should only be called once
        write before the puppet manifests are copied to the various servers
        """
        os.mkdir(basedefs.PUPPET_MANIFEST_DIR, 0o700)
        for fname, data in self.data.items():
            path = os.path.join(basedefs.PUPPET_MANIFEST_DIR, fname)
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, 'w') as fp:
                fp.write(data)


manifestfiles = ManifestFiles()


def getManifestTemplate(template_name):
    if not template_name.endswith(".pp"):
        template_name += ".pp"
    with open(os.path.join(PUPPET_TEMPLATE_DIR, template_name)) as fp:
        return fp.read() % controller.CONF


def appendManifestFile(manifest_name, data, marker=''):
    manifestfiles.addFile(manifest_name, marker, data)


def generateHieraDataFile():
    os.mkdir(basedefs.HIERADATA_DIR, 0o700)
    with open(HIERA_COMMON_YAML, 'w') as outfile:
        outfile.write(yaml.dump(controller.CONF,
                                explicit_start=True,
                                default_flow_style=False))
    os.symlink(os.path.basename(HIERA_COMMON_YAML), HIERA_DEFAULTS_YAML)


def generate_ssl_cert(config, host, service, ssl_key_file, ssl_cert_file):
    """
    Generate SSL certificate
    """
    # We have to check whether the certificate already exists
    cert_dir = os.path.join(config['CONFIG_SSL_CERT_DIR'], 'certs')
    local_cert_name = host + os.path.basename(ssl_cert_file)
    local_cert_path = os.path.join(cert_dir, local_cert_name)
    if os.path.exists(local_cert_path):
        return

    with open(config['CONFIG_SSL_CACERT_FILE'], 'rb') as cacert_file:
        ca_cert = x509.load_pem_x509_certificate(cacert_file.read())

    with open(config['CONFIG_SSL_CACERT_KEY_FILE'], 'rb') as ca_key_file:
        ca_key = serialization.load_pem_private_key(ca_key_file.read(),
                                                    password=None)

    # create a key pair
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )

    hostinfo = config['HOST_DETAILS'][host]
    fqdn = hostinfo['fqdn']
    cn = "%s/%s" % (service, fqdn)
    # if subject.CN is more than 64 chars long, cert creation will fail
    if len(cn) > 64:
        cn = cn[0:63]

    subject = x509.Name([
        x509.NameAttribute(oid.NameOID.COUNTRY_NAME,
                           config['CONFIG_SSL_CERT_SUBJECT_C']),
        x509.NameAttribute(oid.NameOID.STATE_OR_PROVINCE_NAME,
                           config['CONFIG_SSL_CERT_SUBJECT_ST']),
        x509.NameAttribute(oid.NameOID.LOCALITY_NAME,
                           config['CONFIG_SSL_CERT_SUBJECT_L']),
        x509.NameAttribute(oid.NameOID. ORGANIZATION_NAME,
                           config['CONFIG_SSL_CERT_SUBJECT_O']),
        x509.NameAttribute(oid.NameOID. ORGANIZATIONAL_UNIT_NAME,
                           config['CONFIG_SSL_CERT_SUBJECT_OU']),
        x509.NameAttribute(oid.NameOID.COMMON_NAME, cn),
        x509.NameAttribute(oid.NameOID.EMAIL_ADDRESS,
                           config['CONFIG_SSL_CERT_SUBJECT_MAIL']),
    ])
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        ca_cert.subject
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.now(datetime.timezone.utc)
    ).not_valid_after(
        datetime.datetime.now(datetime.timezone.utc) +
        datetime.timedelta(days=3650)
    ).add_extension(
        x509.KeyUsage(
            digital_signature=True,
            content_commitment=True,
            key_encipherment=True,
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=False,
            crl_sign=False,
            encipher_only=False,
            decipher_only=False,
        ),
        critical=False,
    ).add_extension(
        x509.ExtendedKeyUsage([
            x509.ExtendedKeyUsageOID.CLIENT_AUTH,
            x509.ExtendedKeyUsageOID.SERVER_AUTH,
        ]),
        critical=False,
    ).sign(ca_key, hashes.SHA256())

    final_cacert = ca_cert.public_bytes(serialization.Encoding.PEM)
    final_cert = cert.public_bytes(serialization.Encoding.PEM)
    final_key = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    deliver_ssl_file(final_cacert.decode(), config['CONFIG_SSL_CACERT'], host)
    deliver_ssl_file(final_cert.decode(), ssl_cert_file, host)
    deliver_ssl_file(final_key.decode(), ssl_key_file, host)

    with open(local_cert_path, 'wb') as f:
        f.write(final_cert)


def deliver_ssl_file(content, path, host):
    server = utils.ScriptRunner(host)
    server.append("grep -- '{content}' {path} || "
                  "echo '{content}' > {path} ".format(
                      content=content,
                      path=path))
    server.execute()


def gethostlist(CONF):
    hosts = []
    for key, value in CONF.items():
        if key.endswith("_HOST"):
            value = value.split('/')[0]
            if value and value not in hosts:
                hosts.append(value)
        if key.endswith("_HOSTS"):
            for host in value.split(","):
                host = host.strip()
                host = host.split('/')[0]
                if host and host not in hosts:
                    hosts.append(host)
    return hosts
