import random


class Suspect:
    def __init__(self, name, alibi, description, relationship_to_victim):
        self.name = name
        self.alibi = alibi
        self.description = description
        self.relationship_to_victim = relationship_to_victim
        self.clues = []

    def update_clue(self, clue):
        self.clues.append(clue)

    def __str__(self):
        return f"{self.name} - Alibi: {self.alibi}, Relationship: {self.relationship_to_victim}"


class KnowledgeBase:
    def __init__(self):
        self.facts = set()
        self.rules = []

    def add_fact(self, fact_type, subject, obj, negated=False):
        self.facts.add(((fact_type, subject, obj), negated))

    def add_rule(self, rule):
        self.rules.append(rule)

    def get_facts(self):
        return self.facts

    def get_rules(self):
        return self.rules

    def get_suspects_names(self):
        return {subject for (fact_type, subject, obj), _ in self.facts}

    def check(self, fact_type, subject, obj, negated=False):
        return ((fact_type, subject, obj), negated) in self.facts


class ProofEngine:
    def __init__(self, kb):
        self.kb = kb

    def forward_chain(self):
        new_inferred = True
        while new_inferred:
            new_inferred = False
            for rule in self.kb.get_rules():
                for suspect in self.kb.get_suspects_names():
                    if self.rule_matches(rule['if'], suspect):
                        then_fact = self.instantiate(rule['then'], suspect)
                        if (then_fact, False) not in self.kb.get_facts():
                            self.kb.add_fact(*then_fact)
                            new_inferred = True
            for suspect in self.kb.get_suspects_names():
                alibi_facts = [(fact, negated) for (fact, negated) in self.kb.get_facts()
                               if fact[0] == "alibi" and fact[1] == suspect]
                for i in range(len(alibi_facts)):
                    for j in range(i + 1, len(alibi_facts)):
                        fact1, neg1 = alibi_facts[i]
                        fact2, neg2 = alibi_facts[j]
                        if fact1 == fact2 and neg1 != neg2:
                            then_fact = ("suspicious", suspect, True)
                            if (then_fact, False) not in self.kb.get_facts():
                                self.kb.add_fact(*then_fact)
                                new_inferred = True

    def rule_matches(self, conditions, suspect):
        for fact_type, subj, obj in conditions:
            real_subj = suspect if subj == "X" else subj
            real_obj = suspect if obj == "X" else obj
            if not self.kb.check(fact_type, real_subj, real_obj, negated=False):
                return False
        return True

    def instantiate(self, fact, suspect):
        fact_type, subj, obj = fact
        subj = suspect if subj == "X" else subj
        obj = suspect if obj == "X" else obj
        return (fact_type, subj, obj)


interrogation_responses = {
    "alibi": [
        ("I was alone at home reading a book.", "home"),
        ("I went for a late-night jog, no one saw me.", "none"),
        ("I was out grabbing dinner with a friend.", "restaurant")
    ],
    "motive": [
        ("They got the promotion I deserved. It’s not fair.", "jealousy"),
        ("I loved them... why would I hurt them?", None),
        ("They ruined my life years ago. Maybe I wanted payback.", "revenge")
    ],
    "relationship": [
        ("We were just acquaintances, barely spoke.", None),
        ("We were close once. Things changed.", None),
        ("They were like family to me.", None)
    ]
}


