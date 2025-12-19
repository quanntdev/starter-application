"""Favourite tab with two-column layout."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QComboBox, QPushButton, QLineEdit, QListWidget, QListWidgetItem,
    QScrollArea, QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QTimer
import qtawesome as qta
import time

from services.launcher_service import LauncherService
from services.url_service import URLService
from ui.components.dialogs import ConfirmDeleteDialog


class LinkItemWidget(QWidget):
    """Widget for a single link item with delete button."""
    
    def __init__(self, url, on_delete_callback, parent=None):
        super().__init__(parent)
        self.url = url
        self.on_delete_callback = on_delete_callback
        self.init_ui()
    
    def init_ui(self):
        """Initialize link item UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # URL label
        url_label = QLabel(self.url)
        url_label.setStyleSheet("color: #e0e0e0;")
        url_label.setWordWrap(True)
        layout.addWidget(url_label, 1)
        
        # Delete button
        btn_delete = QPushButton()
        btn_delete.setIcon(qta.icon('fa5s.times', color='white'))
        btn_delete.setProperty("class", "danger")
        btn_delete.setToolTip("Remove")
        btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_delete.clicked.connect(lambda: self.on_delete_callback(self.url))
        btn_delete.setMaximumWidth(30)
        btn_delete.setMaximumHeight(30)
        layout.addWidget(btn_delete)


