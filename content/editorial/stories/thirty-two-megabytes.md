<!-- story: {"id":"thirty-two-megabytes","title":"Thirty-two megabytes for the bus ride","category":"tech","summary":"The 1998 Rio PMP300 traded the spinning disc for flash memory. Its small capacity made the playlist a decision you finished at the PC.","art":"rio-pmp300","sourceIds":["connected-rio","connected-rio-manual","connected-mp3","connected-mp3-paper"],"objectIds":["rio-pmp300","discman","cdr-spindle"],"topics":["mp3","rio","digital audio","portable","playlist"],"relatedStoryIds":["from-mixtape-to-file","minidisc-small-door"],"publishedAt":"2026-11-06","updatedAt":"2026-11-06"} -->

## The music travels. Most of the library stays home.

Thirty-two megabytes is an excellent way to make a person choose. Diamond Multimedia’s standard Rio PMP300, introduced in 1998, put that much flash storage into a portable MP3 player. There was no album-sized disc to swap when you grew tired of your selection. The next transfer meant returning to the computer.

The reward was a player without a spinning audio disc or a tape transport. The compromise was a library small enough to think about track by track. This was not the first MP3 player ever made, and it was not a pocket window onto an unlimited streaming service. It carried the files you had deliberately put there.

## Start at the back of the PC

The original Rio instructions show a parallel-port adapter, a data cable and Rio Manager software. A printer pass-through is part of that arrangement. It is a very particular desk scene: the player depends on the computer, and connecting it involves hardware that a later USB player does not need.

The manual’s connection diagram gives the printer and the music player places in the same setup. That detail makes the Rio feel less like a separate music library and more like a portable extension of the PC. Later PMP300 editions offered different capacities; the standard 32 MB version is the one budgeted below.

The front buttons let the listener move through the choice already made. The more substantial editing happens before departure: add a track, remove another, transfer again. Compare the [Rio object](/archive/objects/rio-pmp300/) with a [Discman](/archive/objects/discman/). Both are portable listening devices, but the thing you replace when the music runs out is different.

## How much music fits?

Bitrate turns a storage number into a duration. In the worked example below, a four-minute track encoded at a constant **128 kbps** needs **3.84 decimal MB of audio payload**. A nominal 32 MB therefore holds eight whole tracks of that length, before allowing for headers or device overhead.

{{tool:mp3-budget}}

The calculation is simple: seconds × kilobits per second ÷ 8 gives kilobytes; divide by 1,000 for decimal megabytes. The tool uses decimal units throughout. Real files and players consume space beyond that payload, so treat its result as an upper bound rather than a transfer guarantee.

At 64 kbps, the theoretical running time doubles. That is also a different audio-quality choice. Perceptual coding reduces the data needed to represent sound by exploiting how hearing works; a lower number does not promise transparent results for every voice, cymbal or dense arrangement. Listen to the actual encode before committing a favorite recording to the smaller file.

## A file is not an audio CD track

Four minutes of CD-format stereo PCM contains 42.336 MB of audio payload: 44,100 samples per second × 16 bits × two channels × 240 seconds ÷ eight. The 128 kbps MP3 example is much smaller because its representation is different. These figures compare audio data, not the complete physical structure of a CD.

That distinction matters when making a disc, too. Copying MP3 files onto a CD-R does not turn them into an ordinary audio CD for every older player. The playback device has to understand the format you provide.

The [mixtape guide](/stories/from-mixtape-to-file/) asks what the opening song should do. The Rio adds a second question: how much of the next song can you afford to bring? The medium changes, and a good sequence still earns its place.
