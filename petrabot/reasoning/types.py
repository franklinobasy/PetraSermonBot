from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class LLMMetadata:
    """
    A class to represent metadata for a Large Language Model (LLM).
    Attributes:
    ----------
    client : Optional[Any]
        The client associated with the LLM. Default is None.
    model : str
        The model name or identifier. Default is an empty string.
    client_type : str
        The type of client. Default is an empty string.
    ALLOWED_CLIENT_TYPES : tuple
        A tuple containing the allowed client types. Default is ("google", "groq").
    Methods:
    -------
    set_client_type(client_type: str) -> None
        Set the client_type after validating against allowed choices.
    """
    """"""
    client: Optional[Any] = None
    model: str = ""
    client_type: str = ""
    
    ALLOWED_CLIENT_TYPES: tuple = field(default=("google", "groq"), 
                                        init=False, repr=False)
    
    def set_client_type(self, client_type: str) -> None:
        """Set the client_type after validating against allowed choices."""
        if client_type and client_type not in self.ALLOWED_CLIENT_TYPES:
            raise ValueError(f"client_type must be one of {self.ALLOWED_CLIENT_TYPES}")
        self.client_type = client_type

    