def interrogate_suspect(suspect, kb):
    facts = kb.get_facts()
    extra_question_available = (("motive", suspect.name, "inheritance"), False) in facts
    print("\n------------------------------")
    print(f"Interrogating {suspect.name}...")
    print("------------------------------")
    print("Choose a question:")
    print("1. Where were you last night?")
    print("2. Why would anyone suspect you?")
    print("3. How well did you know the victim?")
    if extra_question_available:
        print("4. What do you know about the inheritance?")
    choice = input("Enter choice (1-4): ") if extra_question_available else input("Enter choice (1-3): ")

    if choice == "1":
        response, info = random.choice(interrogation_responses["alibi"])
        suspect.alibi = info
        suspect.update_clue(f"Alibi revealed: {response}")
        kb.add_fact("alibi", suspect.name, info)
        print(f"\n{suspect.name}: \"{response}\"")
    elif choice == "2":
        response, motive = random.choice(interrogation_responses["motive"])
        suspect.update_clue(f"Motive discussed: {response}")
        if motive:
            kb.add_fact("motive", suspect.name, motive)
        print(f"\n{suspect.name}: \"{response}\"")
    elif choice == "3":
        response, _ = random.choice(interrogation_responses["relationship"])
        suspect.update_clue(f"Relationship insight: {response}")
        print(f"\n{suspect.name}: \"{response}\"")
    elif choice == "4" and extra_question_available:
        print(
            f"\n{suspect.name}: \"Inheritance? I suppose you found the letter, didn't you? ... Fine. Yes, there was something to gain.\"")
        suspect.update_clue("Mentioned inheritance motive after being confronted with clue.")
        if (("motive", suspect.name, "inheritance"), False) not in kb.get_facts():
            kb.add_fact("motive", suspect.name, "inheritance")
    else:
        print("Invalid choice.")


def explore_scene():
    rooms = {
        "bedroom": [
            ("a torn piece of fabric", ("motive", "Bob Bob", "revenge")),
            ("a smudged footprint", None),
            ("a diary entry", ("motive", "Charlie Doe", "jealousy"))
        ],
        "kitchen": [
            ("a broken glass", None),
            ("a spilled bottle", None),
            ("a strange scent", ("alibi", "Alice Smith", "none"))
        ],
        "study": [
            ("a hidden letter", ("motive", "Alice Smith", "inheritance")),
            ("an encrypted note", None),
            ("a missing book", None)
        ]
    }
    print("\nYou may explore the scene for clues.")
    while True:
        print("\nRooms: 1. Bedroom  2. Kitchen  3. Study  4. Return to Menu")
        room_choice = input("Choose a room to search (1-4): ")
        if room_choice == "4":
            break
        elif room_choice in ["1", "2", "3"]:
            room_keys = list(rooms.keys())
            selected_room = room_keys[int(room_choice) - 1]
            print("\n------------------------------")
            print(f"You enter the {selected_room}...")
            print("------------------------------")
            options = ["closet", "desk", "under the bed"]
            print("Where would you like to look?")
            for i, option in enumerate(options):
                print(f"{i + 1}. {option.capitalize()}")
            spot = input("Enter your choice (1-3): ")
            if spot in ["1", "2", "3"]:
                clue, fact = random.choice(rooms[selected_room])
                print("------------------------------")
                print(f"You found {clue}.")
                print("------------------------------")
                if fact:
                    fact_type, subject, obj = fact
                    if ((fact_type, subject, obj), False) not in kb.get_facts():
                        kb.add_fact(fact_type, subject, obj)
                        print(f"New fact added: {fact_type}({subject}, {obj})")
            else:
                print("Invalid spot.")
        else:
            print("Invalid room choice.")


def reveal_sequence():
    print("==============================")
    print("The room falls silent. Holmes steps forward, eyes sharp as a blade.")
    print("\"Based on all gathered facts... the culprit is...\"")
    print("==============================")
    pe.forward_chain()
    suspects_found = []
    for (fact_type, subject, obj), negated in kb.get_facts():
        if fact_type == "suspicious" and obj is True and not negated:
            suspects_found.append(subject)

    if suspects_found:
        for name in suspects_found:
            print(f"🔍 {name} is guilty.")
            if name == "Alice Smith":
                print(
                    "Congratulations, Watson. You helped solve the case. Another day, another mystery solved. Case closed.")
            else:
                print(
                    "Holmes hesitates, as though something is terribly wrong... but he speaks the name anyway. Then... a cackle is heard.")
                print("The real killer, Alice Smith, walks free...")
                print("Game Over. You lost the case.")
                exit()
        print("❓ Holmes hesitates... \"I need more evidence.\"")


