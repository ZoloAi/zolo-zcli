# zCLI/subsystems/zDisplay/zDisplay_modules/zEvents_packages/AdvancedData.py
"""AdvancedData - complex data display with pagination."""


class Pagination:
    """Pagination helper for slicing data with limit/offset parameters."""

    @staticmethod
    def paginate(data, limit=None, offset=0):
        """Paginate data with limit/offset and return dict with items and metadata."""
        if not data:
            return {
                "items": [],
                "total": 0,
                "showing_start": 0,
                "showing_end": 0,
                "has_more": False
            }

        total = len(data)

        # No limit - show all
        if limit is None:
            return {
                "items": data,
                "total": total,
                "showing_start": 1,
                "showing_end": total,
                "has_more": False
            }

        # Negative limit - from bottom
        if limit < 0:
            items = data[limit:]  # Last N items
            showing_start = max(1, total + limit + 1)
            showing_end = total
            has_more = abs(limit) < total

            return {
                "items": items,
                "total": total,
                "showing_start": showing_start,
                "showing_end": showing_end,
                "has_more": has_more
            }

        # Positive limit - from top with offset
        start_idx = offset
        end_idx = offset + limit
        items = data[start_idx:end_idx]

        showing_start = start_idx + 1 if items else 0
        showing_end = start_idx + len(items)
        has_more = end_idx < total

        return {
            "items": items,
            "total": total,
            "showing_start": showing_start,
            "showing_end": showing_end,
            "has_more": has_more
        }


class AdvancedData:
    """Advanced data display events: zTable with pagination."""

    def __init__(self, display_instance):
        """Initialize AdvancedData with reference to parent display instance."""
        self.display = display_instance
        self.zPrimitives = display_instance.zPrimitives
        self.zColors = display_instance.zColors
        # Get references to other packages for composition
        self.BasicOutputs = None  # Will be set after zEvents initialization
        self.Signals = None  # Will be set after zEvents initialization

        # Internal pagination helper
        self.pagination = Pagination()

    def zTable(self, title, columns, rows, limit=None, offset=0, show_header=True):
        """Display data table with optional pagination and formatting for Terminal/GUI modes."""
        # Try GUI mode first - send clean event
        if self.zPrimitives.send_gui_event("zTable", {
            "title": title,
            "columns": columns,
            "rows": rows,
            "limit": limit,
            "offset": offset,
            "show_header": show_header
        }):
            return  # GUI event sent successfully

        # Terminal mode - display formatted table
        if not columns:
            if self.Signals:
                self.Signals.warning("No columns defined for table", indent=0)
            return

        # Paginate rows
        page_info = self.pagination.paginate(rows, limit, offset)
        paginated_rows = page_info["items"]

        # Display title with pagination info
        if self.BasicOutputs:
            self.BasicOutputs.text("", break_after=False)
            self.BasicOutputs.header(
                f"{title} (showing {page_info['showing_start']}-{page_info['showing_end']} of {page_info['total']})",
                color="CYAN",
                style="full"
            )

        # Display column headers if requested
        if show_header and self.BasicOutputs:
            header_row = self._format_row(columns, columns, is_header=True)
            self.BasicOutputs.text(header_row, indent=1, break_after=False)
            self.BasicOutputs.text("─" * 60, indent=1, break_after=False)

        # Display rows
        if not paginated_rows:
            if self.Signals:
                self.Signals.info("No rows to display", indent=1)
        else:
            for row in paginated_rows:
                formatted_row = self._format_row(row, columns)
                if self.BasicOutputs:
                    self.BasicOutputs.text(formatted_row, indent=1, break_after=False)

        # Display pagination footer
        if page_info["has_more"]:
            if self.Signals:
                self.Signals.info(
                    f"... {page_info['total'] - page_info['showing_end']} more rows",
                    indent=1
                )

        if self.BasicOutputs:
            self.BasicOutputs.text("", break_after=False)

    def _format_row(self, row, columns, is_header=False):
        """Format a single row for display with given columns and optional header formatting."""
        # Convert row to list if it's a dict
        if isinstance(row, dict):
            row_values = [str(row.get(col, "")) for col in columns]
        elif isinstance(row, list):
            row_values = [str(val) for val in row]
        else:
            row_values = [str(row)]

        # Calculate column widths (simple fixed width for now)
        col_width = 15

        # Format each cell
        formatted_cells = []
        for i, value in enumerate(row_values):
            # Truncate if too long
            if len(value) > col_width:
                value = value[:col_width-3] + "..."

            # Apply header formatting (use CYAN for headers)
            if is_header:
                value = f"{self.zColors.CYAN}{value}{self.zColors.RESET}"

            # Pad to column width
            formatted_cells.append(value.ljust(col_width))

        return " ".join(formatted_cells)
