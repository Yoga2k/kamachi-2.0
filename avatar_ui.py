"""
avatar_ui.py — Floating desktop avatar for KAMACHI 2.0 / ZenAI (PyQt5 version)

Shows the robot avatar floating on the screen, with a transparent
background (no window border/title bar). Features:

  - Click-to-dash: click the avatar and it quickly slides to the
    diagonally opposite corner of the screen (bottom-right <-> top-left,
    or bottom-left <-> top-right, whichever diagonal it's currently
    closest to). That corner becomes its new "home".
  - Cursor-shy movement: if you move the mouse cursor close to the
    avatar, it slides away so the cursor can't land on top of it. When
    the cursor moves away again, it gently drifts back to its home
    corner.
  - A soft colored glow behind the avatar reflecting its current status:
    grey = idle, blue (pulsing) = listening, green (pulsing) = speaking.
  - A small animated voice/sound-wave bar indicator just below the
    avatar — bars bounce actively while speaking, pulse gently while
    listening, and sit flat when idle.
  - Gentle idle bobbing motion.
  - A wave/wiggle-and-bounce greeting animation triggered when "hello"
    (or similar) is heard.

Note: since we only have a single static avatar image (no hand-drawn
animation frames of an arm moving), the greeting "wave" is simulated by
rotating and bouncing the whole avatar, not real limb animation.

Requires PyQt5:
    pip install PyQt5

Same public API as before (init_ui / notify_status / notify_user_said /
notify_ai_said), so utils.py and run_with_avatar.py don't need changes.
"""

import math
import sys
from PyQt5 import QtCore, QtGui, QtWidgets

GREETING_WORDS = ("hello", "hi", "hey", "good morning", "good afternoon", "good evening")


class _Bridge(QtCore.QObject):
    """
    Cross-thread signal bridge. The assistant's logic runs on a background
    thread (see run_with_avatar.py), but Qt widgets may only be touched
    from the GUI/main thread. Qt's signal/slot system automatically queues
    emit() calls from other threads onto the receiving object's own
    thread, so this is the safe way to pass updates across.
    """
    status_changed = QtCore.pyqtSignal(str)
    user_said = QtCore.pyqtSignal(str)
    ai_said = QtCore.pyqtSignal(str)


