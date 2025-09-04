# ez_blackjack_solver_v3_2_full.py
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QScrollArea, QDialog, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# ------------------------------
# Strategy Engine Configuration
# ------------------------------
CARD_VALUES = {'A':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':10,'Q':10,'K':10}
TEN_RANKS = {'10','J','Q','K'}
RANKS = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']

HARD_STRATEGY = {
    17:{2:'S',3:'S',4:'S',5:'S',6:'S',7:'S',8:'S',9:'S',10:'S','A':'S'},
    16:{2:'S',3:'S',4:'S',5:'S',6:'S',7:'H',8:'H',9:'H',10:'H','A':'H'},
    15:{2:'S',3:'S',4:'S',5:'S',6:'S',7:'H',8:'H',9:'H',10:'H','A':'H'},
    14:{2:'S',3:'S',4:'S',5:'S',6:'S',7:'H',8:'H',9:'H',10:'H','A':'H'},
    13:{2:'S',3:'S',4:'S',5:'S',6:'S',7:'H',8:'H',9:'H',10:'H','A':'H'},
    12:{2:'H',3:'H',4:'S',5:'S',6:'S',7:'H',8:'H',9:'H',10:'H','A':'H'},
    11:{2:'D',3:'D',4:'D',5:'D',6:'D',7:'D',8:'D',9:'D',10:'D','A':'H'},
    10:{2:'D',3:'D',4:'D',5:'D',6:'D',7:'D',8:'D',9:'D',10:'H','A':'H'},
    9: {2:'H',3:'D',4:'D',5:'D',6:'D',7:'H',8:'H',9:'H',10:'H','A':'H'},
    8: {2:'H',3:'H',4:'H',5:'H',6:'H',7:'H',8:'H',9:'H',10:'H','A':'H'}
}

SOFT_STRATEGY = {
    'A,9': {2:'S',3:'S',4:'S',5:'S',6:'S',7:'S',8:'S',9:'S',10:'S','A':'S'},
    'A,8': {2:'S',3:'S',4:'S',5:'S',6:'S',7:'S',8:'S',9:'S',10:'S','A':'S'},
    'A,7': {2:'S',3:'Ds',4:'Ds',5:'Ds',6:'Ds',7:'S',8:'S',9:'H',10:'H','A':'H'},
    'A,6': {2:'H',3:'D',4:'D',5:'D',6:'D',7:'H',8:'H',9:'H',10:'H','A':'H'},
    'A,5': {2:'H',3:'H',4:'D',5:'D',6:'D',7:'H',8:'H',9:'H',10:'H','A':'H'},
    'A,4': {2:'H',3:'H',4:'D',5:'D',6:'D',7:'H',8:'H',9:'H',10:'H','A':'H'},
    'A,3': {2:'H',3:'H',4:'H',5:'D',6:'D',7:'H',8:'H',9:'H',10:'H','A':'H'},
    'A,2': {2:'H',3:'H',4:'H',5:'D',6:'D',7:'H',8:'H',9:'H',10:'H','A':'H'}
}

PAIR_STRATEGY = {
    'A,A': {2:'P',3:'P',4:'P',5:'P',6:'P',7:'P',8:'P',9:'P',10:'P','A':'P'},
    'T,T': {2:'S',3:'S',4:'S',5:'S',6:'S',7:'S',8:'S',9:'S',10:'S','A':'S'},
    '9,9': {2:'P',3:'P',4:'P',5:'P',6:'P',7:'S',8:'P',9:'P',10:'S','A':'S'},
    '8,8': {2:'P',3:'P',4:'P',5:'P',6:'P',7:'P',8:'P',9:'P',10:'P','A':'P'},
    '7,7': {2:'P',3:'P',4:'P',5:'P',6:'P',7:'P',8:'S',9:'S',10:'S','A':'S'},
    '6,6': {2:'H',3:'P',4:'P',5:'P',6:'P',7:'S',8:'S',9:'S',10:'S','A':'S'},
    '5,5': {2:'D',3:'D',4:'D',5:'D',6:'D',7:'D',8:'D',9:'D',10:'H','A':'H'},
    '4,4': {2:'H',3:'H',4:'H',5:'P',6:'P',7:'H',8:'H',9:'H',10:'H','A':'H'},
    '3,3': {2:'H',3:'P',4:'P',5:'P',6:'P',7:'P',8:'S',9:'S',10:'S','A':'S'},
    '2,2': {2:'H',3:'P',4:'P',5:'P',6:'P',7:'P',8:'S',9:'S',10:'S','A':'S'}
}

ACTION_NAMES = {
    'H': 'Hit',
    'S': 'Stand',
    'D': 'Double (or Hit if not allowed)',
    'Ds': 'Double (or Stand if not allowed)',
    'P': 'Split',
    'BUST': 'Bust',
    'BJ': 'Blackjack!'
}

# ------------------------------
# Hand model & helper functions
# ------------------------------
class Hand:
    def __init__(self, name="Player"):
        self.cards = []
        self.name = name
        self.skip_pair = False  # set True when refuse split

    def add_card(self, card):
        self.cards.append(card)

    def total(self):
        total = sum(CARD_VALUES.get(c, 0) for c in self.cards)
        if 'A' in self.cards and total + 10 <= 21:
            return total + 10
        return total

    def is_soft(self):
        return 'A' in self.cards and self.total() != sum(CARD_VALUES.get(c, 0) for c in self.cards)

    def is_pair(self):
        if self.skip_pair or len(self.cards) != 2:
            return False
        return CARD_VALUES.get(self.cards[0], 0) == CARD_VALUES.get(self.cards[1], 0)

    def is_bust(self):
        return self.total() > 21

    def is_blackjack(self):
        if len(self.cards) != 2:
            return False
        has_ace = 'A' in self.cards
        has_ten = any(c in TEN_RANKS for c in self.cards if c != 'A')
        return has_ace and has_ten

def normalize_pair_key(cards):
    if len(cards) != 2: return None
    if CARD_VALUES.get(cards[0]) != CARD_VALUES.get(cards[1]): return None
    if cards[0] == 'A' and cards[1] == 'A': return 'A,A'
    if CARD_VALUES[cards[0]] == 10: return 'T,T'
    return f"{cards[0]},{cards[1]}"

def soft_key_from_total(hand):
    if not hand.is_soft(): return None
    other = hand.total() - 11
    other = max(2, min(other, 9))
    return f"A,{other}"

def norm_dealer_key(rank):
    if rank == 'A': return 'A'
    if rank in TEN_RANKS: return 10
    try: return int(rank)
    except: return rank

def relabel_hands(hands):
    if len(hands) == 1:
        hands[0].name = "Player"
    else:
        for i, h in enumerate(hands):
            h.name = f"Hand {i+1}"

# ------------------------------
# Splash Dialog (scrollable)
# ------------------------------
class SplashDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("EZ Blackjack Solver - Welcome")
        # 10% larger than prior (was 900x700)
        self.resize(990, 770)
        self.setStyleSheet("""
            QDialog { background-color: #0f3d1e; }
            QLabel  { color: white; }
            QPushButton#startBtn {
                background: #ffd60a; color: black; font-weight: 700;
                padding: 10px 18px; border-radius: 8px;
            }
            QPushButton#startBtn:hover { background: #ffe066; }
        """)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 12)
        outer.setSpacing(10)

        # Scroll area
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        outer.addWidget(scroll, 1)

        content = QWidget()
        scroll.setWidget(content)
        v = QVBoxLayout(content)
        v.setContentsMargins(20, 12, 20, 12)
        v.setSpacing(10)
        v.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        # Logo cluster
        logo1 = QLabel("♠ ♣")
        logo1.setAlignment(Qt.AlignCenter)
        logo1.setStyleSheet("color: white;")
        logo1.setFont(QFont("Arial", 26))
        v.addWidget(logo1)

        logo2 = QLabel("♦ ♥")
        logo2.setAlignment(Qt.AlignCenter)
        logo2.setStyleSheet("color: #ff4d4d;")
        logo2.setFont(QFont("Arial", 26))
        v.addWidget(logo2)

        # Title
        title = QLabel("Welcome to EZ Blackjack Solver")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 22, QFont.Bold))
        title.setStyleSheet("color: #ffd60a;")
        v.addWidget(title)
        v.addSpacing(8)

        def header(text):
            h = QLabel(text)
            h.setAlignment(Qt.AlignCenter)
            h.setFont(QFont("Arial", 16, QFont.Bold))
            return h

        def para(text, emphasize=False):
            p = QLabel(text)
            p.setWordWrap(True)
            p.setAlignment(Qt.AlignHCenter)
            p.setFont(QFont("Arial", 12, QFont.Bold if emphasize else QFont.Normal))
            if emphasize:
                p.setStyleSheet("color: #ff4d4d;")
            return p

        v.addWidget(para("This is a simple blackjack assistant that determines the optimal strategy decisions while playing blackjack online."))

        v.addSpacing(8)
        v.addWidget(header("How to Use"))
        v.addWidget(para(
            'First, input both of your cards as prompted, then select the dealer\'s up-card. The program will show your total and suggest the optimal strategy (hit, stand, split, etc). '
            'In the case of a suggested hit or split, the program will prompt you to enter the values of your additional cards before determining any further suggested action.\n\n'
            'Click "Clear" at the end of the hand to start a new hand - the program does not store any data or keep a running total of any kind.'
        ))

        v.addWidget(para('Never take insurance or "even money" if offered.', emphasize=True))

        v.addSpacing(8)
        v.addWidget(header("Strategy Explanation"))
        v.addWidget(para(
            "The strategy in this program is based entirely on standard S17 blackjack hand charts, which are derived from the known mathematics of multi-deck blackjack. "
            "There is no cutting-edge technology being utilized in this program. It's just simplifying the use of hand charts."
        ))

        v.addSpacing(8)
        v.addWidget(header("Does this program count cards?"))
        v.addWidget(para(
            "No. Card counting is largely useless in modern internet casino play with massive shoes that are changed regularly. Blackjack games offered on casino websites without a live dealer (essentially just video games) are based on RNG, "
            "which renders card counting entirely useless as the deck size is effectively infinite."
        ))

        v.addStretch(1)

        # Start button pinned at bottom (outside scroll)
        start_row = QHBoxLayout()
        start_row.addStretch(1)
        start_btn = QPushButton("Start")
        start_btn.setObjectName("startBtn")
        start_btn.setFixedWidth(200)
        start_btn.clicked.connect(self.accept)
        start_row.addWidget(start_btn)
        start_row.addStretch(1)
        outer.addLayout(start_row)

