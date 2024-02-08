import subprocess
import os

class Certif:

    @staticmethod
    def generate_ca():
        subprocess.run(["sudo", "albatross-client", "generate", "ca", "db"])

    @staticmethod
    def user_add_policy():
        subprocess.run(["sudo", "albatross-client", "add-policy", "user", "16", "--mem", "2048", "--cpu", "0", "--cpu", "1", "--csr", "--bridge=service"])

    @staticmethod
    def ca_sign_user_request():
        subprocess.run(["sudo", "albatross-client", "sign", "cacert.pem", "db", "ca.key", "user.req"])

    @staticmethod
    def intermediate_sign_unipi_request():
        subprocess.run(["albatross-client", "sign", "user.pem", "db", "user.key", "user.req"])

    @staticmethod
    def create_unikernel():
        subprocess.run(["sudo", "albatross-client", "certificate", "--server-ca=cacert.pem", "unipi.pem", "unipi.key", "--destination", "10.0.0.10/24"])

    @staticmethod
    def sign_certificate_request():
        subprocess.run(["sudo", "albatross-client", "sign", "cacert.pem", "db", "key.pem", "user.req"])

    @staticmethod
    def server_start_endpoint():
        subprocess.run(["sudo", "/home/ahmed/.opam/ocaml-base-compiler/bin/albatross-tls-endpoint", "cacert.pem", "server.pem", "server.key"])

    @staticmethod
    def destroy_vm():
        subprocess.run(["sudo", "albatross-client", "destroy", "unipi"])

    @staticmethod
    def sign_vm():
        Certif.generate_ca()
        Certif.user_add_policy()
        Certif.intermediate_sign_unipi_request()
        Certif.client_create_remote_unipi()
        Certif.ca_sign_user_request()


    @staticmethod
    def client_create_remote_unipi():
        ssh_key = "rsa:fZ6C4YpxVTVjZErqfnzDAunGlv6Jn67pqj2epEDg"
        ssh_authenticator = "SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU"

        subprocess.run([
            "sudo",
            "albatross-client", "create", "unipi", "/home/ahmed/Desktop/cyber/idenity/unipi/dist/unipi.spt", "--csr",
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

