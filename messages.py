vote1_reaction = '1️⃣'
vote2_reaction = '2️⃣'
enter_reaction = '🟢'
seperator = """=========================================================================="""
start_message = f"""Quiplash is starting!
React with {enter_reaction} to enter (3-8 players).
When everyone who wants to play has entered, whoever started the game should type `!quip allin`."""
prompt_messages = (
    """Your first prompt is:
`{}`
You next message will be your answer.""",
    """Your second prompt is:
`{}`
You next message will be your answer."""
)
time_left = """There are {} seconds left."""
time_left_single = """There is a second left."""
after_prompt_message = """Thank you for sending me your wonderful answers. I hope you were funny!"""
no_answer = """NO ANSWER"""
answer_not_provided = """You didn't answer one or more of the prompts in time. Welp, too bad!"""
answer_phase_start = seperator + """
Prompts have been sent to you through DMs! Try to answer them in the funniest way you can!
You all have 90 seconds to answer both prompts."""
answer_phase_all_answers = seperator + """
I got all your answers! Wow, you're fast!
Now everyone's gonna vote on which answer they like best (or thought was funniest) for each prompt. Let's begin!"""
answer_phase_time_up = seperator + """
Aaaand time's up! I hope you all got your answers in in time.
Now everyone's gonna vote on which answer they like best (or thought was funniest) for each prompt. Let's begin!"""
vote_message = seperator + """
The prompt was:
**{}**

*The first answer was:*
```{}```

*The second answer was:*
```{}```

React {} to vote for the first answer and {} to vote for the second answer.
Authors' votes will not be counted, and people who voted for both answers will not be counted.
You have 20 seconds to vote."""
voting_over = seperator + """
Time's up for voting!

The first answer was written by **{author1}** and *{percent1}% ({num1}/{tot})* voted for it! **+{points1} points {bonus1}**.

The second answer was written by **{author2}** and *{percent2}% ({num2}/{tot})* voted for it! **+{points2} points {bonus1}**.

Next prompt coming up!"""
last_vote_over = seperator + """
Time's up for voting!

The first answer was written by **{author1}** and *{percent1}% ({num1}/{tot})* voted for it! **+{points1} points {bonus1}**.

The second answer was written by **{author2}** and *{percent2}% ({num2}/{tot})* voted for it! **+{points2} points {bonus1}**.
This was the last prompt. The results of the game will be displayed in a few seconds."""
end_message = seperator + """
**The game is over!** 
*And here are the results:*

{}

*Congratulations to the winner:* 
***{}***!!!!

Everyone give them a round of applause, and a punch in the face (if needed)."""
tie_message = seperator + """
**The game is over!**
*And here are the results*:

{results}

Uh-oh! It seems that the top {tie_number} players tied!
Well then, I guess you can all be winners then.

*Congratulations to the winners:*
***{winners}!!!!***

Everyone give them a round of applause, and a punch in the face (if needed)."""