# ------------------------------
# Main Window (full feature)
# ------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EZ Blackjack Solver v3.2")
        self.resize(1100, 750)

        # State
        self.hands = [Hand("Player")]
        self.current_hand_index = 0
        self.dealer_card = None
        self.split_mode = False
        self.stage = 'player'  # 'player','dealer','hitting','action'

        # Central widget / layout
        central = QWidget()
        self.setCentralWidget(central)
        self.main = QVBoxLayout(central)
        self.main.setContentsMargins(16, 12, 16, 12)
        self.main.setSpacing(12)

        # Title
        title = QLabel("EZ Blackjack Solver")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 24, QFont.Bold))
        self.main.addWidget(title)

        # Recommendation banner
        self.recommend = QLabel("Recommendation will appear here")
        self.recommend.setAlignment(Qt.AlignCenter)
        self.recommend.setWordWrap(True)
        self.recommend.setMinimumHeight(60)
        self.recommend.setStyleSheet("""
            QLabel {
                background-color: #234d20;
                color: #ffd60a;
                border-radius: 8px;
                padding: 14px;
                font: 700 20px "Arial";
            }
        """)
        self.main.addWidget(self.recommend)

        # Insurance reminder (hidden by default)
        self.insurance_reminder = QLabel("")
        self.insurance_reminder.setAlignment(Qt.AlignCenter)
        self.insurance_reminder.setFont(QFont("Arial", 14, QFont.Bold))
        self.insurance_reminder.setStyleSheet("color: red;")
        self.insurance_reminder.setVisible(False)
        self.main.addWidget(self.insurance_reminder)

        # Instruction label (below banner)
        self.instruction = QLabel("Click player cards, then dealer card")
        self.instruction.setAlignment(Qt.AlignCenter)
        self.instruction.setFont(QFont("Arial", 15, QFont.Bold))
        self.instruction.setStyleSheet("color: #cccccc;")
        self.main.addWidget(self.instruction)

        # Card rows header
        card_label = QLabel("Select a card:")
        card_label.setAlignment(Qt.AlignCenter)
        card_label.setFont(QFont("Arial", 14, QFont.Bold))
        card_label.setStyleSheet("color: white;")
        self.main.addWidget(card_label)

        # Card grid: two rows (2-9) and (10,J,Q,K,A)
        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        self.card_buttons = []
        for r in ['2','3','4','5','6','7','8','9']:
            b = QPushButton(r)
            b.setFixedSize(80, 60)
            b.setStyleSheet("""
                QPushButton { background: #2f2f2f; color: white; border-radius: 8px; font: 700 18px "Arial"; }
                QPushButton:hover { background: #3a3a3a; }
                QPushButton:pressed { background: #4a4a4a; }
            """)
            b.clicked.connect(lambda checked=False, rank=r: self.on_card_clicked(rank))
            top_row.addWidget(b)
            self.card_buttons.append(b)
        self.main.addLayout(top_row)

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(3)  # reduced spacing by ~50%
        for r in ['10','J','Q','K','A']:
            b = QPushButton(r)
            b.setFixedSize(80, 60)
            b.setStyleSheet("""
                QPushButton { background: #2f2f2f; color: white; border-radius: 8px; font: 700 18px "Arial"; }
                QPushButton:hover { background: #3a3a3a; }
                QPushButton:pressed { background: #4a4a4a; }
            """)
            b.clicked.connect(lambda checked=False, rank=r: self.on_card_clicked(rank))
            bottom_row.addWidget(b)
            self.card_buttons.append(b)
        self.main.addLayout(bottom_row)

        # Split counter
        self.counter_label = QLabel("")
        self.counter_label.setAlignment(Qt.AlignCenter)
        self.counter_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.counter_label.setStyleSheet("color: #cccccc;")
        self.main.addWidget(self.counter_label)

        # Info panels area (centered totals/cards)
        self.info_container = QVBoxLayout()
        self.info_container.setSpacing(10)
        self.main.addLayout(self.info_container)

        # Dynamic controls container (confirm/refuse + play-hand rows)
        self.dynamic_container = QVBoxLayout()
        self.main.addLayout(self.dynamic_container)
        self.confirm_widget = None
        self.playhand_widget = None
        self.playhand_buttons = []

        # Bottom row with Clear (anchored at bottom)
        bottom = QHBoxLayout()
        bottom.addStretch(1)
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setFixedWidth(140)
        self.clear_btn.setStyleSheet("""
            QPushButton { background: #b22222; color: white; border-radius: 6px; padding: 8px; }
            QPushButton:hover { background: #c63a3a; }
        """)
        self.clear_btn.clicked.connect(self.reset)
        bottom.addWidget(self.clear_btn)
        self.main.addLayout(bottom)

        # Initial render
        self.refresh_info()

    # ----------------- Input handlers -----------------
    def on_card_clicked(self, rank):
        # Stage handling: 'player' -> add to player's current hand; 'dealer' -> set dealer; 'hitting' -> add card
        hand = self.hands[self.current_hand_index]
        if self.stage == 'player':
            hand.add_card(rank)
            if len(hand.cards) == 2:
                self.stage = 'dealer'
                self.instruction.setText("Click dealer up-card")
            self.refresh_info()
        elif self.stage == 'dealer':
            self.dealer_card = rank
            # insurance reminder toggle
            if self.dealer_card == 'A':
                self.insurance_reminder.setText('Reminder: Never take insurance or "even money."')
                self.insurance_reminder.setVisible(True)
            else:
                self.insurance_reminder.setVisible(False)
            self.show_strategy()
        elif self.stage == 'hitting':
            hand.add_card(rank)
            self.show_strategy()
        # if 'action' stage, ignore card clicks

    # ---------------- Strategy / Decision Logic ----------------
    def get_action_code(self, hand, dealer):
        dealer_key = norm_dealer_key(dealer)
        if hand.is_blackjack():
            return 'BJ'
        if hand.is_bust():
            return 'BUST'
        if hand.is_pair():
            key = normalize_pair_key(hand.cards)
            if key and key in PAIR_STRATEGY:
                return PAIR_STRATEGY[key].get(dealer_key, 'H')
        if hand.is_soft():
            skey = soft_key_from_total(hand)
            if skey and skey in SOFT_STRATEGY:
                return SOFT_STRATEGY[skey].get(dealer_key, 'H')
        total = hand.total()
        if total in HARD_STRATEGY:
            return HARD_STRATEGY[total].get(dealer_key, 'H')
        return 'S' if total >= 18 else 'H'

    def set_recommend_banner(self, text, mood="neutral"):
        bg = {
            "neutral": "#234d20",
            "hit": "#642323",
            "stand": "#234d20",
            "split": "#2a3e6b",
            "bust": "#5a1f1f",
            "bj": "#205a2a",
            "double": "#4b3f14"
        }.get(mood, "#234d20")
        self.recommend.setStyleSheet(f"""
            QLabel {{
                background-color: {bg};
                color: #ffd60a;
                border-radius: 8px;
                padding: 14px;
                font: 700 20px "Arial";
            }}
        """)
        self.recommend.setText(text)

    def show_strategy(self):
        # remove any confirm/refuse controls until needed
        self.clear_dynamic_controls()

        if self.dealer_card is None:
            return
        hand = self.hands[self.current_hand_index]
        code = self.get_action_code(hand, self.dealer_card)

        # Toggle insurance reminder
        if self.dealer_card == "A":
            self.insurance_reminder.setText('Reminder: Never take insurance or "even money."')
            self.insurance_reminder.setVisible(True)
        else:
            self.insurance_reminder.setVisible(False)

        if code == 'BUST':
            self.set_recommend_banner("Bust.", "bust")
            self.stage = 'action'
        elif code == 'BJ':
            self.set_recommend_banner("Blackjack!", "bj")
            self.stage = 'action'
        elif code == 'H':
            self.set_recommend_banner("Player should: HIT — please click next card.", "hit")
            self.stage = 'hitting'
        elif code == 'S':
            self.set_recommend_banner("Player should: STAND.", "stand")
            self.stage = 'action'
        elif code == 'P':
            self.set_recommend_banner("Player should: SPLIT.", "split")
            self.add_split_confirm_controls()
            self.stage = 'action'
        elif code in ('D', 'Ds'):
            # Double advice only valid for two-card hands; otherwise fallback
            if len(hand.cards) > 2:
                fallback = "HIT." if code == 'D' else "STAND."
                self.set_recommend_banner(f"Player should: {fallback}", "double")
                self.stage = 'hitting' if code == 'D' else 'action'
            else:
                fallback = "HIT." if code == 'D' else "STAND."
                self.set_recommend_banner(f"Player should: DOUBLE. If not allowed, {fallback}", "double")
                self.stage = 'hitting' if code == 'D' else 'action'
        else:
            self.set_recommend_banner(ACTION_NAMES.get(code, str(code)), "neutral")
            self.stage = 'action'

        self.refresh_info()

    # ---------------- Split UI & logic ----------------
    def add_split_confirm_controls(self):
        # destroy existing confirm widget if present
        if self.confirm_widget:
            self.confirm_widget.deleteLater()
            self.confirm_widget = None

        widget = QWidget()
        h = QHBoxLayout(widget)
        h.setSpacing(8)
        h.setContentsMargins(0, 0, 0, 0)

        confirm = QPushButton("Confirm Split")
        confirm.setFixedWidth(150)
        confirm.setStyleSheet("""
            QPushButton { background: #2a3e6b; color: white; border-radius: 6px; padding: 8px; }
            QPushButton:hover { background: #35518c; }
        """)
        confirm.clicked.connect(self.perform_split)
        h.addWidget(confirm)

        refuse = QPushButton("Refuse Split")
        refuse.setFixedWidth(150)
        refuse.setStyleSheet("""
            QPushButton { background: #444; color: white; border-radius: 6px; padding: 8px; }
            QPushButton:hover { background: #555; }
        """)
        refuse.clicked.connect(self.refuse_split)
        h.addWidget(refuse)

        # add to dynamic container (above Clear)
        self.dynamic_container.addWidget(widget)
        self.confirm_widget = widget

    def perform_split(self):
        idx = self.current_hand_index
        hand = self.hands[idx]
        if not hand.is_pair():
            return
        if len(self.hands) >= 4:
            return  # max 4 hands allowed

        c1, c2 = hand.cards
        # replace hand with two single-card hands
        self.hands.pop(idx)
        new1, new2 = Hand(), Hand()
        new1.add_card(c1)
        new2.add_card(c2)
        # insert so new1 is left, new2 right
        self.hands.insert(idx, new2)
        self.hands.insert(idx, new1)
        relabel_hands(self.hands)
        self.split_mode = True
        self.current_hand_index = idx

        # remove confirm widget
        if self.confirm_widget:
            self.confirm_widget.deleteLater()
            self.confirm_widget = None

        # add play-hand controls
        self.add_play_hand_controls()
        self.refresh_info()
        if self.dealer_card:
            self.show_strategy()

    def refuse_split(self):
        self.hands[self.current_hand_index].skip_pair = True
        if self.confirm_widget:
            self.confirm_widget.deleteLater()
            self.confirm_widget = None
        self.show_strategy()

    def add_play_hand_controls(self):
        # remove existing playhand widget if any
        if self.playhand_widget:
            self.playhand_widget.deleteLater()
            self.playhand_widget = None
            self.playhand_buttons = []

        widget = QWidget()
        h = QHBoxLayout(widget)
        h.setSpacing(8)
        h.setContentsMargins(0, 0, 0, 0)

        for i in range(len(self.hands)):
            b = QPushButton(f"Play Hand {i+1}")
            b.setFixedWidth(130)
            b.setStyleSheet("""
                QPushButton { background: #2f2f2f; color: white; border-radius: 6px; padding: 8px; font: 700 12px "Arial"; }
                QPushButton:hover { background: #3a3a3a; }
            """)
            b.clicked.connect(lambda checked=False, idx=i: self.switch_hand(idx))
            h.addWidget(b)
            self.playhand_buttons.append(b)

        self.dynamic_container.addWidget(widget)
        self.playhand_widget = widget
        self.update_playhand_button_styles()
        self.update_split_counter()

    def update_playhand_button_styles(self):
        for i, btn in enumerate(self.playhand_buttons):
            if i == self.current_hand_index:
                # yellow underline style
                btn.setStyleSheet("""
                    QPushButton { background: #2f2f2f; color: white; border-radius: 6px; padding: 8px; font: 700 12px "Arial";
                                  border-bottom: 4px solid yellow; }
                    QPushButton:hover { background: #3a3a3a; }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton { background: #2f2f2f; color: white; border-radius: 6px; padding: 8px; font: 700 12px "Arial"; }
                    QPushButton:hover { background: #3a3a3a; }
                """)

    def switch_hand(self, idx):
        if not self.split_mode:
            return
        if idx < 0 or idx >= len(self.hands):
            return
        self.current_hand_index = idx
        relabel_hands(self.hands)
        self.instruction.setText(f"Now playing {self.hands[idx].name}. Click a card to add.")
        self.update_playhand_button_styles()
        self.refresh_info()
        if self.dealer_card:
            self.show_strategy()

    def clear_dynamic_controls(self):
        if self.confirm_widget:
            self.confirm_widget.deleteLater()
            self.confirm_widget = None
        if self.playhand_widget:
            self.playhand_widget.deleteLater()
            self.playhand_widget = None
            self.playhand_buttons = []

    # ------------------ UI refresh ------------------
    def refresh_info(self):
        # Clear info_container
        def clear_layout(layout):
            while layout.count():
                item = layout.takeAt(0)
                w = item.widget()
                if w:
                    w.deleteLater()
                else:
                    sub = item.layout()
                    if sub:
                        clear_layout(sub)
        clear_layout(self.info_container)

        # Rebuild hand panels with outer-only yellow highlight when active
        for i, h in enumerate(self.hands):
            panel = QFrame()
            panel.setFrameShape(QFrame.NoFrame)
            is_active = (i == self.current_hand_index and self.split_mode)
            if is_active:
                # full yellow rectangle (outer only)
                panel.setStyleSheet("""
                    QFrame { background: #2a2a1f; border: 3px solid yellow; border-radius: 10px; padding: 12px; }
                """)
            else:
                panel.setStyleSheet("""
                    QFrame { background: #222; border-radius: 10px; padding: 12px; }
                """)
            inner = QVBoxLayout(panel)
            inner.setContentsMargins(0, 0, 0, 0)
            inner.setSpacing(8)

            # Name + total centered and larger
            name_line = QLabel(f"{h.name}: {h.total()}" + (f"  vs Dealer: {self.dealer_card}" if self.dealer_card else ""))
            name_line.setFont(QFont("Arial", 16, QFont.Bold))
            name_line.setStyleSheet("color: white;")
            name_line.setAlignment(Qt.AlignCenter)
            inner.addWidget(name_line)

            # Cards list centered, slightly larger
            if h.cards:
                cards = QLabel(f"Cards: {', '.join(h.cards)}")
                cards.setStyleSheet("color: #ddd;")
                cards.setFont(QFont("Arial", 14))
                cards.setAlignment(Qt.AlignCenter)
                inner.addWidget(cards)

            self.info_container.addWidget(panel)

        # After split, ensure play-hand controls are visible
        if self.split_mode and self.playhand_widget is None:
            self.add_play_hand_controls()

        self.update_split_counter()

    def update_split_counter(self):
        if self.split_mode and len(self.hands) > 1:
            self.counter_label.setText(f"Currently managing {len(self.hands)} hands")
        else:
            self.counter_label.setText("")

    # ------------------ Reset ------------------
    def reset(self):
        self.clear_dynamic_controls()
        self.hands = [Hand("Player")]
        self.current_hand_index = 0
        self.dealer_card = None
        self.split_mode = False
        self.stage = 'player'
        self.instruction.setText("Click player cards, then dealer card")
        self.set_recommend_banner("Recommendation will appear here", "neutral")
        self.insurance_reminder.setVisible(False)
        self.counter_label.setText("")
        self.refresh_info()

# ------------------------------
# App entry
# ------------------------------
def main():
    app = QApplication(sys.argv)

    splash = SplashDialog()
    if splash.exec() != QDialog.Accepted:
        sys.exit(0)

    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
