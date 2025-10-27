"""
ProgressContext - Injectable progress tracking for declarative _progress metadata

Week 4.3: Declarative Progress Pattern
Allows zUI files to specify _progress metadata, which gets injected into plugin functions.
"""


class ProgressContext:
    """
    Progress tracking context injected into plugin functions when _progress metadata is present.
    
    Usage in plugin:
        def my_long_task(zcli, progress=None):
            if progress:
                for i, item in progress.iterator(items):
                    process(item)
            else:
                for item in items:
                    process(item)
    
    The framework creates this context based on _progress metadata in zUI:
        "Do Work":
          _progress: {label: "Processing", show_eta: true}
          zFunc: "&plugin.my_long_task()"
    """
    
    def __init__(self, display, config=None):
        """
        Initialize progress context.
        
        Args:
            display: zDisplay instance for rendering
            config: _progress metadata dict from zUI
        """
        self.display = display
        self.config = config or {}
        self.label = self.config.get('label', 'Processing')
        self.style = self.config.get('style', 'bar')  # 'bar' or 'spinner'
        self.show_eta = self.config.get('show_eta', False)
        self.show_percentage = self.config.get('show_percentage', True)
        self.color = self.config.get('color', 'GREEN')
        
        self._start_time = None
        self._current = 0
        self._total = None
    
    def update(self, current, total=None):
        """
        Update progress bar.
        
        Args:
            current: Current progress value
            total: Total value (optional, uses last set total if not provided)
        """
        import time
        
        if self._start_time is None:
            self._start_time = time.time()
        
        if total is not None:
            self._total = total
        
        self._current = current
        
        if self._total:
            self.display.progress_bar(
                current=current,
                total=self._total,
                label=self.label,
                show_percentage=self.show_percentage,
                show_eta=self.show_eta,
                start_time=self._start_time,
                color=self.color
            )
    
    def iterator(self, iterable, total=None):
        """
        Wrap an iterable with automatic progress tracking.
        
        Args:
            iterable: Any iterable to wrap
            total: Total count (auto-detected if iterable has __len__)
        
        Yields:
            Items from the iterable
        
        Example:
            for item in progress.iterator(items):
                process(item)
        """
        if total is None:
            try:
                total = len(iterable)
            except TypeError:
                total = None
        
        return self.display.progress_iterator(
            iterable,
            label=self.label,
            show_eta=self.show_eta,
            color=self.color
        )
    
    def spinner(self, label=None):
        """
        Create a spinner context manager.
        
        Args:
            label: Optional label override
        
        Returns:
            Context manager for spinner
        
        Example:
            with progress.spinner("Loading"):
                do_work()
        """
        return self.display.spinner(
            label=label or self.label,
            style=self.config.get('spinner_style', 'dots')
        )
    
    def start_spinner(self):
        """Start a spinner (for non-context-manager use)."""
        return self.spinner().__enter__()
    
    def stop_spinner(self):
        """Stop the current spinner."""
        # This is a simplified version - proper implementation would track the context
        pass
    
    def complete(self, message=None):
        """
        Mark progress as complete with optional success message.
        
        Args:
            message: Optional completion message
        """
        if message:
            self.display.success(message)
        elif self._total and self._current >= self._total:
            self.display.success(f"✅ {self.label} complete!")