class AvatarWidget(QtWidgets.QWidget):
    AVATAR_SIZE = 160     # square area the avatar image occupies
    WAVE_HEIGHT = 50      # extra strip below the avatar for the voice bars
    SCREEN_MARGIN = 20

    # Cursor-avoidance tuning
    FLEE_DISTANCE = 160   # start dodging once the cursor is this close (px)
    MAX_PUSH_SPEED = 10   # fastest the avatar slides away per tick (px)
    RETURN_LERP = 0.04    # how quickly it drifts back home when cursor is far (0-1)

    # Click-to-dash tuning
    DASH_SPEED = 45        # px per tick while dashing to a corner (fast)
    DIAGONAL_OPPOSITE = {"TL": "BR", "BR": "TL", "TR": "BL", "BL": "TR"}

    STATUS_COLORS = {
        "idle": QtGui.QColor(140, 140, 140, 110),
        "listening": QtGui.QColor(50, 160, 255, 170),
        "speaking": QtGui.QColor(60, 220, 130, 170),
    }

    def __init__(self, avatar_image_path):
        super().__init__()
        self.avatar_image_path = avatar_image_path

        self.bridge = _Bridge()
        self.bridge.status_changed.connect(self._on_status)
        self.bridge.user_said.connect(self._on_user_said)
        self.bridge.ai_said.connect(self._on_ai_said)

        self._status = "idle"
        self._bob_phase = 0.0
        self._glow_phase = 0.0
        self._wave_phase = 0.0
        self._greet_frames_left = 0
        self._rotation_angle = 0.0
        self._y_offset = 0
        self._bar_heights = [4, 4, 4, 4, 4]

        # Home corner position vs. current (possibly fled/dashing) position
        self._home_x = 0
        self._home_y = 0
        self._cur_x = 0.0
        self._cur_y = 0.0
        self._screen_w = 0
        self._screen_h = 0

        # Click-to-dash state
        self._dashing = False
        self._dash_target_x = 0.0
        self._dash_target_y = 0.0

        self._setup_window()
        self._setup_timer()

    # ---------------- window setup ----------------
    def _setup_window(self):
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.Tool  # keeps it out of the taskbar
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        total_height = self.AVATAR_SIZE + self.WAVE_HEIGHT
        self.setFixedSize(self.AVATAR_SIZE, total_height)

        self._base_pixmap = QtGui.QPixmap(self.avatar_image_path).scaled(
            self.AVATAR_SIZE - 20, self.AVATAR_SIZE - 20,
            QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
        )

        screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
        self._screen_w = screen.width()
        self._screen_h = screen.height()
        self._home_x = self._screen_w - self.AVATAR_SIZE - self.SCREEN_MARGIN
        self._home_y = self._screen_h - total_height - self.SCREEN_MARGIN
        self._cur_x = float(self._home_x)
        self._cur_y = float(self._home_y)
        self.move(int(self._cur_x), int(self._cur_y))

    def _setup_timer(self):
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(40)  # ~25 FPS

    # ---------------- corner geometry ----------------
    def _compute_corners(self):
        m = self.SCREEN_MARGIN
        total_height = self.AVATAR_SIZE + self.WAVE_HEIGHT
        return {
            "TL": (m, m),
            "TR": (self._screen_w - self.AVATAR_SIZE - m, m),
            "BL": (m, self._screen_h - total_height - m),
            "BR": (self._screen_w - self.AVATAR_SIZE - m, self._screen_h - total_height - m),
        }

    # ---------------- click-to-dash ----------------
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._start_corner_dash()
        super().mousePressEvent(event)

    def _start_corner_dash(self):
        corners = self._compute_corners()
        nearest_key = min(
            corners.keys(),
            key=lambda k: math.hypot(corners[k][0] - self._cur_x, corners[k][1] - self._cur_y)
        )
        target_key = self.DIAGONAL_OPPOSITE[nearest_key]
        self._dash_target_x, self._dash_target_y = corners[target_key]
        self._dashing = True

    # ---------------- movement (cursor-avoidance / dash / return-home) ----------------
    def _update_position(self):
        if self._dashing:
            dx = self._dash_target_x - self._cur_x
            dy = self._dash_target_y - self._cur_y
            dist = math.hypot(dx, dy)
            if dist < self.DASH_SPEED:
                self._cur_x, self._cur_y = self._dash_target_x, self._dash_target_y
                self._home_x, self._home_y = self._dash_target_x, self._dash_target_y
                self._dashing = False
            else:
                ux, uy = dx / dist, dy / dist
                self._cur_x += ux * self.DASH_SPEED
                self._cur_y += uy * self.DASH_SPEED
            self.move(int(self._cur_x), int(self._cur_y))
            return  # skip cursor-avoidance while dashing to a corner

        cursor = QtGui.QCursor.pos()
        cx, cy = cursor.x(), cursor.y()

        avatar_center_x = self._cur_x + self.AVATAR_SIZE / 2
        avatar_center_y = self._cur_y + self.AVATAR_SIZE / 2

        dx = avatar_center_x - cx
        dy = avatar_center_y - cy
        dist = math.hypot(dx, dy)

        if 0 < dist < self.FLEE_DISTANCE:
            strength = (self.FLEE_DISTANCE - dist) / self.FLEE_DISTANCE * self.MAX_PUSH_SPEED
            ux, uy = dx / dist, dy / dist
            self._cur_x += ux * strength
            self._cur_y += uy * strength
        else:
            self._cur_x += (self._home_x - self._cur_x) * self.RETURN_LERP
            self._cur_y += (self._home_y - self._cur_y) * self.RETURN_LERP

        max_x = self._screen_w - self.AVATAR_SIZE
        max_y = self._screen_h - (self.AVATAR_SIZE + self.WAVE_HEIGHT)
        self._cur_x = min(max(self._cur_x, 0), max_x)
        self._cur_y = min(max(self._cur_y, 0), max_y)

        self.move(int(self._cur_x), int(self._cur_y))

    # ---------------- animation state update ----------------
    def _tick(self):
        self._update_position()
        self._glow_phase += 0.15

        if self._greet_frames_left > 0:
            self._greet_frames_left -= 1
            self._rotation_angle = 18 * math.sin(self._greet_frames_left * 0.9)
            bounce = int(4 * math.sin(self._greet_frames_left * 0.9))
            self._y_offset = -abs(bounce)
        else:
            self._rotation_angle = 0
            self._bob_phase += 0.08
            self._y_offset = int(4 * math.sin(self._bob_phase))

        if self._status == "speaking":
            self._wave_phase += 0.4
            self._bar_heights = [
                int(8 + 14 * abs(math.sin(self._wave_phase + i * 0.9)))
                for i in range(5)
            ]
        elif self._status == "listening":
            self._wave_phase += 0.25
            self._bar_heights = [
                int(6 + 6 * abs(math.sin(self._wave_phase + i * 0.7)))
                for i in range(5)
            ]
        else:
            self._bar_heights = [4, 4, 4, 4, 4]

        self.update()  # schedules a repaint (paintEvent below)

    # ---------------- drawing ----------------
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        center_x = self.AVATAR_SIZE / 2
        center_y = self.AVATAR_SIZE / 2 + self._y_offset

        color = self.STATUS_COLORS.get(self._status, self.STATUS_COLORS["idle"])
        pulse = 6 * abs(math.sin(self._glow_phase)) if self._status != "idle" else 0
        glow_radius = (self.AVATAR_SIZE - 20) / 2 + 12 + pulse

        gradient = QtGui.QRadialGradient(center_x, center_y, glow_radius)
        gradient.setColorAt(0, color)
        faded = QtGui.QColor(color)
        faded.setAlpha(0)
        gradient.setColorAt(1, faded)
        painter.setBrush(QtGui.QBrush(gradient))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawEllipse(QtCore.QPointF(center_x, center_y), glow_radius, glow_radius)

        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self._rotation_angle)
        pix = self._base_pixmap
        painter.drawPixmap(int(-pix.width() / 2), int(-pix.height() / 2), pix)
        painter.restore()

        bar_width = 6
        gap = 6
        n = len(self._bar_heights)
        total_width = n * bar_width + (n - 1) * gap
        start_x = (self.AVATAR_SIZE - total_width) / 2
        base_y = self.AVATAR_SIZE + self.WAVE_HEIGHT / 2

        if self._status == "speaking":
            bar_color = QtGui.QColor(120, 240, 170, 230)
        elif self._status == "listening":
            bar_color = QtGui.QColor(120, 190, 255, 220)
        else:
            bar_color = QtGui.QColor(150, 150, 150, 140)

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(bar_color)
        for i, h in enumerate(self._bar_heights):
            x = start_x + i * (bar_width + gap)
            rect = QtCore.QRectF(x, base_y - h / 2, bar_width, h)
            painter.drawRoundedRect(rect, 3, 3)

    # ---------------- reacting to events ----------------
    def _on_status(self, state):
        self._status = state

    def _on_user_said(self, text):
        if any(word in text.lower() for word in GREETING_WORDS):
            self.trigger_greeting()

    def _on_ai_said(self, text):
        pass

    def trigger_greeting(self):
        """Starts the ~1.4s wave/bounce greeting animation."""
        self._greet_frames_left = 35


