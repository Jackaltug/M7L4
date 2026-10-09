import sounddevice as sd
import scipy.io.wavfile as wav
import speech_recognition as sr
from googletrans import Translator
import random
import time
import os
from datetime import datetime

os.system("")


def colorize(text, code):
    return f"\033[{code}m{text}\033[0m"


def combo_color(combo):
    if combo < 3:
        return "32"
    elif combo < 6:
        return "33"
    elif combo < 9:
        return "35"
    return "91"


def combo_bar(combo, max_width=10):
    filled = min(max_width, max(0, combo))
    return "█" * filled + "▢" * (max_width - filled)


def show_combo_advance(combo):
    for i in range(1, min(combo, 10) + 1):
        bar = combo_bar(i)
        print(colorize(f"Combo bar: {bar} ({i}/10)", combo_color(i)))
        time.sleep(0.07)


def monster_health_by_level(level, is_boss=False, hard_mode=False):
    normal_hp = {"A1": 3, "A2": 4, "B1": 5, "B2": 6}
    boss_hp = {"B2": 12, "C1": 16, "C2": 20}
    if hard_mode:
        hard_normal_hp = {"A1": 5, "A2": 6, "B1": 7, "B2": 8, "C1": 9, "C2": 10}
        hard_boss_hp = {"B2": 20, "C1": 24, "C2": 28}
        return hard_boss_hp.get(level, 20) if is_boss else hard_normal_hp.get(level, 5)
    return boss_hp.get(level, 12) if is_boss else normal_hp.get(level, 3)


def show_battle_summary(battle_name, battle_level, monster_health, player_health, skor, combo):
    print(colorize("\n===== BATTLE SUMMARY =====", "1;36"))
    print(f"Enemy: {battle_name} | Level: {battle_level}")
    print(f"Enemy HP: {monster_health}")
    print(f"Your HP: {player_health}")
    print(f"Total score: {skor}")
    print(f"Combo: x{combo}")
    print(colorize(f"Combo bar: {combo_bar(combo)} ({combo}/10)", combo_color(combo)))
    print(colorize("=====================", "1;36"))


def panel(title):
    print(colorize(f"\n{'=' * 28} {title} {'=' * 28}", "1;36"))


def animated_title(title):
    for char in title:
        print(colorize(char, "1;33"), end="", flush=True)
        time.sleep(0.04)
    print()


def menu_screen(game_mode):
    print(colorize("\n" + "=" * 60, "1;36"))
    animated_title("SPEAK RIGHT")
    print(colorize("1) Start", "1;32"))
    print(colorize(f"2) Gamemodes (Current: {game_mode})", "1;35"))
    print(colorize("3) High Scores", "1;34"))
    print(colorize("4) Exit", "1;31"))
    print(colorize("=" * 60, "1;36"))
    choice = input("Choose an option: ").strip()
    return choice


def choose_game_mode(current_mode):
    while True:
        print(colorize("\nChoose a game mode:", "1;36"))
        print(colorize("1) Normal", "1;32"))
        print(colorize("2) Hard - harder words and tougher enemies", "1;31"))
        print(colorize("3) Speedrun - defeat the boss before time runs out", "1;33"))
        print(colorize("4) Survival - endless monster and boss waves", "1;35"))
        print(colorize("5) Glass Cannon - one HP, but deal extra damage", "1;31"))
        print(colorize("6) Back to main menu", "1;34"))
        print(colorize(f"Current mode: {current_mode}", "1;36"))
        choice = input("Choose a mode: ").strip()
        modes = {
            "1": "Normal",
            "2": "Hard",
            "3": "Speedrun",
            "4": "Survival",
            "5": "Glass Cannon",
        }
        if choice in modes:
            return modes[choice]
        if choice == "6":
            return current_mode
        print(colorize("Invalid choice. Enter a mode from 1 to 5, or 6 to go back.", "1;31"))


def parse_score_line(line):
    line = (line or "").strip()
    if " - " not in line:
        return None

    parts = line.split(" - ")
    if len(parts) == 3:
        ad, tarih, puan_text = parts
        game_mode = "Normal"
    elif len(parts) == 4:
        ad, tarih, game_mode, puan_text = parts
    else:
        return None

    try:
        puan = int(puan_text.strip())
    except ValueError:
        return None

    return {
        "ad": ad.strip(),
        "tarih": tarih.strip(),
        "gamemode": game_mode.strip(),
        "puan": puan,
    }