def progress_tracker():
    print("==============================")
    print("Progress Tracker:")
    print("==============================")
    for suspect in suspects:
        print(f"- {suspect.name}:")
        alibi_known = any(
            fact for (fact, neg) in kb.get_facts() if fact == ("alibi", suspect.name, suspect.alibi) and not neg)
        motive_known = any(
            fact for (fact, neg) in kb.get_facts() if fact[0] == "motive" and fact[1] == suspect.name and not neg)
        print(f"  Alibi known: {'Yes' if alibi_known else 'No'}")
        print(f"  Motive known: {'Yes' if motive_known else 'No'}")


def game_loop():
    def print_hints():
        print("\nHints:")
        print("- Try interrogating!")
        print("- Try exploring rooms!")

    print("========================================================")
    print("Rain pelts the mansion as you and Holmes stand outside.")
    print("Holmes smokes his pipe, eyes scanning the house.")
    print("\"Watson, we have a case.\"")
    print("========================================================")
    while True:
        print("\n------------------------------")
        print("Menu:")
        print("1. View suspects")
        print("2. Interrogate a suspect")
        print("3. Explore the crime scene")
        print("4. Ask Holmes to deduce")
        print("5. View known facts")
        print("6. Reveal the culprit")
        print("7. Check progress")
        print("------------------------------")

        choice = input("Enter your choice (1-7): ")

        if choice == "1":
            print("------------------------------------------------------------------")
            for suspect in suspects:
                print(suspect)
            print("------------------------------------------------------------------")
        elif choice == "2":
            print("\n----------------------------------")
            print("Who would you like to interrogate?")
            for i, suspect in enumerate(suspects):
                print(f"{i + 1}. {suspect.name}")
            print("----------------------------------")
            selected = input("Enter the number of the suspect: ")
            if selected.isdigit():
                idx = int(selected) - 1
                if 0 <= idx < len(suspects):
                    interrogate_suspect(suspects[idx], kb)
                else:
                    print("Invalid suspect number.")
            else:
                print("Please enter a valid number.")
        elif choice == "3":
            explore_scene()
        elif choice == "4":
            print("\n----------------------------------")
            print("Holmes is deducing...")
            pe.forward_chain()
            print("Suspicious suspects:")
            print("----------------------------------")
            found = False
            for (fact_type, subject, obj), negated in kb.get_facts():
                if fact_type == "suspicious" and obj is True and not negated:
                    print(f"- {subject}")
                    found = True
            if not found:
                print("None yet.")
                print("----------------------------------")
        elif choice == "5":
            print("\n----------------------------------")
            print("Known facts:")
            for (fact_type, subject, obj), negated in kb.get_facts():
                status = "NOT " if negated else ""
                print(f"{status}{fact_type}({subject}, {obj})")
            print("----------------------------------")
        elif choice == "6":
            reveal_sequence()
        elif choice == "7":
            progress_tracker()

        else:
            print("Invalid choice. Try again.")
            print_hints()


suspect1 = Suspect("Bob Bob", "undisclosed", "Tall, blond, and muscular", "Coworker of victim")
suspect2 = Suspect("Alice Smith", "undisclosed", "Short, brunette, and quiet", "Neighbor of victim")
suspect3 = Suspect("Charlie Doe", "undisclosed", "Average height, black hair, mysterious", "Friend of victim")
suspects = [suspect1, suspect2, suspect3]

kb = KnowledgeBase()
pe = ProofEngine(kb)

rule1 = {
    "if": [("alibi", "X", "none"), ("motive", "X", "jealousy")],
    "then": ("suspicious", "X", True)
}
rule2 = {
    "if": [("alibi", "X", "none"), ("motive", "X", "revenge")],
    "then": ("suspicious", "X", True)
}
rule3 = {
    "if": [("motive", "X", "inheritance")],
    "then": ("suspicious", "X", True)
}
kb.add_rule(rule1)
kb.add_rule(rule2)
kb.add_rule(rule3)

game_loop()