# ------------------------------------------------------------------
# Public API — same shape as before, so utils.py and run_with_avatar.py
# work with this file unchanged.
# ------------------------------------------------------------------
_widget = None
_app = None


class AvatarUI:
    def __init__(self, avatar_image_path):
        self.avatar_image_path = avatar_image_path

    def set_status(self, state):
        if _widget:
            _widget.bridge.status_changed.emit(state)

    def set_user_caption(self, text):
        if _widget:
            _widget.bridge.user_said.emit(text)

    def set_ai_caption(self, text):
        if _widget:
            _widget.bridge.ai_said.emit(text)

    def run(self):
        """Blocks the calling thread — call this from your main thread
        only, with the assistant logic running on a background thread."""
        global _widget, _app
        _app = QtWidgets.QApplication(sys.argv)
        _widget = AvatarWidget(self.avatar_image_path)
        _widget.show()
        _app.exec_()


_ui_instance = None


def init_ui(avatar_image_path):
    global _ui_instance
    _ui_instance = AvatarUI(avatar_image_path)
    return _ui_instance


def notify_status(state):
    if _ui_instance:
        _ui_instance.set_status(state)


def notify_user_said(text):
    if _ui_instance and text:
        _ui_instance.set_user_caption(text)


def notify_ai_said(text):
    if _ui_instance and text:
        _ui_instance.set_ai_caption(text)