import sys, os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QScrollArea, QDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap

# ------------------------------
# Resource Loader for PyInstaller
# ------------------------------
def resource_path(relative_path):
    """Get absolute path to resource (works in dev and PyInstaller exe)."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ------------------------------
# Strategy Engine Configuration
# ------------------------------
CARD_VALUES = {'A':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':10,'Q':10,'K':10}
TEN_RANKS = {'10','J','Q','K'}
RANKS = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']

HARD_STRATEGY = {
    17:{2:'S',3:'S',4:'S',5:'S',6:'S',7:'S',8:'S',9:'S',10:'S','A':'S'},
    16:{2:'S',3:'S',4:'S',5:'S',6:'S',7:'H',8:'H',9:'H',10:'H','A':'H'},
    11:{2:'D',3:'D',4:'D',5:'D',6:'D',7:'D',8:'D',9:'D',10:'D','A':'H'},
    10:{2:'D',3:'D',4:'D',5:'D',6:'D',7:'D',8:'D',9:'D',10:'H','A':'H'},
    9: {2:'H',3:'D',4:'D',5:'D',6:'D',7:'H',8:'H',9:'H',10:'H','A':'H'}
}
SOFT_STRATEGY = {
    'A,8': {2:'S',3:'S',4:'S',5:'S',6:'S',7:'S',8:'S',9:'S',10:'S','A':'S'},
    'A,7': {2:'S',3:'Ds',4:'Ds',5:'Ds',6:'Ds',7:'S',8:'S',9:'H',10:'H','A':'H'},
    'A,6': {2:'H',3:'D',4:'D',5:'D',6:'D',7:'H',8:'H',9:'H',10:'H','A':'H'}
}
PAIR_STRATEGY = {
    'A,A': {2:'P',3:'P',4:'P',5:'P',6:'P',7:'P',8:'P',9:'P',10:'P','A':'P'},
    '8,8': {2:'P',3:'P',4:'P',5:'P',6:'P',7:'P',8:'P',9:'P',10:'P','A':'P'}
}
ACTION_NAMES = {
    'H': 'Hit','S': 'Stand','D': 'Double (or Hit if not allowed)',
    'Ds': 'Double (or Stand if not allowed)','P': 'Split',
    'BUST': 'Bust','BJ': 'Blackjack!'
}

# ------------------------------
# Hand Model
# ------------------------------
class Hand:
    def __init__(self, name="Player"):
        self.cards = []
        self.name = name
        self.skip_pair = False

    def add_card(self, card): self.cards.append(card)
    def total(self):
        total = sum(CARD_VALUES.get(c,0) for c in self.cards)
        if 'A' in self.cards and total+10<=21: return total+10
        return total
    def is_soft(self): return 'A' in self.cards and self.total()!=sum(CARD_VALUES[c] for c in self.cards)
    def is_pair(self): return len(self.cards)==2 and CARD_VALUES[self.cards[0]]==CARD_VALUES[self.cards[1]]
    def is_bust(self): return self.total()>21
    def is_blackjack(self): return len(self.cards)==2 and 'A' in self.cards and any(c in TEN_RANKS for c in self.cards if c!='A')

# ------------------------------
# Splash Dialog
# ------------------------------
class SplashDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("EZ Blackjack Solver - Welcome")
        self.resize(1000, 790)  # slightly larger than before
        self.setStyleSheet("""
            QDialog { background-color: #0f3d1e; }
            QLabel  { color: white; }
            QPushButton#startBtn {
                background: #ffd60a; color: black; font-weight: 700;
                padding: 10px 18px; border-radius: 8px;
            }
            QPushButton#startBtn:hover { background: #ffe066; }
        """)
        layout = QVBoxLayout(self)
        scroll = QScrollArea(self); scroll.setWidgetResizable(True); layout.addWidget(scroll,1)
        content = QWidget(); scroll.setWidget(content)
        v = QVBoxLayout(content); v.setAlignment(Qt.AlignTop)

        title = QLabel("Welcome to EZ Blackjack Solver")
        title.setFont(QFont("Arial", 22, QFont.Bold)); title.setStyleSheet("color: #ffd60a;")
        v.addWidget(title)

        body = QLabel("This is a simple blackjack assistant that determines optimal strategy decisions...")
        body.setWordWrap(True); v.addWidget(body)

        warn = QLabel("Never take insurance or even money!")
        warn.setStyleSheet("color:red; font-weight:700;"); v.addWidget(warn)

        # Donation section
        donate = QLabel('Enjoying this solver? I accept tips! '
                        'BTC: bc1quhq2mw86m90jxkuzlw86l7p8gv2zg908kdjug3')
        donate.setAlignment(Qt.AlignCenter)
        donate.setFont(QFont("Arial", 9))
        donate.setStyleSheet("color: #bbbbbb;")
        donate.setTextInteractionFlags(Qt.TextSelectableByMouse)
        v.addWidget(donate)

        # QR button
        qr_button = QPushButton("View QR")
        qr_button.setFixedWidth(80)
        qr_button.setStyleSheet("""
            QPushButton { background: #444; color: white; font: 10pt Arial; border-radius: 6px; padding: 4px; }
            QPushButton:hover { background: #666; }
        """)
        qr_button.clicked.connect(lambda: self.show_qr(resource_path("btc_qr.jpg")))
        v.addWidget(qr_button, alignment=Qt.AlignCenter)

        start = QPushButton("Start"); start.setObjectName("startBtn")
        start.clicked.connect(self.accept); layout.addWidget(start)

    def show_qr(self, path):
        qr_dialog = QDialog(self); qr_dialog.setWindowTitle("BTC QR Code"); qr_dialog.resize(300,300)
        layout = QVBoxLayout(qr_dialog)
        qr_label = QLabel(); qr_label.setAlignment(Qt.AlignCenter)
        pixmap = QPixmap(path).scaled(280,280,Qt.KeepAspectRatio,Qt.SmoothTransformation)
        qr_label.setPixmap(pixmap)
        layout.addWidget(qr_label)

        # Add copy button
        copy_btn = QPushButton("Copy BTC Address")
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText("bc1quhq2mw86m90jxkuzlw86l7p8gv2zg908kdjug3"))
        layout.addWidget(copy_btn, alignment=Qt.AlignCenter)

        qr_dialog.exec()

# ------------------------------
# Main Window
# ------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EZ Blackjack Solver v3.6 (PySide6)")
        self.resize(1100, 750)

        self.hands=[Hand("Player")]
        self.current_hand_index=0
        self.dealer_card=None
        self.split_mode=False
        self.stage='player'

        central=QWidget(); self.setCentralWidget(central)
        self.main=QVBoxLayout(central)

        self.recommend=QLabel("Recommendation will appear here")
        self.recommend.setAlignment(Qt.AlignCenter)
        self.recommend.setStyleSheet("color:yellow; font:700 20px Arial; background:#234d20; padding:14px; border-radius:8px;")
        self.main.addWidget(self.recommend)

        self.insurance_reminder=QLabel("")
        self.insurance_reminder.setAlignment(Qt.AlignCenter)
        self.insurance_reminder.setFont(QFont("Arial",14,QFont.Bold))
        self.insurance_reminder.setStyleSheet("color:red;")
        self.insurance_reminder.hide()
        self.main.addWidget(self.insurance_reminder)

        self.instruction=QLabel("Click player cards, then dealer card")
        self.instruction.setAlignment(Qt.AlignCenter)
        self.instruction.setStyleSheet("color:#ccc; font:700 15px Arial;")
        self.main.addWidget(self.instruction)

        # Card rows
        card_frame=QVBoxLayout()
        card_label=QLabel("Select a card:"); card_label.setAlignment(Qt.AlignCenter)
        card_label.setStyleSheet("color:white; font:700 16px Arial;")
        card_frame.addWidget(card_label)

        # top row (2-9) with side padding
        top_row=QHBoxLayout(); top_row.addStretch(1)
        for r in ['2','3','4','5','6','7','8','9']:
            b=self.make_card_button(r); top_row.addWidget(b)
        top_row.addStretch(1); card_frame.addLayout(top_row)

        # bottom row (10-A) with side padding
        bottom_row=QHBoxLayout(); bottom_row.addStretch(1)
        for r in ['10','J','Q','K','A']:
            b=self.make_card_button(r); bottom_row.addWidget(b)
        bottom_row.addStretch(1); card_frame.addLayout(bottom_row)

        self.main.addLayout(card_frame)

        self.info_container=QVBoxLayout(); self.main.addLayout(self.info_container)

    def make_card_button(self, rank):
        b=QPushButton(rank); b.setFixedSize(80,60)
        b.setStyleSheet("QPushButton{background:#2f2f2f;color:white;font:700 18px Arial;border-radius:8px;} QPushButton:hover{background:#3a3a3a;}")
        b.clicked.connect(lambda checked=False, r=rank: self.on_card_clicked(r))
        return b

    def on_card_clicked(self,rank):
        self.dealer_card=rank
        if self.dealer_card=="A":
            self.insurance_reminder.setText('Reminder: Never take insurance or "even money."')
            self.insurance_reminder.show()
        else: self.insurance_reminder.hide()
        self.refresh_info()

    def refresh_info(self):
        while self.info_container.count():
            item=self.info_container.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for i,h in enumerate(self.hands):
            panel=QFrame()
            is_active=(i==self.current_hand_index and self.split_mode)
            if is_active:
                panel.setStyleSheet("QFrame{background:#2a2a1f;border:3px solid yellow;border-radius:10px;padding:12px;}")
            else:
                panel.setStyleSheet("QFrame{background:#222;border-radius:10px;padding:12px;}")
            inner=QVBoxLayout(panel)
            name_line=QLabel(f"{h.name}: {h.total()}" + (f" vs Dealer: {self.dealer_card}" if self.dealer_card else ""))
            name_line.setAlignment(Qt.AlignCenter); name_line.setStyleSheet("color:white;font:700 18px Arial;")
            inner.addWidget(name_line)
            if h.cards:
                cards=QLabel(f"Cards: {', '.join(h.cards)}"); cards.setAlignment(Qt.AlignCenter)
                cards.setStyleSheet("color:#ddd;font:16px Arial;"); inner.addWidget(cards)
            self.info_container.addWidget(panel)

# ------------------------------
def main():
    app=QApplication(sys.argv)
    splash=SplashDialog()
    if splash.exec()!=QDialog.Accepted: sys.exit(0)
    win=MainWindow(); win.show()
    sys.exit(app.exec())

if __name__=="__main__": main()
