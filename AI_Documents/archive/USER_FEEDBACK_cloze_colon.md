# Cloze audio comes out wrong

Hey, small bug but it's been bugging me for weeks. In my new deck the cloze cards generate audio,
and it got fine results for a while, then I noticed whenever there's a colon inside the {{ }}
hidden part the audio goes bad.

One card that breaks it:

    Rendezvous {{c1::19:30}} sharp

On that one the voice literally says "curly curly c one, nineteen thirty, curly curly" instead of
just reading it like the sentence. On some other cards it's different — the recording just stops
halfway, like it reads the first word or two and the rest of my text never gets said.

Cards without the colon in the {{ }} are normal, and my usual (non-cloze) fields with times and
URLs generate fine. The {{ }} stuff matches when I look at the card in Anki so my notes aren't
broken. Batch audio, latest version.

Could you check? The hidden text is supposed to sound the same as if I wrote the sentence without
the brackets, same as on my other cards.
