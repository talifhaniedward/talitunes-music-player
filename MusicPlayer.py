import os
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                            QPushButton, QWidget, QFileDialog, QListWidget,
                            QSlider, QLabel, QMessageBox, QStyleFactory, QStyle)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QIcon, QPalette, QColor, QPainter, QLinearGradient, QFont, QBrush
import pygame
from pygame import mixer

# Initialize pygame mixer
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)

class TaliTunesLogo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 70)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#6a11cb"))
        gradient.setColorAt(1, QColor("#2575fc"))
        painter.setBrush(QBrush(gradient))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 10, 10)
        
        font = QFont("Arial", 16, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor("#ffffff"))
        painter.drawText(self.rect(), Qt.AlignCenter, "TaliTunes")

class MusicPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TaliTunes Music Player")
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(600, 500)
        
        # Player State
        self.current_file = None
        self.playlist = []
        self.current_index = -1
        self.paused = False
        self.volume = 70
        self.is_playing = False
        self.last_volume = 70
        self.theme = "dark"

        self.init_ui()
        self.apply_theme(self.theme)
        
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress)

    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Top Bar with Logo and Controls
        top_bar = QHBoxLayout()
        self.logo = TaliTunesLogo()
        top_bar.addWidget(self.logo)
        top_bar.addStretch()
        
        # Control Buttons
        control_buttons = QHBoxLayout()
        
        # Refresh Button
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setFixedWidth(100)
        self.refresh_btn.clicked.connect(self.refresh_app)
        control_buttons.addWidget(self.refresh_btn)
        
        # Clear Playlist Button
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setFixedWidth(100)
        self.clear_btn.clicked.connect(self.clear_playlist)
        control_buttons.addWidget(self.clear_btn)
        
        # Theme Button
        self.theme_btn = QPushButton("Theme")
        self.theme_btn.setFixedWidth(100)
        self.theme_btn.clicked.connect(self.toggle_theme)
        control_buttons.addWidget(self.theme_btn)
        
        # Add Music Button
        self.add_btn = QPushButton("Add Music")
        self.add_btn.setFixedWidth(100)
        self.add_btn.clicked.connect(self.add_files)
        control_buttons.addWidget(self.add_btn)
        
        top_bar.addLayout(control_buttons)
        main_layout.addLayout(top_bar)

        # Playlist
        self.playlist_widget = QListWidget()
        self.playlist_widget.setAlternatingRowColors(True)
        self.playlist_widget.itemDoubleClicked.connect(self.play_selected)
        main_layout.addWidget(self.playlist_widget)

        # Now Playing
        self.now_playing = QLabel("No track selected")
        self.now_playing.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.now_playing)

        # Progress Bar
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.sliderMoved.connect(self.seek_position)
        
        # Time Labels
        time_layout = QHBoxLayout()
        self.current_time = QLabel("00:00")
        self.total_time = QLabel("00:00")
        time_layout.addWidget(self.current_time)
        time_layout.addStretch()
        time_layout.addWidget(self.total_time)
        
        progress_layout = QVBoxLayout()
        progress_layout.addLayout(time_layout)
        progress_layout.addWidget(self.progress_slider)
        main_layout.addLayout(progress_layout)

        # Playback Controls
        control_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton()
        self.prev_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipBackward))
        self.prev_btn.clicked.connect(self.prev_track)
        
        self.play_btn = QPushButton()
        self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_btn.clicked.connect(self.toggle_play)
        
        self.next_btn = QPushButton()
        self.next_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipForward))
        self.next_btn.clicked.connect(self.next_track)
        
        control_layout.addWidget(self.prev_btn)
        control_layout.addWidget(self.play_btn)
        control_layout.addWidget(self.next_btn)
        
        # Volume Control
        control_layout.addStretch()
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.volume)
        self.volume_slider.valueChanged.connect(self.set_volume)
        control_layout.addWidget(self.volume_slider)
        
        main_layout.addLayout(control_layout)

        # Status Bar
        self.status_bar = QLabel("Ready")
        main_layout.addWidget(self.status_bar)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def apply_theme(self, theme):
        palette = QPalette()
        if theme == "dark":
            palette.setColor(QPalette.Window, QColor("#1e1e2e"))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor("#2a2a3a"))
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor("#3a3a3a"))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.Highlight, QColor("#7d5fff"))
        else:
            palette.setColor(QPalette.Window, QColor("#f5f5f5"))
            palette.setColor(QPalette.WindowText, Qt.black)
            palette.setColor(QPalette.Base, QColor("#e0e0e0"))
            palette.setColor(QPalette.Text, Qt.black)
            palette.setColor(QPalette.Button, QColor("#d0d0d0"))
            palette.setColor(QPalette.ButtonText, Qt.black)
            palette.setColor(QPalette.Highlight, QColor("#6200ee"))
        
        self.setPalette(palette)
        self.update_styles()

    def update_styles(self):
        highlight = "#7d5fff" if self.theme == "dark" else "#6200ee"
        bg_color = "#2a2a3a" if self.theme == "dark" else "#e0e0e0"
        text_color = "#ffffff" if self.theme == "dark" else "#000000"
        
        self.playlist_widget.setStyleSheet(f"""
            QListWidget {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {highlight};
                border-radius: 5px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #1e1e2e;
            }}
            QListWidget::item:selected {{
                background-color: {highlight};
                color: white;
            }}
        """)
        
        self.now_playing.setStyleSheet(f"color: {highlight}; font-weight: bold;")
        self.status_bar.setStyleSheet(f"color: {'#aaaaaa' if self.theme == 'dark' else '#555555'};")

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.apply_theme(self.theme)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Music Files", "",
            "Audio Files (*.mp3 *.wav *.ogg *.flac);;All Files (*)"
        )
        if files:
            self.playlist.extend(files)
            self.playlist_widget.addItems([os.path.basename(f) for f in files])
            self.status_bar.setText(f"Added {len(files)} tracks")

    def play_selected(self, item):
        index = self.playlist_widget.row(item)
        self.play_index(index)

    def play_index(self, index):
        if 0 <= index < len(self.playlist):
            self.current_index = index
            self.current_file = self.playlist[index]
            
            try:
                mixer.music.stop()
                mixer.music.load(self.current_file)
                mixer.music.set_volume(self.volume / 100)
                mixer.music.play()
                
                self.is_playing = True
                self.paused = False
                self.progress_timer.start(100)
                
                self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
                self.now_playing.setText(f"Now Playing: {os.path.basename(self.current_file)}")
                
                # Get track length
                sound = mixer.Sound(self.current_file)
                self.progress_slider.setRange(0, int(sound.get_length() * 1000))
                self.total_time.setText(self.format_time(sound.get_length()))
                
            except Exception as e:
                self.status_bar.setText(f"Error: {str(e)}")

    def toggle_play(self):
        if not self.playlist:
            return
            
        if not self.is_playing and self.current_index == -1:
            self.play_index(0)
            return
            
        if self.paused:
            mixer.music.unpause()
            self.paused = False
            self.is_playing = True
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.progress_timer.start(100)
        elif self.is_playing:
            mixer.music.pause()
            self.paused = True
            self.is_playing = False
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.progress_timer.stop()
        else:
            self.play_index(self.current_index)

    def stop(self):
        mixer.music.stop()
        self.is_playing = False
        self.paused = False
        self.progress_timer.stop()
        self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.status_bar.setText("Playback stopped")

    def next_track(self):
        if self.playlist:
            self.play_index((self.current_index + 1) % len(self.playlist))

    def prev_track(self):
        if self.playlist:
            self.play_index((self.current_index - 1) % len(self.playlist))

    def set_volume(self, value):
        self.volume = value
        mixer.music.set_volume(value / 100)

    def seek_position(self, pos):
        if self.is_playing or self.paused:
            mixer.music.set_pos(pos // 1000)

    def update_progress(self):
        if self.is_playing:
            pos = mixer.music.get_pos()
            self.progress_slider.setValue(pos)
            self.current_time.setText(self.format_time(pos / 1000))

    def format_time(self, seconds):
        mins, secs = divmod(int(seconds), 60)
        return f"{mins:02d}:{secs:02d}"

    def clear_playlist(self):
        reply = QMessageBox.question(self, 'Clear Playlist', 
                                   "Are you sure you want to clear the playlist?",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.playlist.clear()
            self.playlist_widget.clear()
            self.stop()
            self.current_index = -1
            self.current_file = None
            self.now_playing.setText("No track selected")
            self.status_bar.setText("Playlist cleared")

    def refresh_app(self):
        self.stop()
        self.playlist_widget.clear()
        self.playlist.clear()
        self.current_index = -1
        self.current_file = None
        self.now_playing.setText("No track selected")
        self.progress_slider.setValue(0)
        self.current_time.setText("00:00")
        self.total_time.setText("00:00")
        self.status_bar.setText("App refreshed")
        
        # Re-initialize mixer to clear any audio issues
        pygame.mixer.quit()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)

    def closeEvent(self, event):
        self.stop()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    
    player = MusicPlayer()
    player.show()
    sys.exit(app.exec_())