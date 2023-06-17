from pydantic import BaseModel, validator
from typing import List
import ipaddress
from cryptography.fernet import Fernet, InvalidToken
import config


class Host(BaseModel):
    """
    Represents a host in the inventory.
    """

    hostname: str
    ip_address: str
    password: str
    private_key_path: str

    @validator('ip_address')
    def validate_ip_address(cls, value):
        """
        Validates if the IP address is a valid IPv4 or IPv6 address.

        Args:
            value (str): The IP address to validate.

        Returns:
            str: The validated IP address.

        Raises:
            ValueError: If the IP address is invalid.
        """
        try:
            ipaddress.ip_address(value)
        except ValueError:
            raise ValueError(f'Invalid IP address ({value}) provided')
        return value
    
    def encrypt_password(self) -> str:
        """
        Encrypts the password using the encryption key if it is not already encrypted.

        Returns:
            str: The encrypted password.
        """
        if not self._is_password_encrypted():
            cipher_suite = Fernet(config.ENCRYPTION_KEY)
            encrypted_password = cipher_suite.encrypt(self.password.encode())
            self.password = encrypted_password.decode()
        return self.password

    def decrypt_password(self) -> str:
        """
        Decrypts the password using the encryption key if it is encrypted.

        Returns:
            str: The decrypted password.
        """
        if self._is_password_encrypted():
            cipher_suite = Fernet(config.ENCRYPTION_KEY)
            decrypted_password = cipher_suite.decrypt(self.password.encode())
            self.password = decrypted_password.decode()
        return self.password

    def _is_password_encrypted(self) -> bool:
        """
        Checks if the password is already encrypted.

        Returns:
            bool: True if the password is encrypted, False otherwise.
        """
        cipher_suite = Fernet(config.ENCRYPTION_KEY)
        try:
            cipher_suite.decrypt(self.password.encode())
        except InvalidToken:
            return False
        return True


class HostGroup(BaseModel):
    """
    Represents a host group in the inventory.
    """

    group_name: str
    hosts: List[Host] = []


class Variable(BaseModel):
    """
    Represents a variable in the inventory.
    """

    variable_name: str
    value: str
