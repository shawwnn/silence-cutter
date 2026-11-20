class NoSilenceDetected(Exception):
    """Raised when a job has no intervals that meet the user's criteria."""

    def __init__(self, input_duration_seconds: float):
        super().__init__("No silence matched the selected duration and threshold")
        self.input_duration_seconds = input_duration_seconds
