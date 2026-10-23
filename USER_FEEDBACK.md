# Sequence voices repeat in blocks instead of alternating

Hey, I use Collection mode with a preset that has two Edge voices set to "Sequence" (male and
female, for dialogue cards). It used to go female, male, female, male. Since the last update it
comes out in blocks: about 3 cards in the female voice, then 3 in the male voice, then 3 female
again. Every card inside a block uses the voice of the first card in that block, and the cards
themselves are just normal sentences, nothing special in the fields.

If I preview one of those notes on its own before generating, it uses the correct voice for that
card. But after I run the batch, previewing some of those cards plays the wrong
voice too, and re-running the batch on them doesn't fix it. I removed the [sound:] tags and
generated again, same result. Clearing the add-on's cached audio made a single preview sound right
again, but the next batch went straight back to blocks.

It happens on both of my decks. My other preset uses "Random" and it also has this problem now:
instead of a random voice per card I get runs of the same voice, with an occasional card right.
Single-voice presets are fine, and both voices work normally when I preview notes manually. No
errors in the log, the batch just finishes 100%.

Expected: Sequence should cycle one voice per card and Random should pick per card, and what I hear
in preview should match what the batch generated.
