import subprocess

class Certif:

    @staticmethod
    def generate_ca(debug_mode=False):
        # Générer une autorité de certification (CA)
        cmd_args = ["sudo", "albatross-client", "generate", "ca", "db"]
        if debug_mode:
            cmd_args.append("--verbosity=debug")  # Mode debug
        subprocess.run(cmd_args)

    @staticmethod
    def user_add_policy(vm_name="UNIPI", mem_size=2048, cpu_cores=2, debug_mode=False):
        # Ajouter une politique utilisateur
        cmd_args = ["sudo", "albatross-client", "add-policy", "user", vm_name, "--mem", str(mem_size), "--cpu"] + [str(core) for core in range(cpu_cores)] + ["--csr", "--bridge=service"]
        if debug_mode:
            cmd_args.append("--verbosity=debug")  # Mode debug
        subprocess.run(cmd_args)

    @staticmethod
    def ca_sign_user_request(debug_mode=False):
        # Signer une demande utilisateur par l'AC
        cmd_args = ["sudo", "albatross-client", "sign", "cacert.pem", "db", "ca.key", "user.req"]
        if debug_mode:
            cmd_args.append("--verbosity=debug")  # Mode debug
        subprocess.run(cmd_args)

    @staticmethod
    def intermediate_sign_unipi_request(debug_mode=False):
        # Signer une demande UNIPI intermédiaire
        cmd_args = ["albatross-client", "sign", "user.pem", "db", "user.key", "user.req"]
        if debug_mode:
            cmd_args.append("--verbosity=debug")  # Mode debug
        subprocess.run(cmd_args)

    @staticmethod
    def create_unikernel(vm_name="UNIPI", vm_image="/home/ahmed/Desktop/cyber/idenity/unipi/dist/unipi.spt", ipv4="10.0.0.10/24", ipv4_gateway="10.0.0.254", port="8443", tls="false", hook="/updatewebhook", debug_mode=False):
        # Créer un unikernel
        # Note: ssh_authenticator et ssh_key ne sont pas définis comme paramètres car ce sont des informations sensibles.
        cmd_args = [
            "sudo",
            "albatross-client", "create", vm_name, vm_image, "--csr",
            "--net=service",
            "--arg=--ipv4=" + ipv4,
            "--arg=--ipv4-gateway=" + ipv4_gateway,
            "--arg=--port=" + port,
            "--arg=--tls=" + tls,
            "--arg=--hook=" + hook,
        ]
        if debug_mode:
            cmd_args.append("--arg=-l debug")  # Mode debug
        subprocess.run(cmd_args)

    @staticmethod
    def server_start_endpoint(cacert, server_cert, server_key, debug_mode=False):
        # Démarrer le point de terminaison du serveur
        cmd_args = ["sudo", "/home/ahmed/.opam/ocaml-base-compiler/bin/albatross-tls-endpoint", cacert, server_cert, server_key]
        if debug_mode:
            cmd_args.append("--verbosity=debug")  # Mode debug
        subprocess.run(cmd_args)

    @staticmethod
    def destroy_vm(vm_name="UNIPI", debug_mode=False):
        # Détruire la machine virtuelle
        cmd_args = ["sudo", "albatross-client", "destroy", vm_name]
        if debug_mode:
            cmd_args.append("--verbosity=debug")  # Mode debug
        subprocess.run(cmd_args)

    @staticmethod
    def sign_vm(vm_name="UNIPI", vm_image="/home/ahmed/Desktop/cyber/idenity/unipi/dist/unipi.spt", ipv4="10.0.0.10/24", ipv4_gateway="10.0.0.254", port="8443", tls="false", hook="/updatewebhook", debug_mode=False):
        # Signer la machine virtuelle
        Certif.generate_ca(debug_mode)
        Certif.user_add_policy(debug_mode=debug_mode)
        Certif.intermediate_sign_unipi_request(debug_mode)
        Certif.create_unikernel(vm_name=vm_name, vm_image=vm_image, ipv4=ipv4, ipv4_gateway=ipv4_gateway, port=port, tls=tls, hook=hook, debug_mode=debug_mode)


