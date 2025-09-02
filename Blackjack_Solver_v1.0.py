import tkinter as tk

# --- Config ---
DAS = True

# --- Card values ---
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

# --- Action names ---
ACTION_NAMES = {
    'H': 'hit, please click next card',
    'S': 'stand',
    'D': 'double. If not allowed, hit',
    'Ds': 'double. If not allowed, stand',
    'P': 'split',
    'SUR': 'surrender',
    'BUST': 'Bust',
    'BJ': 'Blackjack!'
}

# --- Hand model ---
class Hand:
    def __init__(self, name="Player"):
        self.cards = []
        self.name = name
        self.skip_pair = False

    def add_card(self, card):
        self.cards.append(card)

    def total(self):
        total = sum(CARD_VALUES[c] for c in self.cards if c in CARD_VALUES)
        if 'A' in self.cards and total + 10 <= 21:
            return total + 10
        return total

    def is_soft(self):
        return 'A' in self.cards and self.total() != sum(CARD_VALUES[c] for c in self.cards if c in CARD_VALUES)

    def is_pair(self):
        if self.skip_pair or len(self.cards) != 2:
            return False
        return CARD_VALUES.get(self.cards[0]) == CARD_VALUES.get(self.cards[1])

    def is_bust(self):
        return self.total() > 21

    def is_blackjack(self):
        return len(self.cards) == 2 and 'A' in self.cards and any(c in TEN_RANKS for c in self.cards if c != 'A')

# --- Helpers ---
def normalize_pair_key(cards):
    if len(cards) == 2 and CARD_VALUES.get(cards[0]) == CARD_VALUES.get(cards[1]):
        if cards[0] == 'A':
            return 'A,A'
        if CARD_VALUES[cards[0]] == 10:
            return 'T,T'
        return f"{cards[0]},{cards[1]}"
    return None

def soft_key_from_total(hand):
    if hand.is_soft():
        other = hand.total() - 11
        other = max(2, min(other, 9))
        return f"A,{other}"
    return None

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