class FavouriteRowWidget(QWidget):
    """Widget for a single favourite row."""
    
    def __init__(self, favourite, translator, on_change_callback, on_delete_callback, on_test_callback, on_row_click_callback, on_label_change_callback, is_selected=False, parent=None):
        super().__init__(parent)
        self.favourite = favourite
        self.translator = translator
        self.on_change_callback = on_change_callback
        self.on_delete_callback = on_delete_callback
        self.on_test_callback = on_test_callback
        self.on_row_click_callback = on_row_click_callback
        self.on_label_change_callback = on_label_change_callback
        self.is_selected = is_selected
        self.init_ui()
        self.update_highlight()
    
    def init_ui(self):
        """Initialize row UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Set object name for specific styling
        self.setObjectName("favouriteRow")
        
        # Checkbox for multi-select
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(self.favourite.selected)
        self.checkbox.stateChanged.connect(self.on_selected_changed)
        layout.addWidget(self.checkbox)
        
        # App name only (no badge)
        name_label = QLabel(self.favourite.name)
        name_label.setStyleSheet("font-weight: 500;")
        name_label.setCursor(Qt.CursorShape.PointingHandCursor)
        name_label.mousePressEvent = lambda e: self.on_row_click_callback(self.favourite)
        layout.addWidget(name_label, 1)
        
        # Label dropdown (smaller)
        self.label_combo = QComboBox()
        self.label_combo.addItems([
            self.translator.t("favourites.label.browser"),
            self.translator.t("favourites.label.app"),
            self.translator.t("favourites.label.working_app")
        ])
        
        # Set current selection based on kind
        if self.favourite.kind == "browser":
            self.label_combo.setCurrentIndex(0)
        elif self.favourite.kind == "working_app":
            self.label_combo.setCurrentIndex(2)
        else:
            self.label_combo.setCurrentIndex(1)
        
        self.label_combo.currentIndexChanged.connect(self.on_label_changed)
        self.label_combo.setMaximumWidth(120)  # Reduced from 150
        self.label_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        # Click on combobox also selects row
        self.label_combo.mousePressEvent = self.create_click_handler(self.label_combo.mousePressEvent)
        layout.addWidget(self.label_combo)
        
        # Test button (icon only)
        btn_test = QPushButton()
        btn_test.setIcon(qta.icon('fa5s.play', color='white'))
        btn_test.setProperty("class", "icon")
        btn_test.setToolTip(self.translator.t("common.actions.test"))
        btn_test.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_test.clicked.connect(lambda: self.on_test_callback(self.favourite))
        btn_test.setMaximumWidth(40)
        layout.addWidget(btn_test)
        
        # Delete button (trash icon)
        btn_delete = QPushButton()
        btn_delete.setIcon(qta.icon('fa5s.trash', color='white'))
        btn_delete.setProperty("class", "danger")
        btn_delete.setToolTip(self.translator.t("common.actions.delete"))
        btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_delete.clicked.connect(lambda: self.on_delete_callback(self.favourite))
        btn_delete.setMaximumWidth(40)
        layout.addWidget(btn_delete)
    
    def create_click_handler(self, original_handler):
        """Create a click handler that also selects the row."""
        def handler(event):
            self.on_row_click_callback(self.favourite)
            original_handler(event)
        return handler
    
    def mousePressEvent(self, event):
        """Handle click anywhere on row (except checkbox)."""
        # Check if click is not on checkbox
        if not self.checkbox.geometry().contains(event.pos()):
            self.on_row_click_callback(self.favourite)
        super().mousePressEvent(event)
    
    def update_highlight(self):
        """Update highlight style based on selection state."""
        if self.is_selected:
            # Selected state - highlight text and input with blue, keep icons normal
            self.setStyleSheet("""
                #favouriteRow {
                    background-color: transparent;
                    border-radius: 6px;
                    border-left: 3px solid #0d6efd;
                }
                QLabel {
                    background-color: transparent;
                    color: #0d6efd;
                    font-weight: 600;
                }
                QComboBox {
                    background-color: #2d2d2d;
                    border: 2px solid #0d6efd;
                    color: #0d6efd;
                }
                QPushButton {
                    background-color: transparent;
                }
            """)
        else:
            # Normal state - transparent
            self.setStyleSheet("""
                #favouriteRow {
                    background-color: transparent;
                    border-radius: 6px;
                    border-left: 3px solid transparent;
                }
                #favouriteRow:hover {
                    background-color: #2d2d2d;
                }
                QLabel {
                    background-color: transparent;
                    color: #e0e0e0;
                    font-weight: 500;
                }
            """)
    
    def set_selected(self, selected):
        """Set selection state and update highlight."""
        self.is_selected = selected
        self.update_highlight()
    
    def on_selected_changed(self, state):
        """Handle checkbox state change."""
        self.favourite.selected = (state == Qt.CheckState.Checked.value)
        self.on_change_callback()
    
    def on_label_changed(self, index):
        """Handle label dropdown change."""
        if index == 0:
            self.favourite.kind = "browser"
            self.favourite.label = self.translator.t("favourites.label.browser")
        elif index == 2:
            self.favourite.kind = "working_app"
            self.favourite.label = self.translator.t("favourites.label.working_app")
        else:
            self.favourite.kind = "app"
            self.favourite.label = self.translator.t("favourites.label.app")
        
        self.on_change_callback()
        # Also notify about label change to update right panel
        self.on_label_change_callback(self.favourite)


class FavouriteTab(QWidget):
    """Favourite tab with list and links panel."""
    
    def __init__(self, config_store, translator, parent=None):
        super().__init__(parent)
        self.config_store = config_store
        self.translator = translator
        self.launcher = LauncherService()
        self.currently_editing_fav = None  # Track which favourite is being edited
        self.row_widgets = []  # Initialize row widgets list
        self.init_ui()
        self.load_favourites()
    
    def init_ui(self):
        """Initialize tab UI."""
        main_layout = QVBoxLayout(self)
        
        # Title
        self.title_label = QLabel(self.translator.t("favourite.title"))
        self.title_label.setStyleSheet("font-size: 18px; font-weight: 600;")
        main_layout.addWidget(self.title_label)
        
        # Description at the top
        self.description_label = QLabel(self.translator.t("favourites.description"))
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("font-size: 13px; color: #a0a0a0; margin-bottom: 15px;")
        main_layout.addWidget(self.description_label)
        
        # Two-column layout
        layout = QHBoxLayout()
        layout.setSpacing(20)
        
        # Left column - Favourites list
        left_widget = QWidget()
        left_widget.setProperty("class", "card")
        left_layout = QVBoxLayout(left_widget)
        
        # Title and Run All button
        title_layout = QHBoxLayout()
        self.title_label = QLabel(self.translator.t("favourites.title"))
        self.title_label.setStyleSheet("font-size: 18px; font-weight: 600;")
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        # Run All button
        self.run_all_button = QPushButton()
        self.run_all_button.setIcon(qta.icon('fa5s.play-circle', color='white'))
        self.run_all_button.setText("  " + self.translator.t("favourites.run_all"))
        self.run_all_button.setToolTip("Launch all favourites")
        self.run_all_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.run_all_button.clicked.connect(self.run_all_favourites)
        title_layout.addWidget(self.run_all_button)
        
        left_layout.addLayout(title_layout)
        
        # Scroll area for favourites list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.fav_list_widget = QWidget()
        self.fav_list_layout = QVBoxLayout(self.fav_list_widget)
        self.fav_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll.setWidget(self.fav_list_widget)
        left_layout.addWidget(scroll)
        
        layout.addWidget(left_widget, 1)
        
        # Right column - Links panel or Coming soon
        self.right_stack_widget = QWidget()
        self.right_stack_widget.setProperty("class", "card")
        self.right_layout = QVBoxLayout(self.right_stack_widget)
        
        # Add layout to main layout
        main_layout.addLayout(layout)
        
        self.update_right_panel()
        
        layout.addWidget(self.right_stack_widget, 1)
    
    def load_favourites(self):
        """Load favourites from config store."""
        # Clear existing widgets
        while self.fav_list_layout.count():
            item = self.fav_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add favourite rows
        favourites = self.config_store.get_favourites()
        self.row_widgets = []  # Track all row widgets
        for fav in favourites:
            is_selected = (self.currently_editing_fav and fav.id == self.currently_editing_fav.id)
            row = FavouriteRowWidget(
                fav,
                self.translator,
                self.on_favourite_changed,
                self.on_favourite_delete,
                self.on_favourite_test,
                self.on_row_clicked,
                self.on_label_changed_update,
                is_selected
            )
            self.row_widgets.append(row)
            self.fav_list_layout.addWidget(row)
    
    def on_favourite_changed(self):
        """Handle favourite change (auto-save)."""
        self.config_store.save()
        # Don't update right panel on checkbox change
    
    def on_label_changed_update(self, favourite):
        """Handle label change and update right panel if this is currently editing."""
        if self.currently_editing_fav and self.currently_editing_fav.id == favourite.id:
            # Update right panel since kind changed
            self.update_right_panel()
    
    def on_row_clicked(self, favourite):
        """Handle row click - select for editing."""
        self.currently_editing_fav = favourite
        
        # Update highlight for all rows
        if hasattr(self, 'row_widgets'):
            for row in self.row_widgets:
                is_selected = (row.favourite.id == favourite.id)
                row.set_selected(is_selected)
        
        self.update_right_panel()
    
    def on_favourite_delete(self, favourite):
        """Handle favourite deletion."""
        dialog = ConfirmDeleteDialog(
            "Delete Favourite",
            f"Are you sure you want to delete '{favourite.name}' from favourites?",
            self
        )
        
        if dialog.exec():
            self.config_store.delete_favourite(favourite.id)
            self.load_favourites()
            self.update_right_panel()
    
    def on_favourite_test(self, favourite):
        """Handle test button click."""
        self.launcher.test_favourite(favourite)
    
    def update_right_panel(self):
        """Update right panel based on currently editing favourite."""
        # Clear right panel completely
        while self.right_layout.count():
            item = self.right_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Clear nested layouts
                self.clear_layout(item.layout())
        
        # Check if we have a favourite being edited
        if self.currently_editing_fav and self.currently_editing_fav.kind == "browser":
            # Show links panel for browser
            self.build_links_panel(self.currently_editing_fav)
        else:
            # Show hint
            hint_text = ""
            if self.currently_editing_fav and self.currently_editing_fav.kind != "browser":
                hint_text = f"{self.currently_editing_fav.name}\n\n{self.translator.t('favourites.right.coming_soon')}"
            else:
                hint_text = self.translator.t("favourites.links.multi_select_hint")
            
            hint_label = QLabel(hint_text)
            hint_label.setWordWrap(True)
            hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hint_label.setStyleSheet("color: #a0a0a0; padding: 40px; font-size: 14px;")
            self.right_layout.addWidget(hint_label)
    
    def clear_layout(self, layout):
        """Recursively clear a layout."""
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                elif item.layout():
                    self.clear_layout(item.layout())
    
    def build_links_panel(self, favourite):
        """Build links management panel for a browser favourite."""
        self.current_browser_fav = favourite
        
        # Title with favourite name
        title_layout = QHBoxLayout()
        title = QLabel(self.translator.t("favourites.links.title"))
        title.setStyleSheet("font-size: 18px; font-weight: 600;")
        title_layout.addWidget(title)
        
        # Add label showing selected favourite name
        fav_name_label = QLabel(f"({favourite.name})")
        fav_name_label.setStyleSheet("font-size: 14px; color: #0d6efd; font-weight: 500;")
        title_layout.addWidget(fav_name_label)
        title_layout.addStretch()
        
        self.right_layout.addLayout(title_layout)
        
        self.right_layout.addSpacing(10)
        
        # Input + Add button
        input_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(self.translator.t("favourites.links.placeholder"))
        input_layout.addWidget(self.url_input)
        
        btn_add = QPushButton(self.translator.t("favourites.links.add"))
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add.clicked.connect(self.on_add_link)
        btn_add.setMaximumWidth(80)
        input_layout.addWidget(btn_add)
        
        self.right_layout.addLayout(input_layout)
        
        self.right_layout.addSpacing(10)
        
        # Links list with scroll
        links_scroll = QScrollArea()
        links_scroll.setWidgetResizable(True)
        links_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        links_container = QWidget()
        self.links_container_layout = QVBoxLayout(links_container)
        self.links_container_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.links_container_layout.setSpacing(4)
        
        # Add link items
        for link in favourite.browser_links:
            link_widget = LinkItemWidget(link, self.on_remove_link)
            self.links_container_layout.addWidget(link_widget)
        
        links_scroll.setWidget(links_container)
        self.right_layout.addWidget(links_scroll)
    
    def on_add_link(self):
        """Handle add link button."""
        url = self.url_input.text().strip()
        
        if not url:
            return
        
        if not URLService.validate_url(url):
            QMessageBox.warning(
                self,
                "Invalid URL",
                self.translator.t("common.messages.url_invalid")
            )
            return
        
        url = URLService.normalize_url(url)
        
        # Check duplicate
        if url in self.current_browser_fav.browser_links:
            return
        
        # Add to favourite
        self.current_browser_fav.browser_links.append(url)
        self.config_store.save()
        
        # Update UI - add new link widget
        link_widget = LinkItemWidget(url, self.on_remove_link)
        self.links_container_layout.addWidget(link_widget)
        
        self.url_input.clear()
    
    def on_remove_link(self, url):
        """Handle remove link button."""
        # Remove from favourite
        if url in self.current_browser_fav.browser_links:
            self.current_browser_fav.browser_links.remove(url)
            self.config_store.save()
        
        # Rebuild links panel to refresh UI
        self.update_right_panel()
    
    def run_all_favourites(self):
        """Launch selected favourites only."""
        favourites = self.config_store.get_favourites()
        
        # Filter only selected favourites
        selected_favourites = [f for f in favourites if f.selected]
        
        if not selected_favourites:
            QMessageBox.information(
                self,
                "No Selected Favourites",
                "Please select at least one favourite to launch."
            )
            return
        
        # Launch selected favourites with a small delay between each
        launched_count = 0
        for i, fav in enumerate(selected_favourites):
            try:
                if fav.kind == "browser" and fav.browser_links:
                    self.launcher.launch_browser_urls(fav.lnk_path, fav.browser_links)
                else:
                    self.launcher.launch_app(fav.lnk_path)
                launched_count += 1
                
                # Small delay between launches to avoid overwhelming the system
                if i < len(selected_favourites) - 1:  # Don't delay after the last one
                    time.sleep(0.3)
            except Exception as e:
                print(f"Error launching {fav.name}: {e}")
        
        if launched_count > 0:
            QMessageBox.information(
                self,
                "Launched",
                f"Successfully launched {launched_count} favourite(s)."
            )
    
    def refresh_ui(self):
        """Refresh UI after language change."""
        self.description_label.setText(self.translator.t("favourites.description"))
        self.title_label.setText(self.translator.t("favourites.title"))
        self.run_all_button.setText("  " + self.translator.t("favourites.run_all"))
        self.load_favourites()
        self.update_right_panel()

