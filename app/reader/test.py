from app.reader.base import BaseReader, validate_uri

class TestReader(BaseReader):
    """
    Dummy parser
    """

    def __init__(self):
        self.items = [
            "scheme://project/"
            + exp
            + "/"
            + tp
            + "/"
            + f"file_{row}{col:02d}_w{chan}_s{site}_exp.tiff"
            for exp in ["exp1", "exp2", "exp3"]
            for tp in ["tp1", "tp2"]
            for row in ["A", "B", "C"]
            for col in range(12)
            for chan in range(1, 4)
            for site in range(2)
        ]
        self.allowed_schemes = ['scheme']

    @validate_uri()
    def list(self, uri) -> list[str]:
        """
        Return all items at uri
        """

        return [item for item in self.items if uri in item]

    def __call__(self, *args, **kwargs):
        import numpy as np
        return np.eye(800)