# --- GUI ---
class BlackjackGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("EZ Blackjack Solver v1.0")
        self.root.configure(bg="darkgreen")

        self.hands = [Hand("Player")]
        self.current_hand_index = 0
        self.dealer_card = None
        self.split_mode = False
        self.stage = 'player'

        self.label = tk.Label(root, text="Click player cards, then dealer card",
                              font=("Arial", 16, "bold"), fg="white", bg="darkgreen")
        self.label.pack(pady=6)

        self.card_frame = tk.Frame(root, bg="darkgreen")
        self.card_frame.pack()
        for card in RANKS:
            btn = tk.Button(self.card_frame, text=card, width=4,
                            command=lambda c=card: self.select_card(c))
            btn.pack(side=tk.LEFT, padx=1, pady=2)

        self.info_frame = tk.Frame(root, bg="darkgreen")
        self.info_frame.pack(pady=6)

        self.recommend_label = tk.Label(root, text="", font=("Arial", 14, "bold"),
                                        fg="yellow", bg="darkgreen")
        self.recommend_label.pack(pady=6)

        self.split_btn = tk.Button(root, text="Confirm Split", command=self.perform_split)
        self.refuse_btn = tk.Button(root, text="Refuse Split", command=self.refuse_split)

        self.split_controls = None
        self.counter_label = tk.Label(root, text="", font=("Arial", 12, "bold"),
                                      fg="white", bg="darkgreen")
        self.counter_label.pack(pady=4)

        self.clear_btn = tk.Button(root, text="Clear", command=self.reset)
        self.clear_btn.pack(pady=6)

        self.update_info()

    def select_card(self, card):
        hand = self.hands[self.current_hand_index]
        if self.stage == 'player':
            hand.add_card(card)
            if len(hand.cards) == 2:
                self.stage = 'dealer'
                self.label.config(text="Click dealer up-card")
            self.update_info()
        elif self.stage == 'dealer':
            self.dealer_card = card
            self.show_strategy()
        elif self.stage == 'hitting':
            hand.add_card(card)
            self.show_strategy()

    def get_action_code(self, hand, dealer):
        dealer_key = norm_dealer_key(dealer)
        if hand.is_blackjack(): return 'BJ'
        if hand.is_bust(): return 'BUST'
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
        if total >= 18: return 'S'
        return 'H'

    def show_strategy(self):
        self.split_btn.pack_forget()
        self.refuse_btn.pack_forget()
        hand = self.hands[self.current_hand_index]
        dealer = self.dealer_card
        code = self.get_action_code(hand, dealer)

        if code == 'BUST':
            msg = "Bust."
            self.stage = 'action'
        elif code == 'BJ':
            msg = "Blackjack!"
            self.stage = 'action'
        elif code == 'H':
            msg = "Player should hit, please click next card."
            self.stage = 'hitting'
        elif code == 'S':
            msg = "Player should stand."
            self.stage = 'action'
        elif code == 'P':
            msg = "Player should split."
            self.split_btn.pack(pady=2)
            self.refuse_btn.pack(pady=2)
            self.stage = 'action'
        elif code in ('D','Ds'):
            if len(hand.cards) > 2:
                fallback = 'hit' if code == 'D' else 'stand'
                msg = f"Player should {fallback}."
                self.stage = 'hitting' if fallback == 'hit' else 'action'
            else:
                msg = "Player should double. If not allowed, " + ("hit." if code=='D' else "stand.")
                self.stage = 'hitting' if code=='D' else 'action'
        else:
            msg = ACTION_NAMES.get(code, str(code))
            self.stage = 'action'

        self.update_info()
        self.recommend_label.config(text=msg)

    def perform_split(self):
        idx = self.current_hand_index
        hand = self.hands[idx]
        if not hand.is_pair() or len(self.hands) >= 4: return
        card1, card2 = hand.cards
        self.hands.pop(idx)
        new1, new2 = Hand(), Hand()
        new1.add_card(card1); new2.add_card(card2)
        self.hands.insert(idx, new2); self.hands.insert(idx, new1)
        relabel_hands(self.hands)
        self.split_mode, self.current_hand_index = True, idx
        self.split_btn.pack_forget(); self.refuse_btn.pack_forget()
        self.update_counter(); self.update_split_controls(); self.update_info()
        if self.dealer_card: self.show_strategy()

    def refuse_split(self):
        self.hands[self.current_hand_index].skip_pair = True
        self.split_btn.pack_forget(); self.refuse_btn.pack_forget()
        self.show_strategy()

    def switch_hand(self, idx):
        if not self.split_mode or idx<0 or idx>=len(self.hands): return
        self.current_hand_index = idx
        relabel_hands(self.hands)
        self.label.config(text=f"Now playing {self.hands[idx].name}. Click a card to add.")
        self.update_info()
        if self.dealer_card: self.show_strategy()

    def update_info(self):
        for w in self.info_frame.winfo_children(): w.destroy()
        for i, h in enumerate(self.hands):
            highlight = (i==self.current_hand_index and self.split_mode)
            frame = tk.Frame(self.info_frame, bg='darkgreen', highlightthickness=3,
                             highlightbackground='yellow' if highlight else 'darkgreen')
            frame.pack(fill='x', pady=2)
            dealer_display = f" vs. Dealer: {self.dealer_card}" if self.dealer_card else ""
            tk.Label(frame, text=f"{h.name}: {h.total()}{dealer_display}",
                     font=("Arial", 14, "bold"), fg='white', bg='darkgreen').pack(anchor='w', padx=6)
            if h.cards:
                tk.Label(frame, text=f"Cards: {h.cards}", font=("Arial", 11),
                         fg='white', bg='darkgreen').pack(anchor='w', padx=12, pady=(0,6))

    def update_split_controls(self):
        if self.split_controls: self.split_controls.destroy()
        if not self.split_mode: return
        self.split_controls = tk.Frame(self.root, bg="darkgreen")
        self.split_controls.pack(pady=4, before=self.clear_btn)
        for i in range(len(self.hands)):
            tk.Button(self.split_controls, text=f"Play Hand {i+1}",
                      command=lambda idx=i: self.switch_hand(idx)).pack(side=tk.LEFT, padx=4)
        self.update_counter()

    def update_counter(self):
        self.counter_label.config(
            text=f"Currently managing {len(self.hands)} hands" if self.split_mode and len(self.hands)>1 else "")

    def reset(self):
        if self.split_controls: self.split_controls.destroy()
        self.split_btn.pack_forget(); self.refuse_btn.pack_forget()
        self.hands, self.current_hand_index = [Hand("Player")], 0
        self.dealer_card, self.split_mode, self.stage = None, False, 'player'
        self.label.config(text="Click player cards, then dealer card")
        self.recommend_label.config(text=""); self.update_counter(); self.update_info()