def load_score_entries(score_file):
    entries = []
    if not os.path.exists(score_file):
        return entries

    with open(score_file, "r", encoding="utf-8") as file:
        for satir in file:
            verili = parse_score_line(satir)
            if verili:
                entries.append(verili)
    return entries


def show_score_board(score_entries, oyuncu_adi=None):
    if not score_entries:
        print(colorize("No scores recorded yet.", "1;33"))
        return

    print(colorize("\nBest records by game mode:", "1;36"))
    best_by_mode = {}
    personal_bests = {}
    for item in score_entries:
        game_mode = item.get("gamemode", "Normal")
        if game_mode not in best_by_mode or item["puan"] > best_by_mode[game_mode]["puan"]:
            best_by_mode[game_mode] = item
        if oyuncu_adi and item["ad"].strip().lower() == oyuncu_adi.strip().lower():
            if game_mode not in personal_bests or item["puan"] > personal_bests[game_mode]:
                personal_bests[game_mode] = item["puan"]

    for game_mode in sorted(best_by_mode):
        record = best_by_mode[game_mode]
        print(colorize(
            f"{game_mode}: {record['puan']} points | {record['ad']} | {record['tarih']}",
            "1;34",
        ))

    if oyuncu_adi:
        print(colorize(f"\n{oyuncu_adi}'s best by game mode:", "1;36"))
        for game_mode in sorted(personal_bests):
            print(colorize(f"{game_mode}: {personal_bests[game_mode]} points", "1;32"))
        if not personal_bests:
            print(colorize("No personal scores yet.", "1;33"))

    print(colorize("\nRecent top scores:", "1;36"))
    skor_listesi = sorted(score_entries, key=lambda item: item["puan"], reverse=True)
    for i, item in enumerate(skor_listesi[:5], start=1):
        print(colorize(
            f"{i}. {item['ad']} | {item.get('gamemode', 'Normal')} | "
            f"{item['tarih']} | {item['puan']} points",
            "1;34",
        ))


sample_rate = 44100
duration = 5
max_errors = 3
score = 0
errors = 0

seviyelere_göre_kelimeler = {
    "A1": ["Cat", "Dog", "Apple", "Milk", "Sun", "Brother", "Clothes", "Country", "Daughter", "Doctor", "Family", "Friend", "Fruit", "Listen", "Monday", "Morning", "Mother", "Night", "People", "School", "Shoes", "Speak", "Student", "Sugar", "Teacher", "Book", "Car", "Chair", "Door", "Egg", "Eye", "Fish", "Food", "Girl", "Hand", "House", "Key", "Leg", "Map", "Name", "Paper", "Phone", "Room", "Street", "Table", "Water", "Week", "White", "Write", "Young"],
    "A2": ["Answer", "Beautiful", "Building", "Business", "Castle", "Chocolate", "Cousin", "Dangerous", "Different", "Island", "Journey", "Language", "Listen", "Machine", "Mountain", "Neighbour", "Police", "Question", "Restaurant", "Stomach", "Through", "Vegetable", "Village", "Weather", "Woman", "Airport", "Borrow", "Careful", "Celebrate", "Comfortable", "Compare", "Decide", "Describe", "Early", "Enough", "Excited", "Forget", "Healthy", "Improve", "Invite", "Perhaps", "Popular", "Prepare", "Receive", "Return", "Sick", "Suddenly", "Ticket", "Useful", "Usually"],
    "B1": ["Adventure", "Apartment", "Arrive", "Challenge", "Conversation", "Delicious", "Difficult", "Education", "Environment", "Experience", "Favorite", "Friendly", "Holiday", "Imagination", "Important", "Knowledge", "Language", "Medicine", "Neighbor", "Opinion", "Practice", "Remember", "Sentence", "Together", "Weather", "Achieve", "Advice", "Although", "Attend", "Avoid", "Behavior", "Believe", "Cause", "Certain", "Choose", "Common", "Create", "Develop", "Discover", "Effect", "Especially", "Explain", "Goal", "However", "Increase", "Instead", "Involve", "Local", "Suggest", "Successful"],
    "B2": ["Architect", "Challenge", "Colleague", "Communicate", "Comparison", "Competition", "Consequence", "Discipline", "Emergency", "Familiarity", "Inspiration", "Intelligence", "Investment", "Laboratory", "Mischievous", "Opportunity", "Organization", "Perspective", "Philosophy", "Recommendation", "Responsibility", "Satisfaction", "Sophisticated", "Uncertainty", "Extraordinary", "Calibration", "Innovation", "Leadership", "Motivation", "Negotiation", "Patience", "Prevention", "Strategic", "Accommodate", "Acquire", "Adequate", "Advocate", "Alter", "Apparent", "Assess", "Assume", "Benefit", "Capacity", "Complex", "Conduct", "Consistent", "Contrast", "Demonstrate", "Derive", "Establish", "Evident", "Ensure", "Implement", "Indicate", "Maintain", "Obtain", "Require", "Significant"],
    "C1": ["Ambiguous", "Circumstances", "Commemorate", "Conscientious", "Discrepancy", "Epidemic", "Exaggerate", "Inconvenient", "Indigenous", "Intermittent", "Meticulously", "Phenomenon", "Predecessor", "Proficiency", "Reconciliation", "Sustainability", "Unprecedented", "Accustomed", "Hypothetical", "Misinterpretation", "Substantive", "Unanimously", "Meditation", "Persuasion", "Resilience", "Appreciation", "Compromise", "Enthusiastic", "Fascination", "Justification", "Modulation", "Nuanced", "Optimization", "Alleviate", "Arbitrary", "Coherent", "Compelling", "Conceive", "Constraint", "Controversy", "Credible", "Crucial", "Deteriorate", "Diminish", "Elaborate", "Empirical", "Evoke", "Inherent", "Integrity", "Invoke", "Plausible", "Precede", "Profound", "Reinforce", "Relevant", "Reluctant", "Rigorous", "Successive"],
    "C2": ["Anecdote", "Cacophony", "Chiaroscuro", "Dysfunctional", "Etymology", "Excommunication", "Holographic", "Inconspicuous", "Intercontinental", "Lexicography", "Misanthrope", "Noncompliance", "Oligarchy", "Pseudonym", "Quintessential", "Rambunctious", "Sycophant", "Thermodynamics", "Unfathomable", "Vicarious", "Xenophobia", "Zeitgeist", "Eucalyptus", "Dissonance", "Ephemeral", "Autobiography", "Contradiction", "Deprivation", "Emancipation", "Gravitation", "Introspection", "Linguistics", "Reverence", "Tenacious", "Abrogate", "Acquiesce", "Apocryphal", "Assiduous", "Bellicose", "Capricious", "Circumspect", "Concomitant", "Deleterious", "Desultory", "Equivocal", "Fastidious", "Inexorable", "Inscrutable", "Intransigent", "Juxtaposition", "Obfuscate", "Perfunctory", "Prosaic", "Recondite", "Recalcitrant", "Sanguine", "Supercilious", "Ubiquitous", "Vacillate"]
}
seviye_sirasi = ["A1", "A2", "B1", "B2", "C1", "C2"]


