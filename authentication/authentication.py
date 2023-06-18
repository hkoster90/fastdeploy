import paramiko
import logging


class SSHAuthenticator:
    def __init__(self, host: str, port: int, username: str, password: str | None = None, private_key: str | None = None):
        """
        Initializes an SSHAuthenticator object.

        Args:
            host (str): The remote host to connect to.
            port (int): The SSH port number.
            username (str): The SSH username.
            password (str, optional): The password for password-based authentication. Default is None.
            private_key (str, optional): The private key content for key-based authentication. Default is None.
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.private_key = private_key
        self.client = None
        self.connected = False  # Track connection status

        # Initialize logging
        self.logger = logging.getLogger("SSHAuthenticator")
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

    def connect(self):
        """
        Establishes an SSH connection.

        Raises:
            paramiko.AuthenticationException: If authentication fails.
            paramiko.SSHException: If the SSH connection fails.
        """
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        self.logger.info(f"Connecting to {self.host}:{self.port}")
        
        # Validation
        if not self.host or not self.port or not self.username:
            raise ValueError("Invalid SSHAuthenticator configuration")

        try:
            if self.private_key:
                self.logger.info("Using private key authentication")
                private_key_data = paramiko.RSAKey.from_private_key_file(
                    self.private_key)
                self.client.connect(self.host, self.port,
                                    self.username, pkey=private_key_data)
            else:
                self.logger.info("Using password authentication")
                self.client.connect(self.host, self.port,
                                    self.username, self.password)

            self.connected = True  # Connection successful

        except paramiko.AuthenticationException as e:
            self.logger.error(
                f"Authentication failed for {self.username}@{self.host}:{self.port}")
            raise e

        except paramiko.SSHException as e:
            self.logger.error(
                f"SSH connection failed to {self.host}:{self.port}")
            raise e

    def disconnect(self):
        """
        Closes the SSH connection.
        """
        if self.connected:
            self.client.close()
            self.connected = False
            self.logger.info(f"SSH connection to {self.host} closed")

    def __enter__(self):
        """
        Context manager entry point.
        """
        if not self.connected:
            self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit point.
        """
        self.disconnect()

    def execute_command(self, command: str) -> str:
        """
        Executes a command on the remote host.

        Args:
            command (str): The command to execute.

        Returns:
            str: The output of the command.
        """
        try:
            if not self.connected:
                self.connect()

            stdin, stdout, stderr = self.client.exec_command(command)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            if error:
                self.logger.error(f"Error executing command on {self.host}:{self.port}: {error}")
                raise Exception(f"Error executing command: {error}")
            return output

        except paramiko.SSHException as e:
            self.logger.error(f"SSH command execution failed on {self.host}:{self.port}: {e}")
            raise e
