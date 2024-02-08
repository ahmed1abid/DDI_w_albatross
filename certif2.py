
import socket
import ssl
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat._oid import ObjectIdentifier as NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime

import subprocess


class Certif:

    @staticmethod
    def generate_ca():
        # Generate the root CA private key
        root_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        # Generate the root CA certificate
        root_cert = (
            x509.CertificateBuilder()
            .subject_name(x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME, u"Root CA")]))
            .issuer_name(x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME, u"Root CA")]))
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
            .serial_number(x509.random_serial_number())
            .public_key(root_key.public_key())
            .sign(root_key, hashes.SHA256(), default_backend())
        )

        # Save the root CA private key
        with open("key/ca.key", "wb") as key_file:
            key_file.write(root_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

        # Save the root CA certificate
        with open("key/cacert.pem", "wb") as cert_file:
            cert_file.write(root_cert.public_bytes(serialization.Encoding.PEM))

        # Generate the unipi private key
        server_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        # Generate the unipi certificate
        server_cert = (
            x509.CertificateBuilder()
            .subject_name(x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME, u"Server")]))
            .issuer_name(x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME, u"Root CA")]))
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
            .serial_number(x509.random_serial_number())
            .public_key(server_key.public_key())
            .sign(root_key, hashes.SHA256(), default_backend())
        )

        # Save the unipi private key
        with open("key/unipi.key", "wb") as key_file:
            key_file.write(server_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

        # Save the unipi certificate
        with open("key/unipi.pem", "wb") as cert_file:
            cert_file.write(server_cert.public_bytes(serialization.Encoding.PEM))


    # def start_tls_endpoint( ./key/cacert.pem, ./key/unipi.pem, ./key/unipi.key, listen_address, listen_port):
    #     # Load CA certificate
    #     with open( ./key/cacert.pem, 'rb') as ca_cert_file:
    #         ca_cert_data = ca_cert_file.read()

    #     # Load unipi certificate and private key
    #     with open(./key/unipi.pem, 'rb') as server_cert_file:
    #         server_cert_data = server_cert_file.read()

    #     with open(./key/unipi.key, 'rb') as server_key_file:
    #         server_key_data = server_key_file.read()

    #     # Create a TLS context
    #     context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    #     context.load_verify_locations(cafile=None, cadata=ca_cert_data)
    #     context.load_cert_chain(certfile=./key/unipi.pem, keyfile=./key/unipi.key)

    #     # Create a socket
    #     server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     server_socket.bind((listen_address, listen_port))
    #     server_socket.listen(5)

    #     print(f"Listening on {listen_address}:{listen_port}...")

    #     while True:
    #         client_socket, client_address = server_socket.accept()
    #         print(f"Accepted connection from {client_address}")

    #         # Wrap the socket in a TLS context
    #         secure_socket = context.wrap_socket(client_socket, server_side=True)


    def client_create_unikernel_csr():
    # Generate a key pair for the unikernel
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        # Create a certificate signing request (CSR)
        csr = (
            x509.CertificateSigningRequestBuilder()
            .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, u"Unipi")]))
            .sign(key, hashes.SHA256(), default_backend())
        )

        # Save the private key
        with open("key/unipi.key", "wb") as key_file:
            key_file.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            ))

        # Save the CSR
        with open("key/unipi.req", "wb") as csr_file:
            csr_file.write(csr.public_bytes(serialization.Encoding.PEM))


    def intermediate_ca_sign_request():
        # Load the intermediate CA private key
        with open("key/ca.key", "rb") as key_file:
            ca_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend(),
            )

        # Load the user key
        with open("key/unipi.key", "rb") as key_file:
            user_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend(),
            )

        # Load the user CSR
        with open("key/unipi.req", "rb") as csr_file:
            user_csr = x509.load_pem_x509_csr(
                csr_file.read(),
                default_backend(),
            )

        # Sign the user CSR
        user_cert = (
            x509.CertificateBuilder()
            .subject_name(user_csr.subject)
            .issuer_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, u"Intermediate CA")]))
            .public_key(user_csr.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
            .sign(ca_key, hashes.SHA256(), default_backend())
        )

        # Save the signed user certificate
        with open("key/unipi.pem", "wb") as cert_file:
            cert_file.write(user_cert.public_bytes(serialization.Encoding.PEM))
        # # Add other functions as needed




    def client_send_signed_request_to_server():
        # Load the intermediate CA certificate
        with open("key/intermediate_ca.pem", "rb") as cert_file:
            intermediate_ca_cert = x509.load_pem_x509_certificate(
                cert_file.read(),
                default_backend(),
            )

        # Load the signed user certificate
        with open("key/unipi.pem", "rb") as cert_file:
            user_cert = x509.load_pem_x509_certificate(
                cert_file.read(),
                default_backend(),
            )

        # Create the full chain
        full_chain = (
            user_cert.public_bytes(serialization.Encoding.PEM) +
            intermediate_ca_cert.public_bytes(serialization.Encoding.PEM)
        )

        # Save the full chain
        with open("unipi_full_chain.pem", "wb") as full_chain_file:
            full_chain_file.write(full_chain)

        # Perform additional actions (e.g., send to the unipi)
        server_address = ("10.0.0.254", 8443)  # Change this to your unipi's IP and port

        with socket.create_connection(server_address) as s:
            # Upgrade the socket to a TLS connection
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            with context.wrap_socket(s, server_hostname=server_address[0]) as tls_socket:
                tls_socket.sendall(full_chain)


    def user_add_policy():
        # Generate a user key pair
        user_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        # Generate a signing request for the user
        user_req = (
            x509.CertificateSigningRequestBuilder()
            .subject_name(x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME, u"User")]))
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
            .sign(user_key, hashes.SHA256(), default_backend())
        )

        # Save the user key pair
        with open("key/user.key", "wb") as key_file:
            key_file.write(user_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))

        # Save the user signing request
        with open("key/user.req", "wb") as req_file:
            req_file.write(user_req.public_bytes(serialization.Encoding.PEM))


    def ca_sign_user_request():
        # Load the CA private key
        with open("key/ca.key", "rb") as key_file:
            ca_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None,
                backend=default_backend()
            )

        # Load the user signing request
        with open("user.req", "rb") as req_file:
            user_req = x509.load_pem_x509_csr(req_file.read(), default_backend())

        # Sign the user request
        user_cert = (
            x509.CertificateBuilder()
            .subject_name(user_req.subject)
            .issuer_name(x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME, u"Root CA")]))
            .public_key(user_req.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
            .sign(ca_key, hashes.SHA256(), default_backend())
        )

        # Save the signed user certificate
        with open("user.pem", "wb") as cert_file:
            cert_file.write(user_cert.public_bytes(serialization.Encoding.PEM))



    # def sign_certificate_request(cacert_path, key_path, csr_path, days=365):
    #     # Load the CA certificate
    #     with open(cacert_path, 'rb') as f:
    #         ca_cert = x509.load_pem_x509_certificate(f.read(), default_backend())

    #     # Load the private key
    #     with open(key_path, 'rb') as f:
    #         private_key = serialization.load_pem_private_key(
    #             f.read(),
    #             password=None,  # No password protection for the private key
    #             backend=default_backend()
    #         )

    #     # Load the signing request
    #     with open(csr_path, 'rb') as f:
    #         csr = x509.load_pem_x509_csr(f.read(), default_backend())

    #     # Set the validity period for the signed certificate
    #     not_valid_before = datetime.datetime.utcnow()
    #     not_valid_after = not_valid_before + datetime.timedelta(days=days)

    #     # Build the signed certificate
    #     signed_cert = (
    #         x509.CertificateBuilder()
    #         .subject_name(csr.subject)
    #         .issuer_name(ca_cert.issuer)
    #         .public_key(csr.public_key())
    #         .serial_number(x509.random_serial_number())
    #         .not_valid_before(not_valid_before)
    #         .not_valid_after(not_valid_after)
    #         .sign(private_key, hashes.SHA256(), default_backend())
    #     )

    #     # Save the signed certificate
    #     print("creatin on the way ")
    #     with open(".key/signed_cert.pem", "wb") as cert_file:
    #         cert_file.write(signed_cert.public_bytes(serialization.Encoding.PEM))
    
    
    def server_start_endpoint():
            subprocess.run(["sudo","/home/ahmed/.opam/ocaml-base-compiler/bin/albatross-tls-endpoint", "cacert.pem", "server.pem", "server.key"])
    def Destroy_vm() : 
            # Destroying the vm 
            subprocess.run(["sudo","albatross-client", "destroy", "unipi"])


    def sign_certificate_request():
             subprocess.run(["sudo","albatross-client","cacert.pem", "db", "key.pem", "user.req"])


    def intermediate_sign_unipi_request():
            # Intermediate CA signs the request
            subprocess.run(["albatross-client", "sign", "key/user.pem", "db", "key/user.key", "key/user.req"])

    def client_create_remote_unipi():
            # Client sends the signed request to the server
            subprocess.run(["albatross-client", "certificate", "key/cacert.pem", "key/unipi.pem", "key/unipi.key", "--destination", "10.0.0.10/24"])

    async def sign_vm():
            Certif.generate_ca()
            Certif.user_add_policy()
            Certif.ca_sign_user_request()
            # intermediate_sign_unipi_request()
            # client_create_remote_unipi()

    async def create_vm_with_unipi():
            
            ssh_key = "rsa:fZ6C4YpxVTVjZErqfnzDAunGlv6Jn67pqj2epEDg"
            ssh_authenticator = "SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU"

            # Execute the albatross-client command to create a VM with unipi.hvt
            subprocess.run([
                "sudo",
                "albatross-client", "create", "unipi", "/home/ahmed/Desktop/cyber/idenity/unipi/dist/unipi.spt","--csr"
                "--net=service",
                "--arg=--ipv4=10.0.0.10/24",
                "--arg=--ipv4-gateway=10.0.0.254",
                "--arg=--port=8443",
                "--arg=--remote=https://github.com/ahmed1abid/Test.git",
                "--arg=--ssh-authenticator=" + ssh_authenticator,
                "--arg=--ssh-key=" + ssh_key,
                "--arg=--tls=false",
                "--arg=--hook=/updatewebhook",
                "--arg=-l debug",
                "--arg=--ipv4-only=true"

            ])