# --- Splash Screen ---
class SplashScreen(tk.Frame):
    def __init__(self, master, on_start):
        super().__init__(master, bg="darkgreen")
        self.pack(fill="both", expand=True)

        # --- Scrollable canvas setup ---
        canvas = tk.Canvas(self, bg="darkgreen", highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scroll_frame = tk.Frame(canvas, bg="darkgreen")

        # Link frame and canvas
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0,0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

                # --- Enable mouse wheel / touchpad scrolling ---
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        # Windows + MacOS bindings
        canvas.bind_all("<MouseWheel>", _on_mousewheel)      # Windows / Mac
        canvas.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux scroll up
        canvas.bind_all("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # Linux scroll down


        # --- All splash content goes inside self.scroll_frame ---
        logo_frame = tk.Frame(self.scroll_frame, bg="darkgreen"); logo_frame.pack(pady=(20,5))
        tk.Label(logo_frame, text="♠ ♣", font=("Arial", 20), fg="white", bg="darkgreen").pack()
        tk.Label(logo_frame, text="♦ ♥", font=("Arial", 20), fg="red", bg="darkgreen").pack()

        tk.Label(self.scroll_frame, text="Welcome to EZ Blackjack Solver",
                 font=("Arial", 22, "bold"), fg="yellow", bg="darkgreen").pack(pady=(10,20))

        sections = [
            ("", "This is a simple blackjack assistant that determines the optimal strategy decisions while playing blackjack online."),
            ("How to Use", "First, input both of your cards as prompted, then select the dealer's up-card. "
                           "The program will show your total and suggest the optimal strategy (hit, stand, split, etc). "
                           "In the case of a suggested hit or split, the program will prompt you to enter the values of "
                           "your additional cards before determining any further suggested action.\n\n"
                           "Click \"Clear\" at the end of the hand to start a new hand - the program does not store any data or keep a running total of any kind."),
            ("", "Never take insurance or \"even money\" if offered."),
            ("Strategy Explanation", "The strategy in this program is based entirely on standard S17 blackjack hand charts, which are derived from the known mathematics of multi-deck blackjack. There is no cutting-edge technology being utilized in this program. It's just simplifying the use of hand charts."),
            ("Does this program count cards?", "No. Card counting is largely useless in modern internet casino play with massive shoes that are changed regularly. Blackjack games offered on casino websites without a live dealer (essentially just video games) are based on RNG, which renders card counting entirely useless as the deck size is infinite. This program gives you the best possible strategy without keeping any sort of count.")
        ]

        for header, text in sections:
            if header:
                tk.Label(self.scroll_frame, text=header, font=("Arial", 16, "bold"),
                         fg="white", bg="darkgreen").pack(pady=(12,4))
            tk.Label(self.scroll_frame, text=text, wraplength=640, justify="center",
                     font=("Arial", 12, "bold" if "insurance" in text else "normal"),
                     fg="red" if "insurance" in text else "white", bg="darkgreen").pack(pady=4, padx=20)

        tk.Button(self.scroll_frame, text="Start", font=("Arial", 16, "bold"),
                  command=on_start, bg="yellow", fg="black").pack(pady=20)

        # Default window size
        master.update_idletasks()
        w,h=700,600; x=(master.winfo_screenwidth()//2)-(w//2); y=(master.winfo_screenheight()//2)-(h//2)
        master.geometry(f"{w}x{h}+{x}+{y}")

# --- Launcher ---
def main():
    splash_root = tk.Tk()
    splash_root.title("EZ Blackjack Solver v1.0")
    splash_root.configure(bg="darkgreen")

    def start_app():
        splash_root.destroy()
        root = tk.Tk()
        BlackjackGUI(root)
        root.mainloop()

    SplashScreen(splash_root, on_start=start_app)
    splash_root.mainloop()

if __name__ == '__main__':
    main()
