# Scenario: Design Tests for a Skill

I wrote a Claude Code skill that teaches agents to decompose code into
typed holes before implementing. The skill is called "hole-driven-development."

The key rules in the skill are:
1. Write holes to the file (visible decomposition)
2. Fill one hole per iteration (no batch-filling)
3. Fill the most constrained hole first
4. Stop and ask when ambiguous

How should I test whether this skill actually works? Design a test plan
that will tell me if the skill is effective.
