class InsufficientRetainedContent(Exception):
    """Raised before export when the selected cuts leave no usable video."""

    def __init__(self, input_duration_seconds: float, retained_duration_seconds: float,
                 removed_duration_seconds: float):
        super().__init__(
            "The selected settings would remove virtually the entire video; no output was created"
        )
        self.input_duration_seconds = input_duration_seconds
        self.retained_duration_seconds = retained_duration_seconds
        self.removed_duration_seconds = removed_duration_seconds