recognizer = sr.Recognizer()
translator = Translator()
translator = Translator()

def geri_bildirim(skor, toplam):
    oran = skor / toplam if toplam > 0 else 0


    if oran == 1:
        return "🏆 Excellent! You pronounced every word correctly!"
    elif oran >= 0.7:
        return "🎉 Great job! A little more practice and you'll be amazing."
    elif oran >= 0.4:
        return "👍 You're doing well. Keep practicing!"
    else:
        return "💪 Don't give up! You'll improve with practice. Try again!"


score_file = "skorlar.txt"
onceki_skorlar = load_score_entries(score_file)
en_yuksek_skor = max((item["puan"] for item in onceki_skorlar), default=0)
normal_canavar_seviyeleri = ["A1", "A2", "B1", "B2"]
final_boss_seviyeleri = ["B2", "C1", "C2"]
hard_normal_canavar_seviyeleri = ["B1", "B2", "C1", "C2"]
hard_final_boss_seviyeleri = ["C1", "C2"]
normal_canavar_hedefi = 5

game_mode = "Normal"
while True:
    secim = menu_screen(game_mode)

    if secim == "1":
        panel("START GAME")
        oyuncu_adi = input("Enter your name: ").strip()
        if not oyuncu_adi:
            oyuncu_adi = "Player"
        print(colorize(f"Welcome, {oyuncu_adi}! Are you ready?", "1;32"))
        break
    elif secim == "2":
        game_mode = choose_game_mode(game_mode)
    elif secim == "3":
        panel("HIGH SCORES")
        show_score_board(onceki_skorlar)
        input("Press Enter to continue...")
    elif secim == "4":
        print(colorize("Goodbye!", "1;31"))
        raise SystemExit
    else:
        print(colorize("Invalid choice. Enter 1, 2, 3, or 4.", "1;31"))


