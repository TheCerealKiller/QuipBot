import discord
import os
from dotenv import load_dotenv
import random
from collections import defaultdict
from timer import Timer
from asyncio import sleep

import messages

from chosen_prompt import ChosenPrompt


class Quiplash(discord.Client):
    def __init__(self):
        super().__init__()

        self.prompt_time = 90
        self.vote_time = 20
        self.points_per_prompt = 1000
        self.win_bonus = 100

        self.game_started = False

        # The User who type !quip start
        self.host = None

        self.answer_phase_going = False
        self.game_channel = None

        self.entry_message_id = 0

        self.players = []
        self.points = defaultdict(int)  # maps player id's to points

        with open('prompts.txt', 'r') as f:
            self.prompts = list(map(str.strip, f.readlines()))

        self.chosen_prompts = []

        # the current prompt being voted on
        self.current_prompt = None
        self.current_prompt_index = 0
        self.current_vote_message_id = 0

        # maps each player id to a list of the prompts they get
        self.player_prompts = defaultdict(list)

        # maps each player id to the number of prompts they have already answered
        self.prompts_answered_count = defaultdict(int)

        self.prompt_timer = Timer(self.prompt_time, self.prompt_tick, 0)
        self.vote_timer = None

    def reset_game(self):
        self.game_started = False

        self.host = None

        self.answer_phase_going = False
        self.game_channel = None

        self.entry_message_id = 0

        self.players = []
        self.points = defaultdict(int)  # maps player id's to points

        self.chosen_prompts = []

        # the current prompt being voted on
        self.current_prompt = None
        self.current_prompt_index = 0
        self.current_vote_message_id = 0

        # maps each player id to a list of the prompts they get
        self.player_prompts = defaultdict(list)

        # maps each player id to the number of prompts they have already answered
        self.prompts_answered_count = defaultdict(int)

        self.prompt_timer = Timer(self.prompt_time, self.prompt_tick, 0)
        self.vote_timer = None

    async def prompt_tick(self, seconds, timer):
        if (not self.answer_phase_going) or (not timer == self.prompt_timer):
            return

        if seconds == 60 or seconds == 30 or seconds == 10 or seconds == 5:
            await self.game_channel.send(messages.time_left.format(seconds))
        elif seconds == 0:
            self.answer_phase_going = False
            await self.game_channel.send(messages.answer_phase_time_up)
            await self.force_answers()

        if self.check_all_prompts() and self.answer_phase_going:
            self.answer_phase_going = False
            await self.game_channel.send(messages.answer_phase_all_answers)
            await self.force_answers()

    async def vote_tick(self, seconds, timer):
        if not timer == self.vote_timer:
            return

        if seconds == 10 or seconds == 5:
            await self.game_channel.send(messages.time_left.format(seconds))
        elif seconds == 0:
            await self.vote_end()

    async def next_vote(self):
        await sleep(5.0)
        if self.current_prompt_index < len(self.chosen_prompts):
            await self.vote_start(self.chosen_prompts[self.current_prompt_index])
        else:
            await self.ending()
        self.current_prompt_index += 1

    async def vote_start(self, cprompt: ChosenPrompt):
        self.current_prompt = cprompt

        answer1 = self.current_prompt.answers[self.current_prompt.players[0].id]
        answer2 = self.current_prompt.answers[self.current_prompt.players[1].id]

        prompt_text = self.current_prompt.prompt

        vote_message = await self.game_channel.send(
            messages.vote_message.format(
                prompt_text, answer1, answer2, messages.vote1_reaction, messages.vote2_reaction
            ))

        await vote_message.add_reaction(messages.vote1_reaction)
        await vote_message.add_reaction(messages.vote2_reaction)

        self.current_vote_message_id = vote_message.id

        self.vote_timer = Timer(self.vote_time, self.vote_tick)
        self.vote_timer.start()

    async def vote_end(self):
        await self.clean_up_votes(self.current_vote_message_id, self.current_prompt.players)

        vote_message = await self.game_channel.fetch_message(
            self.current_vote_message_id)

        author1 = self.current_prompt.players[0]
        author2 = self.current_prompt.players[1]

        # Get the votes (in the form of Reactions)
        reactions1 = discord.utils.get(
            vote_message.reactions, emoji=messages.vote1_reaction)
        reactions2 = discord.utils.get(
            vote_message.reactions, emoji=messages.vote2_reaction)

        count1 = reactions1.count if reactions1 else 0
        count2 = reactions2.count if reactions2 else 0
        count_total = count1 + count2

        if count_total == 0:
            percent1 = 0
            percent2 = 0
        else:
            percent1 = int(100.0 * float(count1) / float(count_total))
            percent2 = 100 - percent1

        # Calculate points for each side
        points1 = int(self.points_per_prompt * (percent1 / 100.0))
        points2 = int(self.points_per_prompt * (percent2 / 100.0))

        # Decide win bonus strings
        bonus1 = f' (+{self.win_bonus} Win Bonus)' if (count1 > count2) else ''
        bonus2 = f' (+{self.win_bonus} Win Bonus)' if (count2 > count1) else ''

        self.points[author1.id] += points1
        self.points[author2.id] += points2

        self.points[author1.id] += self.win_bonus if (count1 > count2) else 0
        self.points[author2.id] += self.win_bonus if (count2 > count1) else 0

        message = ""

        real_prompt_index = self.chosen_prompts.index(self.current_prompt)

        if real_prompt_index < len(self.chosen_prompts) - 1:
            # Not the last prompt.
            message = messages.voting_over
        else:
            # It's the last prompt, change the message that will be displayed.
            message = messages.last_vote_over

        await self.game_channel.send(
            message.format(
                author1=author1.name,
                author2=author2.name,
                percent1=percent1,
                percent2=percent2,
                num1=count1,
                num2=count2,
                tot=count_total,
                points1=points1,
                points2=points2,
                bonus1=bonus1,
                bonus2=bonus2
            )
        )

        self.vote_timer = None

        await sleep(5.0)
        await self.next_vote()

    def check_all_prompts(self):

        for prompt in self.chosen_prompts:
            if not len(prompt.answers) == len(prompt.players):
                return False

        return True

    async def clean_up_votes(self, vote_message_id, authors):
        vote_message = await self.game_channel.fetch_message(vote_message_id)

        # remove bot's vote
        await vote_message.remove_reaction(messages.vote1_reaction, self.user)
        await vote_message.remove_reaction(messages.vote2_reaction, self.user)

        reactions1 = discord.utils.get(
            vote_message.reactions, emoji=messages.vote1_reaction)
        reactions2 = discord.utils.get(
            vote_message.reactions, emoji=messages.vote2_reaction)

        voters1 = await reactions1.users().flatten()
        voters2 = await reactions2.users().flatten()

        # remove authors' votes, if needed
        for a in authors:
            if len(self.players) < 3:
                break
            if a in voters1:
                await vote_message.remove_reaction(messages.vote1_reaction, a)
            if a in voters2:
                await vote_message.remove_reaction(messages.vote2_reaction, a)

        cheaters = []

        for u in voters1:
            if u in voters2:
                cheaters.append(u)

        for c in cheaters:
            await vote_message.remove_reaction(messages.vote1_reaction, c)
            await vote_message.remove_reaction(messages.vote2_reaction, c)

    async def vote_phase(self):
        self.current_prompt_index = 0
        await self.next_vote()

    async def ending(self):
        rankings = sorted(self.players, key=lambda p: int(
            self.points[p.id]), reverse=True)
        player_names = list(map(lambda p: p.name, rankings))
        points_sorted = list(
            map(lambda player: self.points[player.id], rankings))

        result_string = ''
        for player, points in zip(rankings, points_sorted):
            result_string += f'{player.name} - {points}\n'
        result_string = result_string[:-1]

        if points_sorted.count(points_sorted[0]) > 1:
            tie_number = points_sorted.count(points_sorted[0])

            winners = ', '.join(
                player_names[: tie_number - 1]) + ', and ' + player_names[tie_number - 1]

            await self.game_channel.send(messages.tie_message.format(
                results=result_string,
                tie_number=tie_number,
                winners=winners
            ))
        else:
            winner = max(self.players, key=lambda p: int(self.points[p.id]))

            await self.game_channel.send(messages.end_message.format(
                result_string,
                winner.name
            ))

        self.game_started = False

    async def force_answers(self):
        sent_players = []
        for prompt in self.chosen_prompts:
            for player in prompt.players:
                if not player.id in prompt.answers:
                    self.record_answer(
                        prompt.prompt, player.id, messages.no_answer)
                    if player not in sent_players:
                        await player.send(messages.answer_not_provided)
                        sent_players.append(player)

        await self.end_answer_phase()

    async def start_entry(self, channel, host):
        self.reset_game()

        self.game_started = True
        self.host = host

        self.game_channel = channel
        entry_message = await self.game_channel.send(messages.start_message)
        await entry_message.add_reaction(messages.enter_reaction)
        self.entry_message_id = entry_message.id

    async def start_game(self):
        entry_message = await self.game_channel.fetch_message(self.entry_message_id)
        await entry_message.remove_reaction(messages.enter_reaction, self.user)
        entry_message = await self.game_channel.fetch_message(self.entry_message_id)
        entry = discord.utils.get(
            entry_message.reactions, emoji=messages.enter_reaction)

        self.players = (await entry.users().flatten())[:8]

        for p in self.players:
            self.points[p] = 0

        self.choose_prompts()

        await self.message_all_players()
        self.answer_phase_going = True
        await self.game_channel.send(messages.answer_phase_start)
        self.answer_phase_going = True

    def choose_prompts(self):
        possible_indexes = list(range(len(self.prompts)))
        player_list_shuffled = random.sample(self.players, k=len(self.players))
        prompt_num = len(self.players)

        # choosing prompts, each taking a random prompt and pairing two players from the shuffled list
        for i in range(prompt_num):
            first = i
            second = i + 1

            if second == prompt_num:
                second = 0

            prompt_index = random.choice(possible_indexes)
            possible_indexes.remove(prompt_index)

            self.chosen_prompts.append(
                ChosenPrompt(
                    self.prompts[prompt_index],
                    [player_list_shuffled[first],
                     player_list_shuffled[second]]
                )
            )

        for p in self.chosen_prompts:
            self.player_prompts[p.players[0].id].append(p.prompt)
            self.player_prompts[p.players[1].id].append(p.prompt)

    async def message_all_players(self):
        for p in self.players:
            await self.send_prompt(p)
        self.prompt_timer.start()

    async def send_prompt(self, player):
        if self.prompts_answered_count[player.id] < len(self.player_prompts[player.id]):
            prompt = self.player_prompts[player.id][self.prompts_answered_count[player.id]]
            message = messages.prompt_messages[self.prompts_answered_count[player.id]].format(
                prompt)
            await player.send(message)
        else:
            await player.send(messages.after_prompt_message)

    async def end_answer_phase(self):
        await sleep(5.0)
        await self.vote_phase()

    async def on_ready(self):
        print(f'{self.user} has connected to Discord.')

    def record_answer(self, prompt: str, player_id, answer):
        chosen_prompt = discord.utils.get(self.chosen_prompts, prompt=prompt)
        chosen_prompt.answers[player_id] = answer

    async def dm_message(self, message):
        if self.answer_phase_going:
            player_id = message.author.id

            if self.prompts_answered_count[player_id] < len(self.player_prompts[player_id]):
                prompt = self.player_prompts[player_id][self.prompts_answered_count[player_id]]
                self.record_answer(prompt, player_id, message.content)
                self.prompts_answered_count[player_id] += 1
                await self.send_prompt(message.author)

    async def on_message(self, message: discord.Message):
        if isinstance(message.channel, discord.TextChannel):
            if not message.content.startswith('!quip'):
                return

            args = message.content.split(' ')[1:]

            if args[0] == 'start':
                if not self.game_started:
                    await self.start_entry(message.channel, message.author)
            elif args[0] == 'allin' and message.author == self.host:
                await self.start_game()

        else:
            await self.dm_message(message)


def main():

    bot = Quiplash()

    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')

    bot.run(TOKEN)


if __name__ == '__main__':
    main()
