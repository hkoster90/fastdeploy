import paramiko

class SSHAuthenticator:
    def __init__(self, host, port, username, password=None, private_key_path=None):
        """
        Initializes an SSHAuthenticator object.

        Args:
            host (str): The remote host to connect to.
            port (int): The SSH port number.
            username (str): The SSH username.
            password (str, optional): The password for password-based authentication. Default is None.
            private_key_path (str, optional): The path to the private key file for key-based authentication. Default is None.
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.private_key_path = private_key_path
        self.client = None

    def __enter__(self):
        """
        Establishes an SSH connection and returns the SSH client object.

        Returns:
            paramiko.SSHClient: The SSH client object.
        """
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if self.private_key_path:
            private_key = paramiko.RSAKey.from_private_key_file(self.private_key_path)
            self.client.connect(self.host, self.port, self.username, pkey=private_key)
        else:
            self.client.connect(self.host, self.port, self.username, self.password)

        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Closes the SSH connection.

        Args:
            exc_type (type): The type of exception raised, if any.
            exc_val (Exception): The exception raised, if any.
            exc_tb (traceback): The traceback of the exception, if any.
        """
        self.client.close()