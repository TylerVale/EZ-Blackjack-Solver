# ez_blackjack_solver_v2_0.py
import tkinter as tk        # used for canvas/scrolling and some low-level widgets
import customtkinter as ctk

# -------------------------
# Setup CustomTkinter theme
# -------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# --- Config & constants ---
DAS = True  # placeholder in config

CARD_VALUES = {'A':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9,'10':10,'J':10,'Q':10,'K':10}
TEN_RANKS = {'10','J','Q','K'}
RANKS = ['A','2','3','4','5','6','7','8','9','10','J','Q','K']

# --- Strategy tables (S17) ---
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

# -----------------------
# Hand model & helpers
# -----------------------
class Hand:
    def __init__(self, name="Player"):
        self.cards = []
        self.name = name
        self.skip_pair = False

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
        v0 = CARD_VALUES.get(self.cards[0], None)
        v1 = CARD_VALUES.get(self.cards[1], None)
        return v0 is not None and v0 == v1

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

# -----------------------
# Splash Screen (CTk + scrollable Canvas)
# -----------------------
class SplashScreen(ctk.CTkToplevel):
    """
    A CTk-based splash implemented as a Toplevel window with a scrollable Canvas inside.
    The caller creates a CTk root, then creates SplashScreen(root, on_start=callable).
    """
    def __init__(self, master, on_start, width=800, height=650):
        super().__init__(master)
        self.title("EZ Blackjack Solver - Welcome")
        self.geometry(f"{width}x{height}")
        self.configure(fg_color="darkgreen")

        # modal-ish: prevent interaction with master until closed
        self.transient(master)
        self.grab_set()

        # top logo + title area inside a content canvas so it's scrollable
        container = tk.Frame(self, bg="darkgreen")
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg="darkgreen", highlightthickness=0)
        vsb = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        content = tk.Frame(canvas, bg="darkgreen")
        canvas.create_window((0,0), window=content, anchor="nw")

        # update scrollregion whenever content changes
        def on_config(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        content.bind("<Configure>", on_config)

        # Enable mousewheel scrolling (Windows/Mac/Linux)
        def _on_mousewheel(event):
            # event.delta on Windows/Mac; Button-4/5 for many Linux setups
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
            else:
                # typical Windows / Mac
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        # bind both platform patterns
        canvas.bind_all("<MouseWheel>", _on_mousewheel)   # Windows / Mac
        canvas.bind_all("<Button-4>", _on_mousewheel)     # Linux scroll up
        canvas.bind_all("<Button-5>", _on_mousewheel)     # Linux scroll down

        # --- content (centered) ---
        # logo cluster
        logo_frame = tk.Frame(content, bg="darkgreen")
        logo_frame.pack(pady=(20, 6))
        tk.Label(logo_frame, text="♠ ♣", font=("Arial", 26), fg="white", bg="darkgreen").pack()
        tk.Label(logo_frame, text="♦ ♥", font=("Arial", 26), fg="red", bg="darkgreen").pack()

        # title
        tk.Label(content, text="Welcome to EZ Blackjack Solver",
                 font=("Arial", 22, "bold"), fg="yellow", bg="darkgreen").pack(pady=(12, 14))

        # sections (headers bold + centered)
        sections = [
            ("", "This is a simple blackjack assistant that determines the optimal strategy decisions while playing blackjack online."),
            ("How to Use", "First, input both of your cards as prompted, then select the dealer's up-card. The program will show your total and suggest the optimal strategy (hit, stand, split, etc). In the case of a suggested hit or split, the program will prompt you to enter the values of your additional cards before determining any further suggested action.\n\nClick \"Clear\" at the end of the hand to start a new hand - the program does not store any data or keep a running total of any kind."),
            ("", "Never take insurance or \"even money\" if offered."),
            ("Strategy Explanation", "The strategy in this program is based entirely on standard S17 blackjack hand charts, which are derived from the known mathematics of multi-deck blackjack. There is no cutting-edge technology being utilized in this program. It's just simplifying the use of hand charts."),
            ("Does this program count cards?", "No. Card counting is largely useless in modern internet casino play with massive shoes that are changed regularly. Blackjack games offered on casino websites without a live dealer (essentially just video games) are based on RNG, which renders card counting entirely useless as the deck size is effectively infinite.")
        ]

        for header, text in sections:
            if header:
                tk.Label(content, text=header, font=("Arial", 16, "bold"), fg="white", bg="darkgreen").pack(pady=(12,6))
            # "Never take insurance..." needs emphasis
            if "insurance" in text:
                tk.Label(content, text=text, wraplength=720, justify="center",
                         font=("Arial", 12, "bold"), fg="red", bg="darkgreen").pack(padx=20, pady=(0,8))
            else:
                tk.Label(content, text=text, wraplength=720, justify="center",
                         font=("Arial", 12), fg="white", bg="darkgreen").pack(padx=20, pady=4)

        # fixed start button anchored at bottom of the splash (outside canvas)
        start_btn = ctk.CTkButton(self, text="Start", width=180, height=44,
                                  fg_color="yellow", text_color="black",
                                  command=lambda: self._on_start(on_start))
        start_btn.pack(side="bottom", pady=12)

        # center the splash on screen
        self.update_idletasks()
        screen_w = self.winfo_screenwidth(); screen_h = self.winfo_screenheight()
        x = (screen_w // 2) - (width//2) if (width := width) else (screen_w//2 - 400)
        y = (screen_h // 2) - (height//2) if (height := height) else (screen_h//2 - 300)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _on_start(self, callback):
        # unbind scroll events and release grab
        self.grab_release()
        try:
            self.destroy()
        except:
            pass
        callback()

# -----------------------
# Main App (CustomTkinter CTk)
# -----------------------
class BlackjackGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("EZ Blackjack Solver v2.0")
        # start somewhat large so splits and controls fit
        self.geometry("980x720")
        self.configure(fg_color="gray15")

        # State
        self.hands = [Hand("Player")]
        self.current_hand_index = 0
        self.dealer_card = None
        self.split_mode = False
        self.stage = 'player'  # 'player', 'dealer', 'hitting', 'action'

        # Top Title
        self.title_label = ctk.CTkLabel(self, text="EZ Blackjack Solver", font=("Arial", 26, "bold"))
        self.title_label.pack(pady=(12,6))

        # Info + recommendation frames
        top_frame = ctk.CTkFrame(self, corner_radius=10)
        top_frame.pack(fill="x", padx=18, pady=(6, 10))

        self.instruction_label = ctk.CTkLabel(top_frame, text="Click player cards, then dealer card",
                                              font=("Arial", 14))
        self.instruction_label.pack(pady=(10,6))

        self.recommend_frame = ctk.CTkFrame(top_frame, corner_radius=8, fg_color="#234d20")
        self.recommend_frame.pack(fill="x", padx=12, pady=(6,12))

        self.recommend_label = ctk.CTkLabel(self.recommend_frame, text="Recommendation will appear here",
                                            font=("Arial", 18, "bold"), text_color="yellow")
        self.recommend_label.pack(pady=10)

        # Info area for showing hands / totals
        self.info_frame = ctk.CTkFrame(self, corner_radius=10)
        self.info_frame.pack(fill="x", padx=18, pady=(2,10))

        # Card grid area
        card_panel = ctk.CTkFrame(self, corner_radius=10)
        card_panel.pack(padx=18, pady=8, fill="x")

        # Create card buttons grid
        self.card_buttons = []
        for i, rank in enumerate(RANKS):
            btn = ctk.CTkButton(card_panel, text=rank, width=72, height=44,
                                command=lambda r=rank: self.select_card(r))
            btn.grid(row=i//7, column=i%7, padx=6, pady=6)
            self.card_buttons.append(btn)

        # Split controls area (populated when split confirmed)
        self.split_controls = None
        self.counter_label = ctk.CTkLabel(self, text="", font=("Arial", 13, "bold"))
        self.counter_label.pack(pady=(6,4))

        # Bottom action row with Clear on right
        bottom_row = ctk.CTkFrame(self, corner_radius=10)
        bottom_row.pack(fill="x", padx=18, pady=12)

        self.clear_btn = ctk.CTkButton(bottom_row, text="Clear", fg_color="#b22222", width=120,
                                       command=self.reset)
        self.clear_btn.pack(side="right", padx=8)

        # initial render
        self.update_info()

    # ----- Input handlers -----
    def select_card(self, card):
        hand = self.hands[self.current_hand_index]
        if self.stage == 'player':
            hand.add_card(card)
            if len(hand.cards) == 2:
                self.stage = 'dealer'
                self.instruction_label.configure(text="Click dealer up-card")
            self.update_info()
        elif self.stage == 'dealer':
            self.dealer_card = card
            self.show_strategy()
        elif self.stage == 'hitting':
            hand.add_card(card)
            self.show_strategy()
        else:
            # 'action' stage: ignore card clicks until clear or switching hands
            pass

    # ----- Strategy/decision logic (same math as previous versions) -----
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
        if total >= 18:
            return 'S'
        return 'H'

    def show_strategy(self):
        # hide split controls until needed
        if self.split_controls:
            try:
                self.split_controls.destroy()
            except:
                pass
            self.split_controls = None

        hand = self.hands[self.current_hand_index]
        if self.dealer_card is None:
            return
        code = self.get_action_code(hand, self.dealer_card)

        if code == 'BUST':
            msg = "Bust."
            self.stage = 'action'
        elif code == 'BJ':
            msg = "Blackjack!"
            self.stage = 'action'
        elif code == 'H':
            msg = "Player should: HIT — please click next card."
            self.stage = 'hitting'
        elif code == 'S':
            msg = "Player should: STAND."
            self.stage = 'action'
        elif code == 'P':
            msg = "Player should: SPLIT."
            # show confirm/refuse controls (within CTk)
            self.show_split_controls()
            self.stage = 'action'
        elif code in ('D', 'Ds'):
            # doubling advice available only for 2-card hands; otherwise fallback
            if len(hand.cards) > 2:
                fallback = 'hit' if code == 'D' else 'stand'
                msg = f"Player should: {fallback.upper()}."
                self.stage = 'hitting' if fallback == 'hit' else 'action'
            else:
                msg = "Player should: DOUBLE. If not allowed, " + ("HIT." if code == 'D' else "STAND.")
                self.stage = 'hitting' if code == 'D' else 'action'
        else:
            msg = ACTION_NAMES.get(code, str(code))
            self.stage = 'action'

        self.recommend_label.configure(text=msg)
        self.update_info()

    # ----- Split UI & logic -----
    def show_split_controls(self):
        # destroy previous if any
        if self.split_controls:
            try:
                self.split_controls.destroy()
            except:
                pass
        self.split_controls = ctk.CTkFrame(self, corner_radius=8)
        # pack above the Clear button (so it's less likely to be mis-clicked)
        self.split_controls.pack(pady=6, before=self.clear_btn)

        confirm_btn = ctk.CTkButton(self.split_controls, text="Confirm Split", width=140,
                                    command=self.perform_split)
        confirm_btn.pack(side="left", padx=8)
        refuse_btn = ctk.CTkButton(self.split_controls, text="Refuse Split", width=140,
                                   command=self.refuse_split)
        refuse_btn.pack(side="left", padx=8)

    def perform_split(self):
        idx = self.current_hand_index
        hand = self.hands[idx]
        if not hand.is_pair():
            return
        if len(self.hands) >= 4:
            # max 4 hands enforced
            return
        card1, card2 = hand.cards
        # remove original hand and insert two single-card hands
        self.hands.pop(idx)
        new1, new2 = Hand(), Hand()
        new1.add_card(card1)
        new2.add_card(card2)
        self.hands.insert(idx, new2)
        self.hands.insert(idx, new1)
        relabel_hands(self.hands)
        self.split_mode = True
        self.current_hand_index = idx
        # remove split_controls
        if self.split_controls:
            try:
                self.split_controls.destroy()
            finally:
                self.split_controls = None
        self.update_counter()
        self.update_info()
        if self.dealer_card:
            self.show_strategy()

    def refuse_split(self):
        # ignore pair logic for this hand and re-evaluate
        self.hands[self.current_hand_index].skip_pair = True
        if self.split_controls:
            try:
                self.split_controls.destroy()
            finally:
                self.split_controls = None
        self.show_strategy()

    def switch_hand(self, idx):
        if not self.split_mode:
            return
        if idx < 0 or idx >= len(self.hands):
            return
        self.current_hand_index = idx
        relabel_hands(self.hands)
        self.instruction_label.configure(text=f"Now playing {self.hands[idx].name}. Click a card to add.")
        self.update_info()
        if self.dealer_card:
            self.show_strategy()

    # ----- UI update helpers -----
    def update_info(self):
        # clear and re-render info_frame contents
        for w in self.info_frame.winfo_children():
            w.destroy()
        for i, h in enumerate(self.hands):
            highlight = (i == self.current_hand_index and self.split_mode)
            # frame with yellow highlight when active
            frame_bg = "#2b2b2b"
            frame = ctk.CTkFrame(self.info_frame, corner_radius=6, fg_color=frame_bg)
            frame.pack(fill="x", pady=6, padx=6)
            dealer_display = f" vs Dealer: {self.dealer_card}" if self.dealer_card else ""
            title = f"{h.name}: {h.total()}{dealer_display}"
            lbl = ctk.CTkLabel(frame, text=title, font=("Arial", 14, "bold"))
            lbl.pack(anchor="w", padx=8, pady=(8, 2))
            if h.cards:
                cards_lbl = ctk.CTkLabel(frame, text=f"Cards: {h.cards}", font=("Arial", 12))
                cards_lbl.pack(anchor="w", padx=12, pady=(0,8))
            if highlight:
                # outline effect: small colored bar
                bar = tk.Frame(frame, bg="yellow", height=4)
                bar.pack(fill="x", side="bottom")

        # Ensure split controls (Play Hand buttons) update if split_mode
        self.update_split_controls()

    def update_split_controls(self):
        # ensure previous split_controls_play exists and remove
        # We'll place Play Hand buttons in a small frame above Clear (if split_mode)
        # Use a separate attribute to avoid colliding with confirm/refuse controls
        # Destroy any dynamic play-hand frame first
        if hasattr(self, "playhand_frame") and self.playhand_frame is not None:
            try:
                self.playhand_frame.destroy()
            except:
                pass
            self.playhand_frame = None

        if not self.split_mode:
            self.counter_label.configure(text="")
            return

        # create play-hand buttons above Clear
        self.playhand_frame = ctk.CTkFrame(self, corner_radius=6)
        self.playhand_frame.pack(pady=6, before=self.clear_btn)
        for i in range(len(self.hands)):
            btn = ctk.CTkButton(self.playhand_frame, text=f"Play Hand {i+1}",
                                command=lambda idx=i: self.switch_hand(idx), width=130)
            btn.pack(side="left", padx=6, pady=6)

        self.update_counter()

    def update_counter(self):
        if self.split_mode and len(self.hands) > 1:
            self.counter_label.configure(text=f"Currently managing {len(self.hands)} hands")
        else:
            self.counter_label.configure(text="")

    # ----- Reset -----
    def reset(self):
        # remove dynamic frames
        if self.split_controls:
            try: self.split_controls.destroy()
            except: pass
            self.split_controls = None
        if hasattr(self, "playhand_frame") and getattr(self, "playhand_frame") is not None:
            try: self.playhand_frame.destroy()
            except: pass
            self.playhand_frame = None

        self.hands = [Hand("Player")]
        self.current_hand_index = 0
        self.dealer_card = None
        self.split_mode = False
        self.stage = 'player'
        self.instruction_label.configure(text="Click player cards, then dealer card")
        self.recommend_label.configure(text="Recommendation will appear here")
        self.counter_label.configure(text="")
        self.update_info()

# -----------------------
# Launcher: CTk root + splash -> main CTk
# -----------------------
def main():
    # create a short-lived CTk root for splash; when done, create the main app CTk
    root = ctk.CTk()
    root.withdraw()  # hide temporary root (we'll create Toplevel splash so no blank root shows)

    def start_main_app():
        # ensure any lingering root windows closed
        try:
            root.destroy()
        except:
            pass
        # create real main app window
        app = BlackjackGUI()
        app.mainloop()

    # Create a splash as a Toplevel so it appears on top and is styled by CTk
    splash = SplashScreen(master=root, on_start=start_main_app, width=900, height=700)
    # start the (hidden) CTk mainloop to show the splash
    try:
        root.mainloop()
    except tk.TclError:
        # Some platforms may destroy root; ignore if main app started
        pass

if __name__ == "__main__":
    main()