oyna = "e"
while oyna == "e":
    skor = 0
    errors = 0
    hard_mode = game_mode == "Hard"
    player_health = 1 if game_mode == "Glass Cannon" else 3
    normal_canavar_kazandi = 0
    final_boss_yenildi = False
    final_boss_sayisi = 0
    combo = 0
    speedrun_seconds = 120
    game_started_at = time.monotonic()
    speedrun_expired = False

    panel("MONSTER BATTLE")
    print(colorize(f"Game mode: {game_mode.upper()}", "1;31" if hard_mode else "1;32"))
    print(colorize("⚔️ The battle begins! Defeat the monsters to win.", "1;33"))
    print(colorize(f"💚 Your HP: {player_health} | 🧟 Monster HP varies by level", "1;32"))
    if game_mode == "Speedrun":
        print(colorize(f"⏱️ Defeat the final boss within {speedrun_seconds} seconds!", "1;33"))
    elif game_mode == "Survival":
        print(colorize("♾️ Defeat as many waves and bosses as you can!", "1;35"))
    elif game_mode == "Glass Cannon":
        print(colorize("💥 One mistake can end your run, but your attacks hit harder!", "1;31"))
    print(colorize("Combo bar: " + "▢" * 10, "1;35"))

    while True:
        if game_mode == "Speedrun" and time.monotonic() - game_started_at >= speedrun_seconds:
            speedrun_expired = True
            print(colorize("\n⏱️ Time's up! The final boss escaped.", "1;31"))
            break

        if (
            (game_mode == "Survival" or not final_boss_yenildi)
            and normal_canavar_kazandi < normal_canavar_hedefi
        ):
            normal_levels = hard_normal_canavar_seviyeleri if hard_mode else normal_canavar_seviyeleri
            battle_level = random.choice(normal_levels)
            battle_name = "Normal Monster"
            monster_health = monster_health_by_level(battle_level, hard_mode=hard_mode) + normal_canavar_kazandi
            if game_mode == "Survival":
                monster_health += final_boss_sayisi
            print(f"\n🧟 A {battle_name} appears! Level: {battle_level} | Monster HP: {monster_health}")
        else:
            boss_levels = hard_final_boss_seviyeleri if hard_mode else final_boss_seviyeleri
            battle_level = random.choice(boss_levels)
            battle_name = "Final Boss"
            level_bonus = seviye_sirasi.index(battle_level) * 2
            monster_health = monster_health_by_level(
                battle_level, is_boss=True, hard_mode=hard_mode
            ) + final_boss_sayisi * 4 + level_bonus
            print(f"\n👹 The {battle_name} appears! Level: {battle_level} | Boss HP: {monster_health}")
            final_boss_sayisi += 1

        kelime_list = seviyelere_göre_kelimeler[battle_level][:]
        random.shuffle(kelime_list)
        kelime_list = kelime_list[:5]

        for kelime in kelime_list:
            if monster_health <= 0:
                break
            if game_mode == "Speedrun":
                remaining_time = speedrun_seconds - int(time.monotonic() - game_started_at)
                if remaining_time <= 0:
                    speedrun_expired = True
                    print(colorize("\n⏱️ Time's up! The final boss escaped.", "1;31"))
                    break
                print(colorize(f"⏱️ Time remaining: {remaining_time} seconds", "1;33"))

            print(f"\n📣 Kelime: {kelime}")
            print("🎙 Say the English translation now...")
            recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
            sd.wait()
            wav.write("output.wav", sample_rate, recording)
            print("✅ Recording complete. Recognizing speech...")

            if game_mode == "Speedrun" and time.monotonic() - game_started_at >= speedrun_seconds:
                speedrun_expired = True
                print(colorize("\n⏱️ Time's up! The final boss escaped.", "1;31"))
                break

            try:
                with sr.AudioFile("output.wav") as source:
                    audio = recognizer.record(source)

                tanimlanan = recognizer.recognize_google(audio, language="en").lower()
                print("📝 You said:", tanimlanan)

                ceviri = translator.translate(kelime, src="tr", dest="en").text.lower()
                print("🔤 Translation:", ceviri)

                if ceviri in tanimlanan or tanimlanan in ceviri:
                    combo += 1
                    damage = 1 + (combo // 2) + seviye_sirasi.index(battle_level)
                    if game_mode == "Glass Cannon":
                        damage += 3
                    monster_health -= damage
                    puan_kazanci = damage + 1
                    skor += puan_kazanci

                    if combo >= 1 and combo <= 2:
                        combo_emoji = "✨"
                    elif combo >= 3 and combo <= 5:
                        combo_emoji = "🔥"
                    elif combo >= 6 and combo <= 8:
                        combo_emoji = "⚡"
                    elif combo >= 9:
                        combo_emoji = "💥"
                    else:
                        combo_emoji = "✅"

                    if combo in [1, 3, 6, 9]:
                        print(colorize(f"{combo_emoji} PERFECT! Combo x{combo}", combo_color(combo)))

                    show_combo_advance(combo)
                    print(colorize(f"Combo bar: {combo_bar(combo)} ({combo}/10)", combo_color(combo)))
                    print(f"✅ Correct! Combo x{combo} | Damage: {damage} | +{puan_kazanci} points")
                    print(f"🧟 Monster HP: {monster_health} | Your HP: {player_health}")

                    if monster_health <= 0:
                        if battle_name == "Final Boss":
                            final_boss_yenildi = True
                            skor += 25
                            print("🏆 The final boss is defeated! You won!")
                            show_battle_summary(battle_name, battle_level, 0, player_health, skor, combo)
                            if game_mode == "Survival":
                                normal_canavar_kazandi = 0
                                print("🔥 Another survival wave is coming!")
                            break
                        else:
                            normal_canavar_kazandi += 1
                            skor += 10
                            print(f"🧟 Monster defeated! +10 bonus points. Total score: {skor}")
                            print(f"✅ Monsters defeated: {normal_canavar_kazandi}/{normal_canavar_hedefi}")
                            combo = 0
                            show_battle_summary(battle_name, battle_level, 0, player_health, skor, combo)
                            if normal_canavar_kazandi >= normal_canavar_hedefi:
                                print("🔥 The final boss is coming!")
                            break
                else:
                    combo = 0
                    player_health -= 1
                    errors += 1
                    print(f"❌ Not quite. Expected: {ceviri}. Mistakes: {errors}/{max_errors}")
                    print(f"💚 Your HP: {player_health} | 🧟 Monster HP: {monster_health}")

                    if player_health <= 0:
                        print("\n💀 You lost! You ran out of health.")
                        break

                if errors >= max_errors:
                    print(f"\n💀 Game over. You made {max_errors} mistakes.")
                    player_health = 0
                    break

            except sr.UnknownValueError:
                combo = 0
                player_health -= 1
                errors += 1
                print(f"😕 Speech could not be recognized. Mistakes: {errors}/{max_errors}")
                print(f"💚 Your HP: {player_health} | 🧟 Monster HP: {monster_health}")

                if player_health <= 0:
                    print("\n💀 You lost! You ran out of health.")
                    break

                if errors >= max_errors:
                    print(f"\n💀 Game over. You made {max_errors} mistakes.")
                    break

            except sr.RequestError as e:
                print(f"❗ Speech recognition service error: {e}")
                player_health = 0
                break

            if player_health <= 0:
                break

        if speedrun_expired or player_health <= 0 or (
            final_boss_yenildi and game_mode != "Survival"
        ):
            break

    tarih = datetime.now().strftime("%d.%m.%Y %H:%M")
    skor_satiri = f"{oyuncu_adi} - {tarih} - {game_mode} - {skor}"
    onceki_skorlar.append({
        "ad": oyuncu_adi,
        "tarih": tarih,
        "gamemode": game_mode,
        "puan": skor,
    })

    with open(score_file, "a", encoding="utf-8") as file:
        file.write(skor_satiri + "\n")

    print(f"\n🏁 Game over, {oyuncu_adi}! Your score: {skor}")
    print(colorize("===== FINAL SUMMARY =====", "1;36"))
    print(f"Player: {oyuncu_adi}")
    print(f"Total score: {skor}")
    print(f"Monsters defeated: {normal_canavar_kazandi}/{normal_canavar_hedefi}")
    print(f"Final boss defeated: {'Yes' if final_boss_yenildi else 'No'}")
    if game_mode == "Speedrun" and speedrun_expired:
        print("Speedrun result: Time ran out before the final boss was defeated.")
    print(colorize("==================", "1;36"))
    print(geri_bildirim(skor, max(1, skor)))

    if skor > en_yuksek_skor:
        en_yuksek_skor = skor
        print(f"🏆 New record! High score: {en_yuksek_skor}")
    else:
        print(f"🏆 High score: {en_yuksek_skor}")

    show_score_board(onceki_skorlar, oyuncu_adi)

    print("\nWould you like to play again? (y/n)")
    oyna = input(">>> ").strip().lower()
    while oyna not in ["y", "n"]:
        print("❗ Invalid response. Please enter y or n.")
        print("\nWould you like to play again? (y/n)")
        oyna = input(">>> ").strip().lower()

print(f"\n👋 Thanks for playing, {oyuncu_adi}! See you next time!")
